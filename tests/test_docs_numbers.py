"""The numbers in README and DEVPOST are the numbers in runs/proof/: every headline claim is checked against the
recorded proof files, so a rerun that changes a result fails here until the text is updated."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PROOF = ROOT / "runs" / "proof"
README = (ROOT / "README.md").read_text()
DEVPOST = (ROOT / "docs" / "submission" / "DEVPOST.md").read_text()


def pct(x: float) -> str:
    return f"{int(x * 100 + 0.5 + 1e-9)}%"  # half up, as tether/eval/prove.py and the film


def load(name: str) -> dict:
    path = PROOF / name
    if not path.exists():
        pytest.skip(f"{name} not recorded")
    return json.loads(path.read_text())


ROWS = {"in-menu": ("In-menu effects only", "In-menu effects"), "speed": ("+ friction that depends on speed", "+ speed-dependent friction"),
        "two regions": ("+ a second friction region", "+ a second friction region"), "slope": ("+ the table tilted 1.5–3°", "+ a 1.5–3° tilt")}


@pytest.mark.parametrize("cond", list(ROWS))
def test_cross_engine_tables_match_the_recorded_run(cond):
    r = load("cross_engine.json")["summary"][cond]
    m, best = r["success_mean"], r["best_dr_width"]
    ci = r["success_ci95"]["tether"]
    cells = [pct(m["current"]), pct(m[best]), pct(m["dr oracle"]), pct(m["exact params"]), f"**{pct(m['tether'])}** ({pct(ci[0])[:-1]}–{pct(ci[1])[:-1]})"]
    for doc, label in ((README, ROWS[cond][0]), (DEVPOST, ROWS[cond][1])):
        line = next(ln for ln in doc.splitlines() if ln.strip().startswith(f"| {label} |"))
        got = [c.strip() for c in line.strip().strip("|").split("|")][1:6]
        assert got == cells, (label, got, cells)


def test_cross_engine_summary_sentences():
    s = load("cross_engine.json")["summary"]
    at_least = sum(r["tether_beats_best_dr"] + r["tether_ties_best_dr"] for r in s.values())
    worlds = sum(r["worlds"] for r in s.values())
    assert f"in {at_least} of {worlds} worlds" in README and f"in {at_least} of {worlds} worlds" in DEVPOST
    assert f"{s['speed']['flagged']}/24 as" in README and f"{s['in-menu']['flagged']}/24 (false alarms)" in README
    assert f"in-menu worlds (the old 1 cm rule flagged {s['in-menu']['size_flagged']})" in DEVPOST


def test_real_footage_friction_law():
    law = load("real_friction.json")["friction_law"]
    for doc in (README, DEVPOST):
        assert f"{law['best']['coulomb']} of {law['slides']}" in doc or f"on {law['best']['coulomb']}" in doc
        assert f"decisively worse on {law['coulomb_beats_viscous_strongly']}" in doc or f"viscous\n  law decisively on {law['coulomb_beats_viscous_strongly']}" in doc


def test_retrain_and_coverage_claims():
    p = load("proof.json")
    ex = p["examples"]
    r = {k: ex[k]["retrain_hidden_success"] for k in ex}
    row = lambda name, k: f"| {name} | {pct(r[k]['current'])} | {pct(r[k]['wide'])} | **{pct(r[k]['tether'])}** |"  # noqa: E731
    for name, k in (("Robot phone video", "flick"), ("Robot log", "lab-bench"), ("Pusher log", "press-line"),
                    ("Roadside video", "stop-line"), ("Short pushes only", "short-reach")):
        assert row(name, k) in DEVPOST, row(name, k)
    assert f"truth {pct(p['coverage']['coverage'])} of the time" in DEVPOST
    ce = load("cross_engine.json")["summary"]["in-menu"]
    assert f"{pct(ce['coverage'])} of {ce['values']} values" in DEVPOST


def test_real_benchmark_tables_match_the_recorded_run():
    rb = load("real_benchmark.json")
    for o in rb["objects"]:
        lg, vd = o["log"], o["video"]
        video_value = (f"{vd['mu']:.3f} ({vd['interval'][0]:.3f}–{vd['interval'][1]:.3f})" if vd['interval']
                       else f"{vd['mu']:.3f} (unavailable: one push)")
        readme = (f"| {o['object']} | {o['mu_tilt_test']:.3f} | {lg['mu']:.3f} ({lg['interval'][0]:.3f}–{lg['interval'][1]:.3f}) | "
                  f"{video_value} | {o['pushes']['log']} / {o['pushes']['video']} |")
        assert readme in README, readme
        assert f"| {o['object']} | {o['mu_tilt_test']:.3f} | {lg['mu']:.3f} | {vd['mu']:.3f} |" in DEVPOST
    sm = rb["summary"]
    for doc in (README, DEVPOST):
        assert f"{sm['log']['mean_abs_error']:.3f}" in doc and f"{sm['video']['mean_abs_error']:.3f}" in doc


def test_real_baseline_and_held_out_tables_match_proof():
    rb = load("real_benchmark.json")
    for doc in (README, DEVPOST):
        for way in ("log", "video"):
            b = rb['baselines'][way]
            assert (f"| {way} | {b['tether']['mean_abs_error']:.3f} | "
                    f"{b['median']['mean_abs_error']:.3f} | {b['mean']['mean_abs_error']:.3f} |") in doc
        v = rb['excluded']['video']
        assert f"{v['excluded']}/{v['total']}" in doc
        for o in rb['objects']:
            for way, h in o['held_out'].items():
                if h['status'] == 'not evaluable':
                    assert f"| {o['object']} / {way} | 0 | not evaluable (one push) |" in doc
                    continue
                cells = [f"{h['summary'][k]['median_cm']:.1f} / {h['summary'][k]['p90_cm']:.1f}"
                         for k in ('tether', 'median', 'mean')]
                assert f"| {o['object']} / {way} | {len(h['rows'])} | " + ' | '.join(cells) + ' |' in doc


def test_paper_reference_always_states_different_protocol():
    files = [ROOT / 'README.md', ROOT / 'docs/submission/DEVPOST.md', ROOT / 'docs/project/STATUS.md']
    files += list((ROOT / 'docs/article').glob('*.md')) + list((ROOT / 'docs/guide').glob('*.md'))
    generated = ROOT / 'submission/about-the-project.md'
    if generated.exists():
        files.append(generated)
    for file in files:
        for paragraph in file.read_text().split('\n\n'):
            if '0.082' in paragraph:
                assert 'RGB-D' in paragraph and ('different protocol' in paragraph or '다른 프로토콜' in paragraph), (file, paragraph)
    stage=(ROOT/'film/stage.html').read_text()
    line=next(s for s in stage.splitlines() if 'DATA.real.paper_reference' in s)
    assert 'different protocol' in line and 'RGB-D' in line


def test_public_article_uses_simulation_vocabulary():
    for path in (ROOT/'docs/article').glob('*.md'):
        text=path.read_text()
        assert '숨겨진 실제 환경' not in text and 'hidden real world' not in text


def test_export_file_held_out_table_matches_recordings():
    for p in (ROOT/'runs/studio-demo').glob('*.json'):
        v=json.loads(p.read_text())['verify']
        assert v['mode']=='held-out prediction' and v['file_roundtrip']['verification']=='executed'
        row=(f"| {p.stem} | {v['training_pushes']} / {v['evaluation_pushes']} | "
             f"{v['rms_calibrated_m']*100:.2f} | {v['rms_current_m']*100:.2f} |")
        assert row in README and row in DEVPOST


def test_nemotron_pilot_table_only_uses_complete_training_fixtures():
    r=load('agent_ablation.json')
    complete=[x for x in r['rows'] if x['agent_status']=='evaluated']
    assert r['missing_fixtures']==len(r['rows'])-len(complete)
    for x in complete:
        cells=[f"{x['conditions'][k]['stop_median_cm']:.2f}" for k in ('offline','agent','agent_cross_check')]
        row='| '+x['case']+' | '+' | '.join(cells)+' |'
        assert row in README and row in DEVPOST


def test_reliability_table_matches_public_real_evidence():
    r=load('real_benchmark.json')['reliability_evaluation']
    for doc in (README,DEVPOST):
        for x in r['rows']:
            flag='yes' if x['over_0_05'] and x['flagged'] else 'missed' if x['over_0_05'] else '—'
            covered='unavailable' if not x['interval_available'] else 'yes' if x['covered'] else 'no'
            assert f"| {x['object']} / {x['path']} | {x['abs_mu_error']:.3f} | {x['level']} | {flag} | {covered} |" in doc
