# Progress Log

Last Updated: 2026-10-15

This file maintains only recent incremental summaries (newest 3-5 items, ≤120 lines). Older entries are archived to `docs/project/archive/progress-YYYY-MM.md` via `/tidy-docs`.

## 2026-10-15 — Layered Studio UX ("easy to learn, hard to master")
- Status: owner asked for the full UX overhaul before submission; implemented locally, uncommitted, not deployed. No paid calls (server ran with TETHER_LLM=none).
- Changed: Studio three-step bar; examples/simulated data tracked and analysed automatically behind a plain four-stage screen; plain-language summary (findings from the calibration, before/after success, hidden-answer check, one export action, next experiment) with four "Go deeper" topic views; export picks the tool first. Overview CTA opens an example; Benchmark leads with three Gap-Bench numbers and folds rule-solvable/own cases; Ask guide and film/footage.py updated to the new flow.
- Verified: make check 146 passed; live robot-log, phone-video, uploaded video (measure → analysis → summary), simulated video + second Newton take, standalone recorded sample, KO copy, 390 px width; footage script recorded once into scratch; Benchmark score cards match recorded Gap-Bench numbers. Not verified: user comprehension.
- Film: new-UI cut rendered locally at film/out/tether_film_v2.mp4 (147.9 s, cached/local narration, no paid TTS); submission/tether_film.mp4 untouched. Commits 8b79a42, c8cdd27 local only.
- Next: owner review of the new UI and film v2; decide whether v2 replaces the submitted film; push/deploy need approval. Detail: docs/project/plans/2026-10-15-ux-redesign.md.

## 2026-10-14 — Submission uses existing samples and public real-object evidence
- Status: owner approved Newton synthetic sample videos + existing EV-RealPhys results; independent phone + A4 validation remains unperformed and moves to after submission. No new paid calls or external release.
- Changed: plan/brief/status/decision, owner guides, README, Devpost, EN/KO articles and local portfolio copies; YouTube description generator and submission package. Historical proof marked as superseded for current real-object claims. Older progress preserved in docs/project/archive/progress-2026-10.md; newest five increments retained here.
- Verified: make submission; offline presubmit with --allow-pending ran make check, 146 passed (241.05 s); media/required files pass, strict readiness still awaits two YouTube URLs. Generated About/SUBMIT match sources, film bytes unchanged, synthetic labels/results checked; portfolio Prettier/diff checks and credential-pattern scan pass. All older progress entries preserved. No new physical, browser or live-model verification.
- Blockers: release authorization for new local edits, existing Cloud Run/portfolio; public YouTube URL and Devpost owner checks/submission. Earlier Tether changes through 8615aef verified on remote main; direct filming no longer blocks submission.
- Next: NEXT_PLAN Priority 1 release review; Priority 2 YouTube URL → regenerate/strict presubmit → Devpost. Preserve portfolio .serena/project.yml WIP.
- Evidence: runs/qa/submission-scope-2026-10-14.json; runs/proof/presubmit.json; docs/submission/SUBMIT.md. Existing real_benchmark/proof numeric results reused, not recomputed as a new experiment.

## 2026-10-13 — Nemotron completed; local ship/readiness retained
- Status: 35/35 Nemotron cases complete and replay-verified; ship d982276 exists; this local ship records the 17-file readiness/Nemotron follow-up, leaving generated outputs and portfolio WIP out. No push/deploy/publication; paid work stayed within the user-approved cumulative $0.40.
- Changed: 26 remaining cases completed; canonical proof, recorded responses/ledger, complete-vs-continuation timing, README/DEVPOST/EN/KO articles and local portfolio copies updated. Devpost comparison moved inside the generated About body; submission rebuilt. Original nine response files unchanged.
- Verified: ship reran make check: 146 passed (265.56 s); offline 35-case replay matched scores within 1e-8 and summary/timing exactly; 224 response token totals match $0.3060624 ledger, unknown reserve zero. Docs-number checks, diff/credential scan and budgets passed. Strict presubmit still has two owner YouTube placeholders; media/files valid.
- Results: mean case-median stop error offline 3.027 / agent 3.018 / cross-check 3.018 cm; difference -0.0096, case-bootstrap 95% [-0.0288, 0.0000]. No accuracy advantage; exact fitted field sets 29/30 vs 3/30, a free-variable proxy. Zero failures/overrules. Fresh-case live timing n=23 (median 14.03 s, p90 18.41 s); nine old timings absent, three continuations separate. Invoice/balance and user comprehension unverified.
- Prior readiness: 145 tests; isolated NAT replay 1 passed, archived-source checks 15 passed, deployment-source pages/browser/held-out Newton verified; URL parser, 165-character pitch and mixed narration credit corrected. These earlier checks are not new live/deployment evidence.
- Blockers: owner filming + truth.json; Tether push/Cloud Run/portfolio approval; public YouTube URL and Devpost owner checks/submission. Next: NEXT_PLAN Priority 1; preserve portfolio .serena/project.yml WIP.
- Evidence: runs/proof/agent_ablation.json; runs/qa/nemotron-completion-2026-10-13.json and residual-readiness-2026-10-13.json; detail: docs/project/plans/2026-10-11-feedback-hardening.md. Raw responses, credit ledger and generated QA outputs remain local/untracked.

## 2026-10-12 — Claims, reliability and exported-file evidence
- Status: A/B/C and E tooling/F local updates complete; publication, independent filming and full D comparison pending.
- Changed: real benchmark baselines/LOPO/inputs/exclusions; reliability status (single-push intervals hidden), predictive bands; Isaac pair ranges; JSON ensemble/base; AST+separate-process Newton round trip and held-out verify; global friction-patch coordinates preserved for negative starts; phone split/rejection tooling; ablation fixtures/credit ledger; presubmit; EN/KO docs and recorded examples; portfolio local copies.
- Verified: final make presubmit ran make check: 144 passed in 234.65 s; media/required files passed, strict failure only on two YouTube placeholders; EN/KO 1440/390 px live local workflow/export/refresh, no overflow or JS errors; robot/driving file round-trip tests; credential scan/diff checks. Optional NAT tests skipped (nat unavailable).
- Evidence: matched-comparison training now excludes the same one short video push for all methods; held-out targets remain evaluated. `--from-recorded-sessions` reproducibly refits saved inputs. Real log μ MAE 0.019 vs median baseline 0.018; video 0.029 vs 0.037. Video retains 25/45 (20 excluded). Single cracker interval unavailable. All 10 real cases flagged; unflagged coverage not estimable. Sweep at n=6 MuJoCo 14/24, not a guarantee. Diagnosis: source Appendix C.3 uneven cardboard/anisotropic contact is consistent with low-scatter mocap bias; tilt ≤1.798°, clock corrected only in wording (source synchronized 30 Hz), no parameter/truth correction.
- D: 9/35 complete, 0 cross-check overrules; token×price $0.0963855 ≤$0.10; 26 incomplete/missing. Expanded cumulative $0.40 approval pending; ledger and training-input hashes preserved, no fake agent scores. Original pilot latency unavailable.
- Film: rebuilt 147.85 s, 67.9 s app footage; cached narration except revised export sentence via local Samantha (no paid TTS); submission regenerated. Portfolio copies uncommitted, not republished.
- Blockers: additional D credit decision; owner phone filming; explicit Git/Cloud Run/portfolio release approval; YouTube URL/Devpost and judging-key check.
- Next: resolve D credit scope, then NEXT_PLAN Priority 2–4. Tether/portfolio changes remain uncommitted.

## 2026-10-11 — Next plan from FEEDBACK.md (plan only, no code)
- Status: plan written; nothing implemented. Waiting on the owner's answers (YouTube timing, filming, one Token Factory run).
- Changed: `docs/project/NEXT_PLAN.md` (Priority 1 A–G, calendar, Frozen list), `docs/project/plans/2026-10-11-feedback-hardening.md` (code-checked findings, designs, risks). `FEEDBACK.md` added (untracked).
- Verified: external review claims A/B/C checked against code and `runs/proof/real_benchmark.json` (all true); extra findings: 20 of 45 video tracks excluded, `verify` replays the fit's own pushes, film footer quotes the paper's 0.082. `make lint` OK; `make check` not run (docs only).
- Blockers: owner decisions (hold YouTube upload until A is done; filming 10-17/18; ~$0.1 Token Factory run; portfolio push).
- Next: start A (`real_benchmark.py` baselines + leave-one-push-out, move 0.082 to a reference line, re-render film).

## 2026-10-11 — Tech article (EN/KO) published on the portfolio
- Status: done; waiting on the owner's YouTube upload.
- Changed: `docs/article/tether.{en,ko}.md` (+ `img/`, served from GitHub raw); published on https://men16922.github.io as `/articles/tether` and `/kr/articles/tether` (portfolio repo commits bc0c40c, 292223e: new "Portfolio" tab, `ArticlePost` page rendering `public/posts/<slug>/<lang>.md` with marked; `.gitattributes` now marks jpg etc. binary after JPGs were line-ending converted). Devpost replay numbers corrected (4-8 mm table scale, 18-27 cm driving).
- Verified: live `.md` files 200, live image hashes equal the originals, `make check` 122 passed (earlier this day), Prettier check passed on the portfolio.
- Blockers: none; YouTube upload and Devpost submission are the owner's.
- Next: add the YouTube link to both articles (repo + portfolio) once the owner sends it; optionally a Tether card in the portfolio Projects section.
