# Agent Brief

Last Updated: 2026-10-14

> ▶ NEXT SESSION: Submission uses existing Newton synthetic sample videos + public EV-RealPhys results; independent phone + A4 validation is deferred until after submission, not completed. Read `docs/project/NEXT_PLAN.md` Priority 1: review the local scope/package changes, then obtain release authorization for commit/push, existing Cloud Run redeploy and portfolio publication. Remote main was verified at 8615aef on 2026-10-14. No more Nemotron calls or new filming needed before submission. Public YouTube URL and Devpost owner checks/submission remain pending. Evidence and limitations: docs/submission/SUBMIT.md.

## Snapshot

Tether (Nebius × NVIDIA Global AI Hackathon, Physical AI track): an agent closes the Sim2Real gap — measurements in a hidden-physics "real" Newton world, including open-world faults (friction strip, lens) → Nemotron 3 Super tool agent (look, fit, probe, commit) on Token Factory → new sim config → retrain → re-measure; Cosmos Reason 2 (local) as a second opinion on tipping. Near-zero cost, no hardware: local Mac + NVIDIA Newton + Token Factory (~$2 of $25 spent). Deadline 2026-10-30 10:00 PDT (KST 10-31 02:00); submit 10-29. 

## Active Work

0. Release the reviewed local scope/package changes, update the existing Cloud Run service and portfolio after authorization. Submission evidence: Newton synthetic samples + public EV-RealPhys; direct phone filming is deferred.

Authority: `docs/project/NEXT_PLAN.md`.

1. Owner reviews/uploads the existing film to public YouTube; add its URL, rerun strict presubmit, then owner completes Devpost. Guide: `docs/submission/SUBMIT.md`. Studio samples: `tether/studio/samples/` (Newton-rendered, truth JSON beside each); new features remain frozen through submission.

## Read Order

1. Current State: `docs/project/STATUS.md`
2. Next Work: `docs/project/NEXT_PLAN.md`
3. Decisions: `docs/project/DECISIONS.md`
4. Recent Log: `docs/project/PROGRESS_LOG.md`

## Commands

- Verification Gate: `make check`  (offline; py_compile + pytest via .venv)
- Tier 0 table: `.venv/bin/python -m tether.eval.compare --worlds 10`
- Gap-Bench: `.venv/bin/python -m tether.eval.open_bench --worlds 6 [--env newton] [--llm tokenfactory]`
- Open scenarios: `.venv/bin/python -m tether.eval.record_demo --open-only --llm tokenfactory`
- Studio: `make serve` → http://localhost:8000/studio; CLI `python -m tether.studio calibrate LOG.csv | video CLIP.mp4 --corners ...`; `make studio-samples`, `make studio-record`, `make studio-bench`
- Demo + dashboard: `make demo` → `tether/web/dist/benchmark.standalone.html` (artifact: https://claude.ai/artifact/WVBNfVMAzeNg71kDSFqYAf)

## Guardrails

- Success rates are always measured by rollout, never LLM-estimated. The agent never reads hidden params (only `RealWorld.rollout`).
- No spending: no paid cloud/GPU/hardware without explicit user approval. Token Factory calls cost credits — never inside `make check`; use mocks/recorded fixtures.
- Secrets only via env vars (`NEBIUS_API_KEY`); never commit keys.
