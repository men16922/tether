# Next Plan

Last Updated: 2026-10-15

Only open work remains here. Completed A/B/C/D/E-tooling/F-local work and proof paths are recorded in
COMPLETED_SUMMARY and PROGRESS_LOG. Detail: `docs/project/plans/2026-10-11-feedback-hardening.md`.

The 35-case comparison and offline replay are done ($0.3060624 within approved $0.40); no more calls are needed. Owner approved Newton synthetic samples plus existing public EV-RealPhys results for submission on 2026-10-14. Independent phone filming is deferred until after submission, not completed. Remote main was verified at 8615aef on 2026-10-14; new scope/documentation changes remain local. Deployment/publication approvals and YouTube/Devpost inputs remain pending.

## Priority 1 — Release the reviewed local changes

- [ ] [manual] Authorize committing/pushing the new Tether documentation/package changes, existing Cloud Run redeploy, and portfolio commit/push separately from Token Factory credit. Earlier Tether changes through 8615aef are already on remote main; portfolio copies remain uncommitted. This scope change does not authorize external release. Portfolio `.serena/project.yml` is pre-existing WIP and must remain excluded.
- [ ] [auto, after approval] Review the scoped Tether diff, run the current release gate and credential scan, commit/push the changes; verify remote HEAD. `make deploy` archives committed HEAD, so do not deploy before the code commit. Prefer existing secret without re-upload/permission changes (`--no-secret`). Verify live pages, offline analysis and export; additional live-model calls require an explicit credit scope.
- [ ] [auto, after approval] Portfolio local copies at `/Users/men1692/Desktop/Career/men16922.github.io/public/posts/tether/` are prepared (EN/KO + real-objects image). Preserve `.serena/project.yml`, check formatting, commit/push only the three files, verify deployment and published bytes.

## Priority 2 — YouTube and Devpost (target 10-29)

- [ ] [manual] Owner reviews `submission/tether_film.mp4`, rebuilt 2026-10-15 with the layered Studio (148.93 s, 1080p, 69.0 s app footage; one ElevenLabs voice throughout, the export line generated once with owner approval; v1 backed up outside the repo). Then upload PUBLIC and provide the URL.
- [ ] [auto, after URL] Replace the two article placeholders and portfolio copies; add README link. Repeat `make submission` and `make presubmit` until strict gate passes. No link is invented.
- [ ] [manual] Owner verifies eligibility/terms and Token Factory key/credit through judging 12-01–12-15, then submits Devpost. Official rules checked 2026-10-12: https://nebiusglobalaihackathon.devpost.com/rules (runtime inference qualifies; public <3-minute video and ≥1-minute core-module footage for no-hardware Physical AI). Existing live-demo fallback is in DEVPOST.
- [ ] [auto] After owner publication/submission, read-only verification of the actual URL/state; no repeat publication.

## Verification boundaries

- Submission uses Newton synthetic samples for the application flow and existing EV-RealPhys results for real-object measurement evidence. EV-RealPhys uses dataset camera calibration and mocap-assisted tracking inputs (25/45 video tracks retained, 20 excluded). Neither source validates the independent phone + A4 workflow. Direct filming is no longer a pre-submission blocker.
- Local gate and browser checks do not imply CI, remote publication, Cloud Run deployment, phone validation or Devpost submission.
- Newton round trip reads JSON and checks snippet constants; it does not execute arbitrary generated Python. Isaac Lab and CARLA have stand-in format tests, not execution evidence.
- One-push intervals are unavailable. Six pushes is product policy; coverage is poor/nonmonotonic and OK status does not detect shared bias. No benchmark-tuned warnings or clock/truth corrections.

## Optional user comprehension check

- [ ] [manual, optional] 3–5 first-time users interpret a result and choose an experiment. Currently explicitly not tested with users.

## After submission — Independent phone validation

- [ ] [manual, deferred] Film ≥1 object–surface pair, ideally 3, with phone + A4 and independent kinetic tilt angle. 15 retained flicks/pair: first 10 calibrate, remaining 5 evaluate; small design, not statistical sufficiency. Place files and truth.json in gitignored `film/real/`. Existing October 10 clips lack independent truth. Guide: `docs/guide/06_실제_영상_촬영법.md`.
- [ ] [auto, after files arrive] `make prove-real`: held-out stop median/p90, predictive coverage, rejection reasons, tilt comparison and export round trip. Keep unvalidated until independent recordings and truth exist.

## Frozen until after submission

New domains/engines/agents, tipping-aware planning, Studio 3D before/after, global i18n/JS refactor, unit/domain refactor, running Isaac Lab/CARLA for real.
