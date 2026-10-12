"""Coverage-vs-count evidence for product policy, not a statistical guarantee of sufficient samples."""
import json
from dataclasses import replace

from tether.paths import REPO
from tether.studio.fit import calibrate
from tether.studio.session import Session


def main():
    from tether.eval.cross_engine import first_day_log, hidden_world
    from tether.sim.mujoco_push import MujocoPushEnv
    from tether.sim.params import ParamSet
    import random

    real=json.loads((REPO/'runs/proof/real_benchmark.json').read_text())
    cases=[]
    for obj in real['objects']:
        for way,raw in real['sessions'][obj['object']].items():
            cases.append(('EV-RealPhys',f"{obj['object']}/{way}",Session.from_json(raw),obj['mu_tilt_test']))
    rng=random.Random(17)
    for i in range(24):
        h=hidden_world(rng)
        p=ParamSet.nominal().with_(**h)
        s=first_day_log(MujocoPushEnv(),p,100+i)
        cases.append(('MuJoCo',str(i),s,h['object_mu']))
    rows=[]
    for origin,name,s,truth in cases:
        for n in (1,2,4,6,8):
            if len(s.pushes)<n:
                continue
            # Evenly spaced in original acquisition order; fixed selection before evaluating coverage.
            indices=[round(i*(len(s.pushes)-1)/max(1,n-1)) for i in range(n)]
            train=replace(s,pushes=[s.pushes[i] for i in indices])
            cal=calibrate(train,n_boot=30)
            iv=cal.intervals.get('mu_eff')
            rows.append({'origin':origin,'case':name,'pushes':n,'mu':cal.model['mu_eff'],'truth':truth,
                         'interval':iv,'covered':False if iv is None else iv[0]<=truth<=iv[1]})
        print(origin,name,flush=True)
    summary={}
    for origin in ('EV-RealPhys','MuJoCo'):
        summary[origin]={}
        for n in (1,2,4,6,8):
            rs=[r for r in rows if r['origin']==origin and r['pushes']==n]
            summary[origin][str(n)]={'cases':len(rs),'covered':sum(r['covered'] for r in rs),'coverage':sum(r['covered'] for r in rs)/len(rs) if rs else None}
    out={'design':'fixed evenly spaced subsamples; 30 bootstrap draws; real 10 cases + 24 in-menu MuJoCo worlds',
         'summary':summary,'rows':rows,'policy_note':'Push-count threshold is a product policy; neither 6 nor any count guarantees 90% coverage.'}
    (REPO/'runs/proof/reliability_sweep.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
