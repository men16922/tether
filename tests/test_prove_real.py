from tether.eval.prove_real import evaluate_session
from tether.studio.session import Session,Push
from tether.sim.params import ParamSet
from tether.sim.push_task import slide_distance,analytic_track


def test_phone_holdout_outcomes_never_enter_calibration():
    p=ParamSet.nominal().with_(object_mu=0.5,table_mu=0.5)
    pushes=[Push(slide_distance(v,p),launch_speed=v,track=analytic_track(v,p)) for v in [1+0.1*i for i in range(15)]]
    s=Session('phone','video',pushes)
    cal,a=evaluate_session(s)
    pushes[10].stop+=0.3
    pushes[10].track=[99]*len(pushes[10].track)
    second,b=evaluate_session(s)
    assert cal.model==second.model
    assert a['rows'][0]['predicted_stop_m']==b['rows'][0]['predicted_stop_m']
    assert a['calibration_pushes']==10 and a['evaluation_pushes']==5
    assert b['rows'][0]['abs_error_cm']>20
