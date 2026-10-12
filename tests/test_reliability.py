import json

import pytest

from tether.studio.fit import calibrate, predict_stop
from tether.studio.session import Push, Session
from tether.studio import export
from tether.sim.params import ParamSet
from tether.sim.push_task import analytic_track, slide_distance
from tether.paths import REPO


def case(n):
    p=ParamSet.nominal().with_(object_mu=0.5,table_mu=0.5)
    ps=[Push(slide_distance(v,p),launch_speed=v,track=analytic_track(v,p),origin='video') for v in [1+0.12*i for i in range(n)]]
    s=Session('known','video',ps)
    return s,calibrate(s,n_boot=8)


def test_single_push_has_no_interval_anywhere():
    s,c=case(1)
    assert c.reliability['level']=='unreliable'
    assert not c.intervals and not c.ensemble
    assert c.gap[0]['lo'] is None and c.gap[0]['hi'] is None
    assert not c.curves['stops']['band']
    assert predict_stop(c,1.4)['predictive_range_m'] is None
    j=export.to_json(s,c)
    assert j['calibration']['reliability']==c.reliability
    assert j['calibration']['predicted']['after']['lo'] is None
    assert j['calibration']['predicted']['after']['hi'] is None
    assert '90%:' not in export.markdown(s,c)
    assert '90% interval' not in export.newton_snippet(s,c)
    assert 'unavailable' in export.markdown(s,c)
    assert 'Intervals unavailable' in export.newton_snippet(s,c)


def test_predictive_band_includes_residual_noise_and_is_wider():
    _,c=case(8)
    c.residuals['stop_residual_rms_m']=0.04
    d=predict_stop(c,1.7)
    a,b=d['parameter_range_m']; lo,hi=d['predictive_range_m']
    assert lo<a<=d['median_m']<=b<hi
    assert hi-lo>=2*1.64*0.04
    with pytest.raises(ValueError): predict_stop(c,float('nan'))


def test_status_copy_has_both_languages_in_the_ui():
    from tether.studio.reliability import LABELS,REASONS
    page=(REPO/'tether/web/studio.html').read_text()
    for d in (*LABELS.values(),*REASONS.values()):
        assert d['en'] in page and d['ko'] in page
    assert 'predictive_band = l(cu.stops.predictive_band)' in page


def test_negative_launch_origin_does_not_disable_an_active_friction_region():
    _,c=case(8)
    c.model.update(mu_eff=.6,patch_y0=.35,patch_mu=.3)
    c.ensemble=[]
    expected=1.15+(4.5**2-2*.6*9.81*1.15)/(2*.3*9.81)
    assert predict_stop(c,4.5,start=-.8)['median_m']==pytest.approx(expected)
