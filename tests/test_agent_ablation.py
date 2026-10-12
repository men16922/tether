from decimal import Decimal
from types import SimpleNamespace

import pytest

from tether.eval.agent_ablation import CreditLimit
from tether.studio.pipeline import analyze
from tether.studio.session import load
from tether.agent.tool_agent import from_params
from tether.studio.fit import fit_base
from tether.paths import REPO


def test_credit_limit_refuses_before_any_paid_call(tmp_path):
    class Fake:
        usage=SimpleNamespace();max_tokens=2048
        called=False
        def __init__(self):
            self.client=SimpleNamespace(with_options=lambda **k:self.client,models=SimpleNamespace(list=lambda **k:SimpleNamespace(data=[SimpleNamespace(id='m',model_dump=lambda:{'pricing':{'prompt':'0.001','completion':'0.001'}})])))
        def model_for(self,role):return 'm'
        def chat(self,*args):self.called=True;raise AssertionError('should not reach network')
    inner=Fake(); limited=CreditLimit(inner,0.1,tmp_path/'ledger.json')
    with pytest.raises(RuntimeError,match='refused before inference'):
        limited.chat('diagnose',[{'role':'user','content':'test'}],[])
    assert not inner.called and limited.spent==Decimal('0')
    # A fresh process must not reset already spent credit.
    limited.spent=Decimal('0.099');limited.save()
    resumed=CreditLimit(inner,0.1,tmp_path/'ledger.json')
    assert resumed.spent==Decimal('0.099')
    with pytest.raises(RuntimeError):resumed.chat('diagnose',[{'role':'user','content':'test'}],[])


def test_ablation_shares_agent_output_without_mutation_or_new_calls():
    s=load((REPO/'tether/studio/samples/lab-bench.csv').read_text())
    agent={'structure':['mu_eff'],'committed':from_params(fit_base(s)), 'model_name':'stored',
           'error':'','requested_commands':[],'trace':[]}
    alone=analyze(s,n_boot=0,agent_result=agent,cross_check=False)
    checked=analyze(s,n_boot=0,agent_result=agent,cross_check=True)
    assert 'cross_check' not in agent and 'cross_check' not in alone.agent
    assert checked.agent['cross_check']['adopted']=='search'
    assert checked.calibration.residuals['stop_residual_rms_m'] < alone.calibration.residuals['stop_residual_rms_m']


def test_missing_fixtures_are_excluded_from_paired_metrics():
    from tether.eval.agent_ablation import summarize
    complete={'agent_status':'evaluated','conditions':{k:{'stop_median_cm':2.0,'stop_p90_cm':3.0,'structure_correct':True}
               for k in ('offline','agent','agent_cross_check')}}
    missing={'agent_status':'not run: fixture missing','conditions':{'offline':{'stop_median_cm':999.0}}}
    r=summarize([complete,missing])
    assert r['paired_cases']==1 and r['unavailable_cases']==1
    assert r['methods']['offline']['mean_of_case_medians_cm']==2.0
    assert r['agent_failure_rate']==0 and r['paired_delta_cm']['mean']==0


def test_live_latency_excludes_replay_and_incomplete_original_timing():
    from tether.eval.agent_ablation import summarize
    conditions={k:{'stop_median_cm':2.0,'stop_p90_cm':3.0,'structure_correct':True}
                for k in ('offline','agent','agent_cross_check')}
    rows=[{'agent_status':'evaluated','conditions':conditions,**timing} for timing in (
        {'original_live_agent_seconds':20.0,'live_latency_scope':'complete case'},
        {'original_live_agent_seconds':None,'live_continuation_seconds':1000.0,'live_latency_scope':'continuation only'},
        {'original_live_agent_seconds':0.001,'live_latency_scope':'unavailable'},
    )]
    r=summarize(rows)['original_live_latency']
    assert r['complete_cases']==1 and r['unavailable_cases']==2
    assert r['median_seconds']==20.0 and r['p90_seconds']==20.0
