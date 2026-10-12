import json
import os
import sys
import types

import pytest

from tether.studio import export
from tether.studio.fit import calibrate
from tether.studio.session import load
from tether.studio.roundtrip import read_export, replay
from tether.paths import REPO


def sample(name='lab-bench',domain='robot'):
    s=load((REPO/f'tether/studio/samples/{name}.csv').read_text(),f'{name}.csv')
    s.meta['domain']=domain
    return s,calibrate(s,n_boot=8)


@pytest.mark.parametrize('domain,scale', [('robot',1.0),('driving',25.0)])
def test_export_files_run_new_pushes_in_a_separate_newton_process(tmp_path,domain,scale):
    pytest.importorskip('newton')
    s,cal=sample('brake-log' if domain=='driving' else 'lab-bench',domain)
    export.write_all(tmp_path,s,cal)
    out=replay(tmp_path,[1.2*scale**0.5,1.8*scale**0.5,2.4*scale**0.5])
    assert out['worker_pid'] != os.getpid()
    assert out['domain']==domain and out['verification']=='executed'
    assert len(out['rows'])==3 and out['max_error_m']/scale<0.02
    assert all(not r['tipped'] for r in out['rows'])
    data=json.loads((tmp_path/'calibration.json').read_text())
    assert data['calibration']['ensemble']==cal.ensemble
    # Deliberately corrupt the separately generated file: validation must reject before executing Newton.
    p=tmp_path/'newton_calibration.py'
    original=p.read_text()
    p.write_text(original.replace(f'MU_EFF = {cal.model["mu_eff"]:.4f}',f'MU_EFF = {round(cal.model["mu_eff"],4)+0.0001:.4f}'))
    with pytest.raises(ValueError,match='MU_EFF'):
        read_export(tmp_path)
    p.write_text(original)
    p.write_text(p.read_text().replace(f'MU_EFF = {cal.model["mu_eff"]:.4f}','MU_EFF = 9.0'))
    with pytest.raises(ValueError,match='MU_EFF'):
        read_export(tmp_path)


def test_isaac_effective_dynamic_friction_range_matches_the_pair_interval(monkeypatch):
    s,cal=sample()
    cal.model['patch_y0']=None
    cal.model['patch_mu']=None
    cal.model['mu_eff']=0.5
    cal.intervals['mu_eff']=(0.4,0.6)
    cal.structure=['mu_eff']
    def term(**kw): return types.SimpleNamespace(**kw)
    def entity(name): return types.SimpleNamespace(name=name)
    envs=types.ModuleType('isaaclab.envs'); envs.mdp=types.SimpleNamespace(randomize_rigid_body_material=object())
    managers=types.ModuleType('isaaclab.managers'); managers.EventTermCfg=term; managers.SceneEntityCfg=entity
    utils=types.ModuleType('isaaclab.utils'); utils.configclass=lambda cls:cls
    for name,mod in [('isaaclab',types.ModuleType('isaaclab')),('isaaclab.envs',envs),('isaaclab.managers',managers),('isaaclab.utils',utils)]:
        monkeypatch.setitem(sys.modules,name,mod)
    ns={}; exec(export.isaaclab_snippet(s,cal),ns)
    obj=ns['CalibratedEventCfg'].object_material.params
    table=ns['CalibratedEventCfg'].table_material.params
    assert obj['asset_cfg'].name=='object' and table['asset_cfg'].name=='table'
    assert tuple((a+b)/2 for a,b in zip(obj['dynamic_friction_range'],table['dynamic_friction_range']))==pytest.approx((0.4,0.6))
    assert obj['static_friction_range'][0]>=obj['dynamic_friction_range'][1]
    assert 'not joint draws' in ns['__doc__']
