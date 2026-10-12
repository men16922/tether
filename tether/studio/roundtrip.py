"""Read exported files, validate their constants, execute new pushes in a fresh Newton process."""
from __future__ import annotations

import argparse
import ast
import json
import math
import subprocess
import sys
from pathlib import Path

from tether.agent.tool_agent import to_params
from tether.sim.params import ParamSet
from tether.sim.push_task import slide_distance
from tether.studio.domains import get, model_to_domain
from tether.studio.export import SCHEMA


def read_export(directory: Path):
    raw = json.loads((directory / 'calibration.json').read_text())
    if raw.get('schema') != SCHEMA:
        raise ValueError('unsupported calibration schema')
    cal = raw['calibration']
    base = ParamSet.nominal().with_(**cal.get('base', {}))
    p = to_params(cal['model'], base)
    d = get(raw.get('domain', {}).get('id'))
    scaled = model_to_domain(d, cal['model'])
    constants = {}
    for node in ast.parse((directory / 'newton_calibration.py').read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('MU_EFF','ACTUATOR_GAIN','FRICTION_REGION','CAMERA'):
                    constants[target.id] = ast.literal_eval(node.value)
    expected = {'MU_EFF': round(scaled['mu_eff'],4)}
    if 'actuator_gain' in cal['structure'] and raw['session'].get('has_commands', raw['session']['source'] != 'video'):
        expected['ACTUATOR_GAIN'] = round(scaled['actuator_gain'],4)
    if scaled.get('patch_y0') is not None:
        expected['FRICTION_REGION'] = {'y_start_m': round(scaled['patch_y0'],4), 'mu_eff': round(scaled['patch_mu'],4)}
    if raw['session'].get('has_targets'):
        expected['CAMERA'] = {'dx_m': round(scaled['camera_dx'],4), 'pitch_error_deg': round(scaled['camera_pitch_deg'],3),
                              'lens_k_per_m': round(scaled['lens_k'],5)}
    def matches(a,b):
        if isinstance(b,dict):
            return isinstance(a,dict) and all(k in a and matches(a[k],v) for k,v in b.items())
        return isinstance(a,(int,float)) and math.isfinite(a) and abs(a-b) <= 1e-12
    for key,value in expected.items():
        if key not in constants or not matches(constants[key],value):
            raise ValueError(f'Newton snippet disagrees with calibration.json: {key}')
    return raw,p,d


def replay(directory: str | Path, speeds=(1.1,1.7,2.3), starts=None, timeout=120) -> dict:
    """Speeds and starts are in exported domain units, not fitted base units. Never execute the generated Python."""
    directory=Path(directory).resolve()
    _,_,d=read_export(directory)
    speeds=list(speeds); starts=list(starts) if starts is not None else [0.0]*len(speeds)
    if not speeds or len(speeds)!=len(starts) or any(not math.isfinite(v) or v<=0 for v in speeds) or any(not math.isfinite(v) for v in starts):
        raise ValueError('positive finite speeds and matching finite starts required')
    output=directory/'newton_roundtrip.json'
    command=[sys.executable,'-m','tether.studio.roundtrip',str(directory),'--worker','--speeds',*map(str,speeds),'--starts',*map(str,starts)]
    subprocess.run(command,check=True,capture_output=True,text=True,timeout=timeout)
    return json.loads(output.read_text())


def worker(directory: Path, speeds: list[float], starts: list[float]):
    from tether.sim.newton_push import NewtonPushEnv
    import os

    raw,p,d=read_export(directory)
    vs=[v/d.speed_scale for v in speeds]; origins=[s/d.scale for s in starts]
    # Explicit measured launch speeds: no actuator uncertainty folded into the holdout input.
    p=p.with_(actuator_gain=1.0)
    trials=NewtonPushEnv().push(p,vs,origins).trials
    rows=[]
    for v,s,t in zip(vs,origins,trials):
        expected=slide_distance(v,p,s)
        rows.append({'launch_speed':v*d.speed_scale,'start_m':s*d.scale,'predicted_stop_m':expected*d.scale,
                     'newton_stop_m':t.slide*d.scale,'abs_error_m':abs(t.slide-expected)*d.scale,'tipped':bool(t.tipped)})
    out={'engine':'NVIDIA Newton (XPBD, CPU)','protocol':'export files -> separate process -> new measured-speed pushes',
         'verification':'executed','domain':d.id,'worker_pid':os.getpid(),'rows':rows,
         'max_error_m':max(r['abs_error_m'] for r in rows)}
    (directory/'newton_roundtrip.json').write_text(json.dumps(out,indent=2)+'\n')
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory',type=Path); ap.add_argument('--worker',action='store_true')
    ap.add_argument('--speeds',nargs='+',type=float,default=[1.1,1.7,2.3])
    ap.add_argument('--starts',nargs='+',type=float)
    a=ap.parse_args()
    out=worker(a.directory,a.speeds,a.starts or [0.0]*len(a.speeds)) if a.worker else replay(a.directory,a.speeds,a.starts)
    print(json.dumps(out,indent=2))


if __name__=='__main__':
    main()
