"""Close the loop in NVIDIA Newton: replay every measured push in the full physics engine with the exported
(calibrated) parameters and with the visitor's current simulator, and compare the stops with the real ones.

The fit uses the analytic slide model; this is the independent check that the exported numbers do what they claim
in the engine the visitor will load them into (XPBD contacts, the friction region switched per body, a real box
with mass and a finite contact patch). Each push is relaunched from its own measured start with its own measured
launch speed (video) or its logged command (robot log, where the calibrated actuator gain applies).
"""

from __future__ import annotations

import math
import time
import tempfile
from dataclasses import replace
from pathlib import Path

from tether.studio.fit import Calibration, fit_base
from tether.studio.session import Session


def verify(session: Session, cal: Calibration) -> dict:
    from tether.sim.newton_push import NewtonPushEnv

    t0 = time.time()
    pushes = [p for p in session.pushes if not p.tipped]
    if not pushes:
        return {"pushes": [], "note": "no untipped pushes to replay"}
    video = not session.has_commands
    # Policy: reserve the last 20% when at least six usable pushes exist; otherwise clearly label fit replay.
    training = session
    mode = "fit replay"
    if len(pushes) >= 6:
        n = max(1, math.ceil(len(pushes) * 0.2))
        training = replace(session, pushes=pushes[:-n])
        from tether.studio.fit import calibrate
        cal = calibrate(training)
        pushes = pushes[-n:]
        mode = "held-out prediction"
    cmds = [p.launch_speed if video else p.command for p in pushes]
    starts = [p.start or 0.0 for p in pushes]
    cur = fit_base(session)
    calp = cal.params
    if video:  # hand-launched: the measured launch speed is the speed, whatever the actuator
        cur, calp = cur.with_(actuator_gain=1.0), calp.with_(actuator_gain=1.0)
    env = NewtonPushEnv()
    from tether.studio import export
    from tether.studio.domains import of_session
    from tether.studio.roundtrip import replay
    d = of_session(session)
    with tempfile.TemporaryDirectory(prefix='tether-verify-') as tmp:
        export.write_all(tmp, training, cal)
        speeds = [u * calp['actuator_gain'] * d.speed_scale for u in cmds]
        trip = replay(Path(tmp), speeds, [s * d.scale for s in starts])
    b = env.push(cur, cmds, starts).trials
    rows = [{"i": session.pushes.index(p), "measured": round(p.stop, 4), "calibrated": round(x['newton_stop_m'] / d.scale, 4),
             "current": round(y.slide, 4), "tipped_in_sim": bool(x['tipped'])} for p, x, y in zip(pushes, trip['rows'], b)]

    def rms(k):
        return round(math.sqrt(sum((r[k] - r["measured"]) ** 2 for r in rows) / len(rows)), 4)

    worst = max(rows, key=lambda r: abs(r["calibrated"] - r["measured"]))
    return {"engine": "NVIDIA Newton (XPBD, CPU)", "pushes": rows, "rms_calibrated_m": rms("calibrated"),
            "mode": mode, "training_pushes": len(training.pushes), "evaluation_pushes": len(pushes),
            "file_roundtrip": {"verification": trip['verification'], "worker_pid": trip['worker_pid'], "protocol": trip['protocol']},
            "rms_current_m": rms("current"), "worst_calibrated_m": round(abs(worst["calibrated"] - worst["measured"]), 4),
            "seconds": round(time.time() - t0, 1)}
