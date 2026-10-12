# Next Plan

Last Updated: 2026-10-13

Only open work remains here. Completed A/B/C/E-tooling/F-local work and proof paths are recorded in
COMPLETED_SUMMARY and PROGRESS_LOG. Detail: `docs/project/plans/2026-10-11-feedback-hardening.md`.

Blocked checkpoint: approvals and owner inputs remain pending; a checkpoint does not authorize paid calls or publication.

## Priority 1 — Nemotron ablation scope and credit

- [ ] [manual] Additional-credit decision pending: $0.0963855 (reported tokens × current model API prices, not invoice) used under the approved $0.10 cap. 9/35 complete, 26 incomplete/missing. Requested additional ≤$0.30, cumulative ≤$0.40. No further paid call before approval.
- [ ] [auto, after approval] `.venv/bin/python -m tether.eval.agent_ablation --live --budget-usd 0.4`. Ledger persists across processes; completed fixtures replay, partial fixtures continue the same conversation. Check `runs/ablation-fixtures/credit_ledger.json`; unknown usage remains reserved. Recompute paired tables from complete cases only, then replay offline. If cap remains $0.10, retain the explicitly bounded 9-case pilot and mark the full 35-case comparison unavailable.
- [ ] [auto] If more cases complete, update README/DEVPOST/article positioning. Keep no accuracy-advantage claim unless justified. Original latency for the first pilot was not retained; never label replay latency as live latency.
- [ ] [manual, optional] 3–5 first-time users interpret a result and choose an experiment. Currently explicitly not tested with users.

## Priority 2 — Independent phone case

- [ ] [manual] Owner films ≥1 object–surface pair, ideally 3, with phone + A4 and independent kinetic tilt angle. 15 flicks/pair: first 10 retained pushes calibrate, remaining 5 evaluate; small design, not statistical sufficiency. Place files and truth.json in gitignored `film/real/`; existing October 10 test clips lack this truth record and are not independent validation. Guide: `docs/guide/06_실제_영상_촬영법.md`.
- [ ] [auto, after files arrive] `make prove-real`: report held-out stop median/p90, predictive coverage, rejected pushes by reason, tilt comparison and export JSON/AST/separate-process Newton round trip. Do not count this as completed until real recordings exist. A's public leave-one-push-out evidence is the fallback, not independent phone usability.

## Priority 3 — Release the reviewed local changes

- [ ] [manual] Authorize Tether push, existing Cloud Run redeploy, and portfolio commit/push separately from Token Factory credit. Tether local commit is authorized by /ship and verified offline; no external release is authorized. Portfolio `.serena/project.yml` is pre-existing WIP and must remain excluded.
- [ ] [auto, after approval] Review the local ship commit, run the current release gate and credential scan, push Tether; verify remote HEAD. `make deploy` archives committed HEAD, so do not deploy before the code commit. Prefer existing secret without re-upload/permission changes (`--no-secret`). Verify live pages, offline analysis and export; additional live-model calls require an explicit credit scope.
- [ ] [auto, after approval] Portfolio local copies at `/Users/men1692/Desktop/Career/men16922.github.io/public/posts/tether/` are prepared (EN/KO + real-objects image). Preserve `.serena/project.yml`, check formatting, commit/push only the three files, verify deployment and published bytes.

## Priority 4 — YouTube and Devpost (target 10-29)

- [ ] [manual] Owner reviews rebuilt `submission/tether_film.mp4` (147.85 s, 1080p, 67.9 s core-app scenes; revised export sentence uses local Samantha, rest cached). YouTube hold for A is lifted; upload PUBLIC and provide the URL. If narration feedback arrives, revise without unapproved TTS charges.
- [ ] [auto, after URL] Replace the two article placeholders and portfolio copies; add README link. Repeat `make submission` and `make presubmit` until strict gate passes. No link is invented.
- [ ] [manual] Owner verifies eligibility/terms and Token Factory key/credit through judging 12-01–12-15, then submits Devpost. Official rules checked 2026-10-12: https://nebiusglobalaihackathon.devpost.com/rules (runtime inference qualifies; public <3-minute video and ≥1-minute core-module footage for no-hardware Physical AI). Existing live-demo fallback is in DEVPOST.
- [ ] [auto] After owner publication/submission, read-only verification of the actual URL/state; no repeat publication.

## Verification boundaries

- Local gate and browser checks do not imply CI, remote publication, Cloud Run deployment, phone validation or Devpost submission.
- Newton round trip reads JSON and checks snippet constants; it does not execute arbitrary generated Python. Isaac Lab and CARLA have stand-in format tests, not execution evidence.
- One-push intervals are unavailable. Six pushes is product policy; coverage is poor/nonmonotonic and OK status does not detect shared bias. No benchmark-tuned warnings or clock/truth corrections.

## Frozen until after submission

New domains/engines/agents, tipping-aware planning, Studio 3D before/after, global i18n/JS refactor, unit/domain refactor, running Isaac Lab/CARLA for real.
