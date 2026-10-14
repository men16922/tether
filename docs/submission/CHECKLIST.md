# Submission checklist

Deadline: 2026-10-30 10:00 PDT (KST 10-31 02:00). Target: submit 10-29.

## Submission evidence (scope agreed 2026-10-14)

- [x] Use existing Newton synthetic sample videos to demonstrate tracking, calibration and the simulation/export flow; keep them labelled synthetic.
- [x] Use existing public EV-RealPhys results for real-object measurement evidence; disclose dataset camera calibration, mocap-assisted inputs and 20/45 excluded video tracks.
- [x] Independent phone + A4 filming deferred until after submission. It remains unvalidated and does not block this submission. Detailed evidence map: `docs/submission/SUBMIT.md`.

## Existing verification (dates stated per item)

- [x] App runs Nemotron 3 Super 120B on **Nebius Token Factory** (rules requirement), key in `.env` (gitignored, never committed).
- [x] `make check`: 146 tests passed on 2026-10-14 (241.05 s) via offline presubmit. Media and required files pass; two YouTube placeholders remain. Earlier fresh-clone check was 33 tests on 2026-10-05. See `docs/project/STATUS.md`.
- [x] `make demo` reproduces the recorded scenarios from a fresh clone (Newton, no LLM needed).
- [x] Live demo on Google Cloud Run: https://tether-454741001655.us-central1.run.app (`make deploy`, verified 2026-10-11: Nemotron analysis, Ask, video tracking, retraining).
- [x] Docker image builds from the repo and ran a full live run on Token Factory (actuator_gain 0.8 + camera pitch 3° → estimates 0.799 / 3.0 → 100%, 1 LLM call).
- [x] Demo film: `film/out/tether_film.mp4` (1080p, 148.93 s, 69.0 s app footage; rebuilt 2026-10-15 with the layered Studio; all narration ElevenLabs, export line generated once with owner approval). Newton synthetic app examples and public EV-RealPhys footage; cached ElevenLabs narration plus local Samantha for the revised export sentence. New filming/TTS is not required for this scope change.
- [x] README, LICENSE (Apache-2.0), Devpost draft (`docs/submission/DEVPOST.md`).
- [x] Nemotron comparison completed 2026-10-13: 35/35 cases; reported cumulative comparison cost $0.3060624 within approved $0.40. Historical overall spend ≈ $2 of $25 is not a refreshed account balance. No additional comparison calls are required.

## Needs you (outward-facing or account actions)

- [ ] Release review/authorization for the new local documentation/package edits, existing Cloud Run redeploy and portfolio commit/push. Earlier Tether changes through 8615aef are already on remote main (verified 2026-10-14).
- [ ] Upload: everything is in `submission/` (`make submission`); step by step in `docs/submission/SUBMIT.md` (YouTube public, then Devpost).
- [x] Public GitHub repo: https://github.com/men16922/tether (`.env` is not in `git ls-files`).
- [ ] Devpost: paste generated `submission/about-the-project.md`, add the video URL, repo URL and live demo URL, choose Physical AI, verify eligibility/terms and key/credit availability for judging, then submit.

## Quick re-verification before submitting

```bash
make check
make submission
make presubmit   # strict: requires real public YouTube URL in both articles
git ls-files .env   # must print nothing
```

Public demo, YouTube visibility and Devpost submission require separate live checks. Offline gates do not establish them. Any additional live-model calls require an explicit credit scope.
