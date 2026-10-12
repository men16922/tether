# Status

Last Updated: 2026-10-13

## Current Baseline

- **Local evidence hardening (2026-10-12, not published/deployed):** real-input median/mean baselines on a shared eligible training pool (one short video push excluded from all methods), leave-one-push-out errors, 20/45 video exclusions and mocap-assisted inputs disclosed; paper reference is a different protocol. Single-push intervals hidden; reliability state and predictive-vs-parameter bands in UI/report/JSON. Isaac object/table material ranges corrected (stand-in checked, not executed); JSON ensemble/base exported; Newton file constants checked and JSON executed in a separate process, with held-out mode (last ~20%) or labelled fit replay. Independent-phone split/coverage/rejections tooling ready. Recorded examples refreshed offline; prior training provenance retained.
- **Current local checks (2026-10-13 ship):** make check: 144 passed (241.75 s); diff and credential-pattern checks passed. Read-only submission inventory/media check: no missing files, 147.85 s / 1080p / 67.9 s app footage, two YouTube placeholders. Strict presubmit was not rerun (the 2026-10-12 run failed on those placeholders). EN/KO desktop + 390 px workflow, export, Newton verify and server-result read after refresh verified, no JS errors/overflow (`runs/qa/browser-qa.json`). NAT tests skipped (nat not installed).
- **Bounded Nemotron pilot:** 9/35 complete training-only fixtures, no cross-check overrules in those 9 in-menu MuJoCo cases; no accuracy-advantage claim. Reported tokens × API prices $0.0963855, cap $0.10 enforced; 26 incomplete/missing, cumulative $0.40 request pending. Original pilot latency unavailable; invoice/balance not verified.
- **Film/package:** rebuilt 147.85 s, app footage 67.9 s; revised export narration uses local Samantha (other lines cached, no paid TTS). Portfolio EN/KO + real-object image synchronized locally; publication pending.

- **Public live demo (2026-10-11): Google Cloud Run** https://tether-454741001655.us-central1.run.app (`make deploy`: Cloud Build from committed files, key in Secret Manager, max 1 instance, scales to zero). Verified: pages, Nemotron analysis 42 s, Ask 2 s, video tracking 30 s, retraining 169 s. Hugging Face Docker Spaces now need PRO (402); GitHub Pages rolled back (static only).
- **Three domains (2026-10-09):** robot manipulation, autonomous vehicles (car braking to a stop line, wet/icy section, speed control, front camera; Froude-scaled 1:25, full-size units on the page and exports, CARLA export), factory inspection (pusher, oily rail, inspection camera). Same physics and pipeline; `tether/studio/domains.py`, tabs on the Studio data step, samples `stop-line` and `press-line`. Details: `docs/guide/05_세가지_업무.md`.
- **Studio simulation mode:** no video needed. The visitor sets the hidden table (friction, a region of different friction, robot motor/camera for logs), NVIDIA Newton renders a phone video or writes a robot log (`POST /api/studio/simulate`), the Studio diagnoses it blind, "Run these pushes in NVIDIA Newton" executes the next experiment in the same world (`/simulate-more`), and the visitor's settings are revealed as truth.

- **Studio (product surface, 2026-10-09):** `/studio` on the live server and `tether/web/dist/studio.standalone.html` (recorded). Flow: phone video (A4 sheet → focal/pose, parallax-corrected tracking, push segmentation) or robot log → Nemotron agent (offline: probe_real queues next-experiment cards) + cross-check → bootstrap 90% intervals, what-if worlds for unmeasured table, ghost boxes (old vs calibrated sim) over the user's video → Newton / Isaac Lab EventTermCfg / Markdown / JSON exports. CLI `python -m tether.studio`. Code: `tether/studio/`, `tether/server/studio_api.py`, `tether/web/studio.html`.
- Studio samples (Newton, truth revealed after; 19 of 21 truths inside 90% intervals across the six examples): flick take 2 μ 0.555 / region 0.376 m / μ 0.282 (truth 0.55 / 0.364 / 0.30); lab-bench μ 0.696, gain 0.872, region 0.376/0.449, pitch 1.9° (truth 0.70, 0.88, 0.38/0.45, 2°); short-reach refuses to invent the unmeasured region and asks for far pushes.
- Artifacts (private): Studio https://claude.ai/artifact/B8mi26WNiRJSiv9NTLoTjw ↔ Console https://claude.ai/artifact/WVBNfVMAzeNg71kDSFqYAf (v8, links to Studio).
- Experiment savings (`make studio-bench`): real pushes to 95%: suggested 5.8 / sweep 5.9–6.2 / random 7.7–7.9 (analytic 50, Newton 20 worlds).

- Scope: zero cost, no hardware, Tier 0. Local Mac: NVIDIA Newton; Nemotron 3 Super 120B on Nebius Token Factory (key in `.env`, gitignored); Ollama Nano for offline experiments.
- Public repo: https://github.com/men16922/tether
- Open world: params `patch_y0`/`patch_mu` (friction strip, seam-free Newton kernel) and `lens_k`; `InverseTrainer` (policy inverts the sim); `tether/agent/tool_agent.py` (Nemotron tool agent: decel_profile, perception_check, fit/test_hypothesis, probe_real, commit).
- Gap-Bench Newton 15/tier (Super, $0.30): closed 100 all; open rule 83±9 / sysID 100 / agent 100; compound rule 54±15 / sysID 97±4 / agent 96±6. Agent ≈ sysID, both ≫ rule. (The 6/tier edge 99 vs 93 was noise.)
- Dashboard v3 (artifact https://claude.ai/artifact/WVBNfVMAzeNg71kDSFqYAf): agent lab notebook, 3D viewer with friction strips, Gap-Bench panel, Cosmos eyes strip, live "Stump the agent" (`make serve`).
- Cosmos Reason 2 8B local (llama.cpp, `tether/agent/cosmos_eyes.py`): second opinion on tipping, 21/21 agree on demo clips; held-out tip recall ~50%.
- Nemotron family (open+compound, 6 each): Super 100/99, Lightning 100/95, Ultra 100/83, Nano 97/53.
- Historical baseline: `make check` 122 tests (2026-10-11); see current local checks above. Optional NAT integration needs nvidia-nat installed.
- Real objects (EV-RealPhys, MPI, tilt-test friction; current proof updated 2026-10-12): 4/5 within ±0.05 on log and video paths, mean error 0.019 / 0.029 (paper reference 0.082: different protocol, RGB-D online tracking and filtering). `make real-benchmark`. (incl. Studio core/API/video; live server, Newton env, tipping, recorded real Nemotron response replay, vision-role request shape).
- Agent: LLMDiagnoser (Nemotron) → fallback TrajectoryDiagnoser; HeuristicPlanner applies estimates. Tipped trials excluded from fits.
- Benchmark (Newton, 10 worlds): full DR 18% / nominal 24% / outcome-only 89% / tracking 94%; Nemotron 30B 99% (run 1) / 93% (run 2), P 0.89/0.94, R 1.00.
- Live server: `make serve` / Docker image (CPU) — verified with Token Factory in a container; deploy guide `docs/deploy/DEPLOY.md`.
- Submission assets (2026-10-11): `submission/` via `make submission` (film 2:28 with ~68 s of app footage from `film/footage.py`, thumbnail, gallery, YouTube description with chapters, Devpost About text); `docs/submission/SUBMIT.md` lists every field. Owner's guide: `docs/guide/00_처음_읽어주세요.md`.
- Demo: console scenarios recorded with Nemotron 3 Super; dashboard v3 https://claude.ai/artifact/WVBNfVMAzeNg71kDSFqYAf.

## Active Focus

Authority: `docs/project/NEXT_PLAN.md`.

0. **Blocked handoff (2026-10-13):** local A/B/C/E-tooling/F work is preserved. First resolve additional D credit; Tether local commit is authorized by /ship; push/Cloud Run/portfolio approval and owner filming/YouTube/Devpost inputs remain pending. No additional paid calls or publication authorized. Detailed execution record: `docs/project/plans/2026-10-11-feedback-hardening.md`.

## Open Risks

- Reliability is a diagnostic policy, not calibrated coverage: subsample coverage remains poor/nonmonotonic (`reliability_sweep.json`); all 10 public-real cases are flagged, so unflagged coverage is not estimable. Cracker normal tilt ≤1.798° and mocap/quadratic bias support the source Appendix C.3 constant-friction limitation; this does not independently isolate the original lab contact cause.
- Publication/Cloud Run deployment is still the 2026-10-11 version; Tether changes are recorded in the local ship commit; portfolio copies remain uncommitted. The credit ledger, ablation response recordings and generated QA/evaluation outputs remain local and unstaged.

- Independent phone calibration remains unvalidated: existing October 10 test clips in film/real/ have no truth.json/independent tilt record; owner says filming is not done. Tracking is template NCC and may struggle with hands occluding, motion blur, glossy objects. Public EV-RealPhys video evidence is separate from this owner-recorded case.
- Token Factory latency spiked on 2026-10-09 (95 s for 20 tokens); recording runs need long timeouts.

- Honest caveat: passive sysID with the same fitter matches the agent on clean (analytic) data; no measurable edge on Newton either at n=15. The agent's value is matching sysID without a hand-ordered structure library, choosing probes, and explaining fixes.
- Token Factory spend so far ≈ $2 of $25 (Super ≈ $0.0013 per diagnosis). Nano Omni not offered on Token Factory.
- Tipping regime (μ_eff ≳ 0.95): model-based diagnosis refuses to explain it; outcome-only fitting does better there.
- Local 30B can run away without max_tokens (fixed: cap 2048, timeout 180 s).
