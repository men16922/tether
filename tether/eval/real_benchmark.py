"""Real objects, real video, independently measured friction: Tether on the EV-RealPhys benchmark.

Data: EV-RealPhys (Kandukuri, Strecke, Stueckler, "Physics-Based Rigid Body Object Tracking and Friction Filtering
From RGB-D Videos", arXiv 2309.15703; MPI, CC BY-SA 4.0): YCB objects pushed by hand across a table and left to
slide to rest, filmed by an Intel RealSense D455 (848x480, 30 Hz after downsampling) with motion-capture poses and
the camera calibrated to the table. The friction of each object on the table was measured separately, by tilting the
table and timing ten slides per object (the paper's Table 5): cracker box 0.280, mustard bottle 0.159, pitcher 0.220,
bleach cleanser 0.169. Those values never enter Tether.

Two ways in, both ending in Tether's own fitter (offline structure search + bootstrap 90% intervals):

  video   Tether's tracker on the RGB frames (the object found as what moved, tracked back from rest), each pixel
          put on the table with the dataset's camera calibration: the role the A4 sheet plays in the Studio. The
          object's centre height (the number the Studio asks for) comes from where the object rests.
  log     the motion-capture centre of mass, as a robot would log it.

Each push is cut at release (peak speed, the hand lets go) and kept to rest; pushes of one object form one session.
The paper's estimator is a different-protocol reference (RGB-D online tracking and filtering), not a baseline.

Run: .venv/bin/python -m tether.eval.real_benchmark --download   (1.7 GB to runs/real_data/ev-realphys, git-ignored)
     .venv/bin/python -m tether.eval.real_benchmark              -> runs/proof/real_benchmark.json
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from tether.paths import REPO

ROOT = REPO
DATA = ROOT / "runs" / "real_data" / "ev-realphys"
OUT = ROOT / "runs" / "proof" / "real_benchmark.json"
URL = "https://keeper.mpdl.mpg.de/d/5ec213b655b44e40a382/files/?p=/ev-realphys.tar.gz&dl=1"
FPS = 30.0
GT = {"2": ("cracker box", 0.280), "5": ("mustard bottle", 0.159), "11": ("pitcher", 0.220), "12": ("bleach cleanser", 0.169),
      # All five independently measured combined values are in the paper's Table 5 (v3, May 2024).
      "14": ("mug", 0.110)}
PAPER = {"mean_abs_error": 0.082, "median_abs_error": 0.0246}


def baselines(pushes: list) -> dict:
    """Same retained pushes as Tether; report missing/nonphysical quadratic fits rather than silently filling them."""
    values = [constant_decel_mu(p.track, p.stop) for p in pushes]
    valid = [v for v in values if v is not None and math.isfinite(v) and v > 0]
    return {"pushes": len(pushes), "usable_quadratic_fits": len(valid),
            "median": None if not valid else round(float(np.median(valid)), 4),
            "mean": None if not valid else round(float(np.mean(valid)), 4)}


def matched_pushes(pushes: list) -> list:
    """Common comparison eligibility, independent of friction truth and model predictions."""
    out=[]
    for p in pushes:
        value=constant_decel_mu(p.track,p.stop)
        if value is not None and math.isfinite(value) and value>0:
            out.append(p)
    return out


def comparison(pushes: list, name='matched') -> dict:
    from tether.studio.fit import calibrate
    from tether.studio.session import Session
    out=baselines(pushes)
    common=matched_pushes(pushes)
    out['tether_matched_mu']=round(calibrate(Session(name,'video',common),n_boot=0).model['mu_eff'],4) if common else None
    out['shared_training_pushes']=len(common)
    out['shared_excluded_pushes']=len(pushes)-len(common)
    return out


def enrich(out: dict) -> dict:
    """All derived summaries come from the same object results on full and matched inputs."""
    objects=out['objects']
    out['data_license']={'name':'CC BY-SA 4.0','url':'https://creativecommons.org/licenses/by-sa/4.0/',
                         'source':'https://keeper.mpdl.mpg.de/d/5ec213b655b44e40a382/',
                         'attribution':'EV-RealPhys, Kandukuri, Strecke, Stueckler (MPI); derived numerical measurements'}
    out['held_out']={o['object']:o.get('held_out',{}) for o in objects}
    out['comparison_exclusions']={way:sum(o.get('baselines',{}).get(way,{}).get('shared_excluded_pushes',0) for o in objects)
                                  for way in ('log','video')}
    rows=[{'object':o['object'],'path':way,'abs_mu_error':abs(o[way]['error']),
           'over_0_05':abs(o[way]['error'])>0.05,'flagged':o[way]['reliability']['level']!='ok',
           'level':o[way]['reliability']['level'],'interval_available':o[way]['interval'] is not None,
           'covered':o[way]['inside_interval']} for o in objects for way in ('log','video') if way in o]
    unflagged=[r for r in rows if not r['flagged'] and r['interval_available']]
    out['reliability_evaluation']={'rows':rows,'unflagged_coverage':{'cases':len(unflagged),'covered':sum(bool(r['covered']) for r in unflagged)},
                                 'note':'Flags do not identify causation; accurate cases can also be flagged; shared bias remains undetectable.'}
    out['inputs']['measurement_error_model']='Both hand-launched benchmark paths use the default video prior: 1% shared scale, 1.5% shared speed, 3 mm stop jitter; not independently measured sensor noise.'
    return out


def refit_saved(path: Path = OUT) -> dict:
    """Recompute on the recorded ingestion, without decoding/tracking the images again."""
    from tether.studio.session import Session
    out=json.loads(path.read_text())
    for o in out['objects']:
        for way,raw in out['sessions'][o['object']].items():
            session=Session.from_json(raw)
            fitted=calibrate_pushes(session.name,session.pushes)
            fitted['error']=round(fitted['mu']-o['mu_tilt_test'],4)
            iv=fitted['interval'];fitted['inside_interval']=None if iv is None else iv[0]<=o['mu_tilt_test']<=iv[1]
            o[way]=fitted
            o['baselines'][way]=comparison(session.pushes,session.name)
            o['held_out'][way]=held_out(session.pushes,session.name)
    for way in ('log','video'):
        for method,key in (('median','median'),('mean','mean'),('tether','tether_matched_mu')):
            errs=[abs(o['baselines'][way][key]-o['mu_tilt_test']) for o in out['objects']
                  if way in o['baselines'] and o['baselines'][way][key] is not None]
            out['baselines'][way][method]={'objects':len(errs),'mean_abs_error':round(float(np.mean(errs)),4) if errs else None}
    out['inputs']['baseline_protocol']='same positive-quadratic-fit training pool for Tether and baselines; full Tether estimates separately; held-out push removed before common training eligibility'
    out['recompute_protocol']='refit recorded sessions; original ingestion/track exclusions retained'
    enrich(out)
    path.write_text(json.dumps(out,indent=1)+'\n')
    return out


def held_out(pushes: list, name: str = "held-out") -> dict:
    """Refit structure AND numbers without the scored push; only its measured launch speed is used to predict."""
    from tether.sim.push_task import slide_distance
    from tether.studio.fit import calibrate
    from tether.studio.session import Session

    if len(pushes) < 2:
        return {"status": "not evaluable", "reason": "single-push object", "rows": []}
    rows = []
    for i, p in enumerate(pushes):
        train = matched_pushes(pushes[:i] + pushes[i + 1:])
        if not train:
            rows.append({'held_out_index':i,'training_pushes':0,'measured_m':p.stop,'launch_mps':p.launch_speed,
                         'predicted_m':{k:None for k in ('tether','median','mean')},
                         'abs_error_cm':{k:None for k in ('tether','median','mean')},'reason':'no common eligible training push'})
            continue
        cal = calibrate(Session(name, "video", train), n_boot=0)
        params = cal.params.with_(actuator_gain=1.0)
        predicted = {"tether": slide_distance(p.launch_speed, params, p.start)}
        bs = baselines(train)
        for method in ("median", "mean"):
            mu = bs[method]
            predicted[method] = None if mu is None else p.launch_speed ** 2 / (2 * 9.81 * mu)
        rows.append({"held_out_index": i, "training_pushes": len(train), "measured_m": p.stop,
                     "launch_mps": p.launch_speed, "predicted_m": predicted,
                     "abs_error_cm": {k: None if v is None else round(abs(v - p.stop) * 100, 4) for k, v in predicted.items()}})
    summary = {}
    for method in ("tether", "median", "mean"):
        errs = [r["abs_error_cm"][method] for r in rows if r["abs_error_cm"][method] is not None]
        summary[method] = {"pushes": len(errs), "median_cm": round(float(np.median(errs)), 4) if errs else None,
                           "p90_cm": round(float(np.percentile(errs, 90)), 4) if errs else None}
    return {"status": "evaluated", "protocol": "leave-one-push-out; refit structure; measured held-out launch speed", "summary": summary, "rows": rows}


def sequences() -> list[Path]:
    base = DATA / "ev-realphys"
    return sorted(p for split in ("val_sliding", "test_sliding") for p in (base / split).glob("*") if (p / "scene_gt.json").exists())


def load(seq: Path) -> dict:
    gt = json.loads((seq / "scene_gt.json").read_text())
    cam = json.loads((seq / "scene_camera.json").read_text())
    props = json.loads((seq / "scene_properties.json").read_text())["object_properties"]
    obj = next(iter(props))
    n = len(gt)
    com = np.array([gt[str(i)][0].get("cam_t_inertial_m2w", gt[str(i)][0]["cam_t_m2w"]) for i in range(n)]) / 1000.0
    return {"seq": seq, "obj": obj, "n": n, "com": com, "cam": [cam[str(i)] for i in range(n)]}


def push_from(xy: np.ndarray):
    """One push the way the Studio measures video: positions along the motion, segmented and launched by
    studio.video (release at peak speed, launch speed from a constant-deceleration fit to the next frames)."""
    from tether.studio.session import Push
    from tether.studio.video import launch_state, segment

    d = xy[-1] - xy[0]
    axis = d / (np.linalg.norm(d) + 1e-12)
    s = (xy - xy[0]) @ axis
    segs = segment(s, FPS)
    if not segs:
        return None, None
    r, e = max(segs, key=lambda q: s[q[1]] - s[q[0]])  # the push itself, not a wobble at rest
    rest = float(np.median(s[e:min(len(s), e + 5)]))
    s0, v0 = launch_state(s, r, e, FPS)
    track = [0.0] + [float(x - s0) for x in s[r + 1:e + 1]] + [rest - s0] * 3
    return Push(stop=round(rest - s0, 4), launch_speed=round(float(v0), 4), track=[round(x, 4) for x in track], origin="video"), (r, e)


def constant_decel_mu(track: list[float], stop: float) -> float | None:
    """Per push, without Tether: fit s(t) = v0 t - a t^2 / 2 until rest, mu = a / g."""
    s = np.asarray(track)
    k = int(np.argmax(s >= stop - 1e-3)) if stop > 0 else 0
    if k < 4:
        return None
    t = np.arange(k + 1) / FPS
    A = np.stack([t, -0.5 * t * t], axis=1)
    v0, a = np.linalg.lstsq(A, s[: k + 1], rcond=None)[0]
    return float(a / 9.81)


def video_xy(d: dict) -> tuple[np.ndarray | None, str]:
    """Tether's tracker on the RGB frames, pixels put on the table plane (z = object centre height) with the dataset's
    camera calibration."""
    import cv2

    from tether.studio.video import track

    rgb = d["seq"] / "rgb"
    files = sorted(rgb.glob("*.png")) or sorted(rgb.glob("*.jpg"))
    if not files:
        return None, "no rgb frames"
    frames = [cv2.imread(str(f)) for f in files][: d["n"]]
    # the click: where the object rests (the Studio asks for a click when it cannot find the object itself; these
    # clips start mid-push with the hand and a ruler in view). The motion-capture rest position, projected into
    # the image, stands in for that one click; every other position comes from the RGB tracker.
    c = d["cam"][-1]
    K, R, t = np.asarray(c["cam_K"]).reshape(3, 3), np.asarray(c["cam_R_w2c"]).reshape(3, 3), np.asarray(c["cam_t_w2c"]) / 1000.0
    proj = lambda w: (K @ (R @ w + t))[:2] / (K @ (R @ w + t))[2]  # noqa: E731
    rest = d["com"][-1]
    x, y = proj(rest)
    size = float(np.linalg.norm(proj(rest + [0.05, 0, 0]) - proj(rest - [0.05, 0, 0])))  # ~10 cm footprint
    uv, _ = track(frames[::-1], (x, y), int(np.clip(size * 1.1, 20, 220)))
    uv = np.asarray(uv)[::-1]
    pad = np.pad(uv, ((2, 2), (0, 0)), mode="edge")
    uv = np.stack([np.median(pad[i:i + 5], axis=0) for i in range(len(uv))])
    h = float(np.median(d["com"][-5:, 2]))  # centre height above the table: the Studio's "object height" input
    out = []
    for (u, v), c in zip(uv, d["cam"]):
        K = np.asarray(c["cam_K"]).reshape(3, 3)
        R = np.asarray(c["cam_R_w2c"]).reshape(3, 3)
        t = np.asarray(c["cam_t_w2c"]) / 1000.0
        C = -R.T @ t  # camera centre in the table frame
        ray = R.T @ np.linalg.solve(K, [u, v, 1.0])
        lam = (h - C[2]) / ray[2]
        out.append((C + lam * ray)[:2])
    return np.asarray(out), "ok"


def calibrate_pushes(name: str, pushes: list) -> dict:
    from tether.studio.fit import calibrate
    from tether.studio.session import Session

    s = Session(name, "video", pushes)
    cal = calibrate(s)
    iv = cal.intervals.get("mu_eff")
    return {"mu": round(cal.model["mu_eff"], 4), "interval": None if iv is None else [round(x,4) for x in iv], "structure": cal.structure,
            'reliability': cal.reliability,
            "stop_rms_m": cal.residuals["stop_residual_rms_m"]}


def main(with_video: bool = True) -> dict:
    from tether.studio.session import Session
    seqs = sequences()
    if not seqs:
        sys.exit("EV-RealPhys not found: run with --download first")
    by_obj: dict[str, dict] = {}
    rows = []
    for seq in seqs:
        d = load(seq)
        if d["obj"] not in GT:
            continue
        row = {"sequence": f"{seq.parent.name}/{seq.name}", "object": GT[d["obj"]][0]}
        p_log, seg = push_from(d["com"][:, :2])
        by_obj.setdefault(d["obj"], {"log": [], "video": []})
        if p_log is None:
            row["log"] = "no push found"
        else:
            row.update(release_frame=seg[0], rest_frame=seg[1], launch_mps=p_log.launch_speed, slide_m=p_log.stop,
                       mu_per_push_log=constant_decel_mu(p_log.track, p_log.stop))
            by_obj[d["obj"]]["log"].append(p_log)
        if with_video:
            xy, status = video_xy(d)
            row["video"] = status
            if xy is not None:
                from tether.studio.video import implausible

                p_vid, _ = push_from(xy)
                why = implausible(p_vid.track, FPS, p_vid.launch_speed) if p_vid is not None else None
                if p_vid is None or why:
                    row["video"] = "no push found" if p_vid is None else f"left out: track {why}"
                else:
                    row.update(slide_m_video=p_vid.stop, launch_mps_video=p_vid.launch_speed,
                               mu_per_push_video=constant_decel_mu(p_vid.track, p_vid.stop))
                    if p_log is not None:
                        row["video_vs_mocap_stop_m"] = round(abs(p_vid.stop - p_log.stop), 4)
                    by_obj[d["obj"]]["video"].append(p_vid)
        rows.append(row)
        print(row, flush=True)
    objects = []
    for oid, ps in by_obj.items():
        name, mu_true = GT[oid]
        o = {"object": name, "mu_tilt_test": mu_true, "pushes": {w: len(ps[w]) for w in ps}}
        for way in ("log", "video"):
            if ps[way]:
                r = calibrate_pushes(f"{name} ({way})", ps[way])
                r["error"] = round(r["mu"] - mu_true, 4)
                r["inside_interval"] = None if r['interval'] is None else r["interval"][0] <= mu_true <= r["interval"][1]
                o[way] = r
                o.setdefault("baselines", {})[way] = comparison(ps[way],f'{name} ({way}, matched)')
                o.setdefault("held_out", {})[way] = held_out(ps[way], f"{name} ({way})")
        objects.append(o)
    summary = {}
    for way in ("log", "video"):
        errs = [abs(o[way]["error"]) for o in objects if way in o]
        if errs:
            summary[way] = {"objects": len(errs), "mean_abs_error": round(float(np.mean(errs)), 4),
                            "median_abs_error": round(float(np.median(errs)), 4), "within_0_05": int(sum(e <= 0.05 for e in errs))}
    baseline_summary = {}
    for way in ("log", "video"):
        baseline_summary[way] = {}
        for method,key in (("median","median"),("mean","mean"),("tether","tether_matched_mu")):
            errs = [abs(o["baselines"][way][key] - o["mu_tilt_test"]) for o in objects
                    if way in o.get("baselines", {}) and o["baselines"][way][key] is not None]
            baseline_summary[way][method] = {"objects": len(errs), "mean_abs_error": round(float(np.mean(errs)), 4) if errs else None}
    excluded = {}
    for way in ("log", "video"):
        if way == "video" and not with_video:
            excluded[way] = {"status": "not run"}
            continue
        reasons = {}
        for row in rows:
            reason = row.get(way, "ok")
            if reason != "ok":
                reasons[reason] = reasons.get(reason, 0) + 1
        excluded[way] = {"total": len(rows), "retained": sum(o["pushes"][way] for o in objects),
                         "excluded": sum(reasons.values()), "by_reason": reasons}
    out = {"source": "EV-RealPhys (Kandukuri et al. 2023, MPI, CC BY-SA 4.0), real split", "fps": FPS,
           "ground_truth": "tilted-table slides, measured separately (paper Table 5)", "paper_estimator_on_real": PAPER,
           "paper_reference_protocol": "different protocol: RGB-D online tracking and filtering; not a same-input baseline",
           "inputs": {"splits": ["val_sliding", "test_sliding"], "video_camera": "dataset camera calibration",
                      "video_tracking_start": "mocap rest position projected into the image (replaces user click)",
                      "video_object_height": "median mocap centre height of last five frames",
                      "log": "mocap centre positions, segmented with the same release/launch estimator as video",
                      "baseline_protocol": "same positive-quadratic-fit training pool for Tether and baselines; full Tether estimates also shown separately; held-out push excluded before common training eligibility"},
           "baselines": baseline_summary, "held_out": {o["object"]: o.get("held_out", {}) for o in objects},
           "excluded": excluded, "summary": summary, "objects": objects, "rows": rows,
           "sessions": {GT[oid][0]: {way: Session(
                       f'{GT[oid][0]} ({way})', 'video', ps[way]).to_json() for way in ('log', 'video') if ps[way]}
                        for oid, ps in by_obj.items()}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    enrich(out)
    OUT.write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out[k] for k in ("summary", "objects")}, indent=1, default=str))
    return out


def download() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    if (DATA / "ev-realphys").exists():
        return
    tar = DATA / "ev-realphys.tar.gz"
    if not tar.exists():
        subprocess.run(["curl", "-L", "-o", str(tar), URL], check=True)
    subprocess.run(["tar", "-xzf", str(tar), "-C", str(DATA)], check=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--no-video", action="store_true")
    ap.add_argument('--from-recorded-sessions',action='store_true',help='refit the recorded public input tracks, no re-tracking')
    a = ap.parse_args()
    if a.from_recorded_sessions:
        refit_saved()
    else:
        if a.download:
            download()
        main(with_video=not a.no_video)
    _ = math
