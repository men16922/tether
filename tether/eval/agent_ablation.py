"""Three-condition holdout evaluation. Offline by default; --live spends Token Factory credit explicitly.

Fixtures are recorded on TRAINING pushes only and shared by the two agent conditions. Existing full-session
Studio traces cannot be used: they saw held-out outcomes. Missing fixtures are reported, never faked.
"""
from __future__ import annotations

import argparse
import json
import random
import time
import hashlib
import math
from decimal import Decimal
from dataclasses import asdict, replace
from pathlib import Path

from tether.paths import REPO
from tether.studio.session import Session
from tether.studio.pipeline import analyze, run_agent
from tether.studio.fit import predict_stop

OUT=REPO/'runs/proof/agent_ablation.json'
FIXTURES=REPO/'runs/ablation-fixtures'


class CreditLimit:
    """Reserve a conservative byte-count token bound before every call; never retry paid requests."""
    def __init__(self, inner, maximum, ledger):
        if not math.isfinite(maximum) or maximum<=0:
            raise ValueError('finite positive credit limit required')
        self.inner=inner
        self.inner.client=inner.client.with_options(max_retries=0)
        self.usage=inner.usage
        self.maximum=Decimal(str(maximum)); self.spent=Decimal('0'); self.uncertain=Decimal('0')
        self.ledger=ledger; self.calls=[]
        self.model=inner.model_for('diagnose')
        model=next(m for m in inner.client.models.list(extra_query={'verbose':'true'}).data if m.id==self.model)
        self.pricing=model.model_dump()['pricing']
        self.input=Decimal(self.pricing['prompt']); self.output=Decimal(self.pricing['completion'])
        self.request=Decimal(self.pricing.get('request') or '0')
        if self.input<0 or self.output<0 or self.request<0:
            raise ValueError('invalid pricing')
        if self.ledger.exists():
            previous=json.loads(self.ledger.read_text())
            if previous['model']!=self.model:
                raise ValueError('cannot mix models in one approved credit ledger')
            self.spent=Decimal(previous['spent_usd'])
            self.uncertain=Decimal(previous['uncertain_reserved_usd'])
            self.calls=previous['calls']
        self.save()

    def save(self):
        self.ledger.parent.mkdir(parents=True,exist_ok=True)
        self.ledger.write_text(json.dumps({'model':self.model,'pricing':self.pricing,'limit_usd':str(self.maximum),
          'spent_usd':str(self.spent),'uncertain_reserved_usd':str(self.uncertain),'calls':self.calls},indent=2)+'\n')

    def chat(self,role,messages,tools,tool_choice=None):
        size=len(json.dumps({'messages':messages,'tools':tools},ensure_ascii=False).encode())+1024+256*len(messages)
        reserve=Decimal(size)*self.input+Decimal(self.inner.max_tokens)*self.output+self.request
        if self.spent+self.uncertain+reserve>self.maximum:
            raise RuntimeError(f'approved ${self.maximum} credit limit reached; next call refused before inference')
        self.uncertain+=reserve; self.save()
        started=time.perf_counter()
        turn=self.inner.chat(role,messages,tools,tool_choice)
        seconds=time.perf_counter()-started
        if turn.prompt_tokens <= 0 or turn.completion_tokens <= 0:
            # Keep the reservation when usage is missing; never silently turn unknown billing into zero.
            raise RuntimeError('usage missing; conservative reservation retained; no automatic retry')
        actual=Decimal(turn.prompt_tokens)*self.input+Decimal(turn.completion_tokens)*self.output+self.request
        self.uncertain-=reserve; self.spent+=actual
        self.calls.append({'prompt_tokens':turn.prompt_tokens,'completion_tokens':turn.completion_tokens,'cost_usd':str(actual),
                           'response_seconds':seconds})
        self.save()
        return turn


class ResumeLLM:
    """Replay a partial fixture, then continue the SAME conversation live; only new responses are appended."""
    def __init__(self, budget, fixture):
        from tether.agent.llm import RecordedLLM, RecordingLLM, Usage
        self.replay=RecordedLLM.from_file(fixture)
        self.record=RecordingLLM(budget,fixture)
        self.usage=Usage()

    def chat(self,role,messages,tools,tool_choice=None):
        if self.replay._queues.get('chat:'+role):
            turn=self.replay.chat(role,messages,tools,tool_choice)
        else:
            turn=self.record.chat(role,messages,tools,tool_choice)
        self.usage.add(turn)
        return turn


def cases():
    from tether.eval.cross_engine import first_day_log,hidden_world
    from tether.sim.mujoco_push import MujocoPushEnv
    from tether.sim.params import ParamSet
    rng=random.Random(17)
    for i in range(24):
        h=hidden_world(rng)
        s=first_day_log(MujocoPushEnv(),ParamSet.nominal().with_(**h),100+i)
        yield f'mujoco-{i:02d}','MuJoCo',s,['mu_eff','actuator_gain','camera_dx','camera_pitch_deg','patch_y0','patch_mu']
    for path in sorted((REPO/'runs/studio-demo').glob('*.json')):
        raw=json.loads(path.read_text())
        result=raw['stages'][-1]['result']
        s=Session.from_json(result['session'])
        truth=['mu_eff']
        if s.has_commands and s.has_tracks:truth.append('actuator_gain')
        if s.has_targets:truth+=['camera_dx','camera_pitch_deg']
        model=(raw.get('truth') or {}).get('model',{})
        if model.get('patch_y0') is not None:truth+=['patch_y0','patch_mu']
        if s.has_targets and model.get('lens_k',0):truth.append('lens_k')
        yield f'newton-{path.stem}','Newton synthetic',s,truth if model else None
    real=json.loads((REPO/'runs/proof/real_benchmark.json').read_text())
    for name,raw in real['sessions'].items():
        yield 'real-'+name.replace(' ','-'),'EV-RealPhys log',Session.from_json(raw['log']),None


def score(session,cal,truth_structure=None):
    errors=[]
    for p in session.pushes:
        # A robot input is its held-out command, with the gain learned from training only.
        v=p.launch_speed if p.command is None else p.command*cal.model['actuator_gain']
        pred=predict_stop(cal,v,p.start)['median_m']
        errors.append(abs(pred-p.stop)*100)
    import numpy as np
    return {'evaluation_pushes':len(errors),'stop_median_cm':float(np.median(errors)) if errors else None,
            'stop_p90_cm':float(np.percentile(errors,90)) if errors else None,
            'structure_correct':None if truth_structure is None else set(cal.structure)==set(truth_structure)}


def summarize(rows):
    """Paired comparison uses identical complete cases; missing/budget-limited cases never become zero errors."""
    import numpy as np
    paired=[r for r in rows if r['agent_status']=='evaluated']
    attempted=[r for r in rows if r['agent_status'] in ('evaluated','failed')]
    result={'paired_cases':len(paired),'unavailable_cases':len(rows)-len(attempted),
            'agent_failed_cases':sum(r['agent_status']=='failed' for r in attempted),
            'agent_failure_rate':sum(r['agent_status']=='failed' for r in attempted)/len(attempted) if attempted else None,
            'methods':{},'note':'case-balanced errors on the complete subset; selected pilot cases, not population inference'}
    for method in ('offline','agent','agent_cross_check'):
        cs=[r['conditions'][method] for r in paired]
        structure=[c['structure_correct'] for c in cs if c.get('structure_correct') is not None]
        result['methods'][method]={'cases':len(cs),'mean_of_case_medians_cm':float(np.mean([c['stop_median_cm'] for c in cs])) if cs else None,
           'mean_of_case_p90_cm':float(np.mean([c['stop_p90_cm'] for c in cs])) if cs else None,
           'structure_evaluable_cases':len(structure),'structure_accuracy':sum(structure)/len(structure) if structure else None}
    deltas=[r['conditions']['agent_cross_check']['stop_median_cm']-r['conditions']['offline']['stop_median_cm'] for r in paired]
    rng=random.Random(0)
    draws=[sum(rng.choice(deltas) for _ in deltas)/len(deltas) for _ in range(1000)] if deltas else []
    result['paired_delta_cm']={'mean':float(np.mean(deltas)) if deltas else None,
                              'case_bootstrap_95':list(map(float,np.percentile(draws,[2.5,97.5]))) if draws else None}
    return result


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--live',action='store_true',help='explicitly authorised Token Factory run, records new training-only fixtures')
    ap.add_argument('--fixtures',type=Path,default=FIXTURES)
    ap.add_argument('--out',type=Path,default=OUT)
    ap.add_argument('--limit',type=int)
    ap.add_argument('--budget-usd',type=float,default=0.1)
    a=ap.parse_args(argv)
    from tether.agent.llm import RecordedLLM,RecordingLLM,make_llm
    rows=[]
    budget=CreditLimit(make_llm('tokenfactory'),a.budget_usd,a.fixtures/'credit_ledger.json') if a.live else None
    for index,(name,origin,s,truth_structure) in enumerate(cases()):
        if a.limit is not None and index>=a.limit:break
        n=max(1,len(s.pushes)//5)
        train,test=replace(s,pushes=s.pushes[:-n]),replace(s,pushes=s.pushes[-n:])
        row={'case':name,'origin':origin,'training_pushes':len(train.pushes),'evaluation_pushes':n,'conditions':{}}
        t=time.perf_counter(); offline=analyze(train,n_boot=0)
        row['conditions']['offline']={**score(test,offline.calibration,truth_structure),'seconds':time.perf_counter()-t,'calls':0}
        fixture=a.fixtures/(name+'.json')
        digest=hashlib.sha256(json.dumps(train.to_json(),sort_keys=True).encode()).hexdigest()
        meta=fixture.with_suffix('.meta.json')
        if fixture.exists() and (not meta.exists() or json.loads(meta.read_text()).get('training_sha256')!=digest):
            raise ValueError(f'fixture does not match training-only input: {fixture.name}')
        complete=fixture.exists() and json.loads(meta.read_text()).get('status')=='evaluated'
        if not complete and not a.live:
            row['agent_status']='not run: training-only fixture missing; live run awaits approval'
            if fixture.exists():row['agent_status']='not evaluable: partial fixture at approved credit limit'
        else:
            llm=(RecordedLLM.from_file(fixture) if complete else ResumeLLM(budget,fixture) if fixture.exists()
                 else RecordingLLM(budget,fixture))
            before_calls=len(budget.calls) if budget else 0
            before_usage=asdict(llm.usage)
            t=time.perf_counter(); agent=run_agent(train,llm); elapsed=time.perf_counter()-t
            row['agent_status']='failed' if agent.get('error') or not agent.get('structure') else 'evaluated'
            row['agent_error']=agent.get('error') or ''
            if 'credit limit' in row['agent_error'] or 'usage missing' in row['agent_error']:
                row['agent_status']='not evaluable: approved credit/usage limit'
            after_usage=asdict(llm.usage)
            row['usage']={k:after_usage[k]-before_usage[k] for k in ('calls','prompt_tokens','completion_tokens')}
            original=json.loads(meta.read_text()) if meta.exists() else {}
            original.update(training_sha256=digest,status=row['agent_status'])
            if budget and len(budget.calls)>before_calls: original['live_agent_seconds']=elapsed
            meta.write_text(json.dumps(original,indent=2)+'\n')
            row['original_live_agent_seconds']=original.get('live_agent_seconds')
            # No money estimate without verified model prices. Report exact tokens and calls for pricing later.
            row['cost_usd']=float(sum(Decimal(c['cost_usd']) for c in budget.calls[before_calls:])) if budget else None
            row['cost_note']='actual new calls only; replay cost is zero; per-token prices in credit_ledger.json' if budget else 'offline replay; no live-cost claim'
            for cond,cross in [('agent',False),('agent_cross_check',True)]:
                if row['agent_status']!='evaluated':
                    row['conditions'][cond]={'failure':row['agent_status']=='failed','stop_median_cm':None,'stop_p90_cm':None,
                                             'structure_correct':None,'reason':row['agent_error']}
                    continue
                r=analyze(train,n_boot=0,agent_result=agent,cross_check=cross)
                row['conditions'][cond]={**score(test,r.calibration,truth_structure),'agent_seconds':elapsed,
                                         'failure':row['agent_status']=='failed','cross_check':(r.agent or {}).get('cross_check')}
            row['overruled']=(row['conditions']['agent_cross_check'].get('cross_check') or {}).get('adopted','agent')!='agent'
        rows.append(row)
        print(name,row['agent_status'],flush=True)
    out={'protocol':'last 20% held out before ANY agent call; one shared agent call; same fitter guards in all conditions',
         'precommitted_interpretation':'No accuracy advantage if agent+cross-check is indistinguishable from offline within uncertainty; guidance and experiment choice only.',
         'live':a.live,'cases':len(rows),'missing_fixtures':sum(r['agent_status']!='evaluated' for r in rows),
         'measured_overrules':sum(r.get('overruled',False) for r in rows),'rows':rows,
         'users':'not tested with users','scope':'24 in-menu MuJoCo + 6 Newton samples + 5 real log objects; queued probes not executed'}
    out['cost_basis']='reported tokens multiplied by contemporaneous model API prices, not an invoice/balance verification'
    out['summary']=summarize(rows)
    out['live_spent_usd']=float(budget.spent) if budget else 0.0
    out['live_reserved_unknown_usd']=float(budget.uncertain) if budget else 0.0
    ledger=a.fixtures/'credit_ledger.json'
    if ledger.exists():out['recorded_live_cost_usd']=float(Decimal(json.loads(ledger.read_text())['spent_usd']))
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n')
    return out


if __name__=='__main__': main()
