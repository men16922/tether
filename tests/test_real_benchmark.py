import math

import pytest

from tether.eval.real_benchmark import baselines, comparison, constant_decel_mu, held_out
from tether.sim.params import ParamSet
from tether.sim.push_task import analytic_track, slide_distance
from tether.studio.session import Push


def pushes():
    p = ParamSet.nominal().with_(object_mu=0.4, table_mu=0.4, actuator_gain=1.0)
    return [Push(slide_distance(v, p), launch_speed=v, track=analytic_track(v, p), origin='video')
            for v in (1.0, 1.3, 1.6, 1.9)]


def test_quadratic_baselines_recover_known_constant_deceleration():
    ps = pushes()
    assert constant_decel_mu(ps[0].track, ps[0].stop) == pytest.approx(0.4, abs=0.01)
    b = baselines(ps)
    assert b['pushes'] == b['usable_quadratic_fits'] == 4
    assert b['median'] == pytest.approx(0.4, abs=0.01)
    assert b['mean'] == pytest.approx(0.4, abs=0.01)
    assert baselines([Push(0.1, launch_speed=1, track=[0, 0.1])])['median'] is None


def test_single_push_has_no_held_out_score():
    assert held_out(pushes()[:1])['status'] == 'not evaluable'


def test_held_out_stop_does_not_enter_its_fit():
    ps = pushes()
    a = held_out(ps)['rows'][0]
    ps[0].stop += 0.5
    ps[0].track = [99.0] * len(ps[0].track)
    b = held_out(ps)['rows'][0]
    assert a['predicted_m'] == b['predicted_m']
    assert b['training_pushes'] == 3
    assert all(math.isfinite(v) for v in b['predicted_m'].values())


def test_comparison_uses_identical_eligible_training_for_all_methods():
    ps=pushes()[:3]
    ps.append(Push(0.1,launch_speed=8.0,track=[0.0,0.1]))
    b=comparison(ps)
    assert b['shared_training_pushes']==3 and b['shared_excluded_pushes']==1
    assert b['tether_matched_mu']==pytest.approx(0.4,abs=0.01)
    h=held_out(ps)
    # The bad push is excluded from training for every method, but stays a held-out prediction target.
    assert len(h['rows'])==4
    assert h['rows'][0]['training_pushes']==2
    assert h['rows'][0]['predicted_m']['tether']==pytest.approx(ps[0].stop,abs=0.01)
