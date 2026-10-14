# Plan: a Studio that non-experts can use (draft, 2026-10-15)

Status (2026-10-15, later the same day): owner asked for the full UX overhaul now ("hackathon-winning impact version"), overriding the pre/post-submission split below. Studio slice implemented locally, uncommitted, not deployed:
- Three-step bar (Choose data → What we found → Use it) replaces the left sidebar; examples and simulated data are tracked (pre-placed corners) and analysed automatically behind a four-stage "working" screen with the visitor's video beside it. Uploaded videos still open "How we measured" first.
- The summary leads with a plain-language headline and findings built from the calibration (e.g. "The table is 31% slipperier than your simulator assumes"), before/after success, reliability chip, a hidden-answer check per value, one primary action (export) and the next experiment; four "Go deeper" topic views (How we measured, The AI's notebook, Every number, Retrain test).
- Export: pick the target tool first, then download; code preview folded; the Newton check follows.
- Overview: primary CTA opens an example directly. Benchmark: first look shows the four open-world cases, the benchmarks and "Stump the agent"; rule-solvable cases and the visitor's own worlds fold under "More cases" (unfold when selected). Benchmark top now leads with three numbers read from the recorded Gap-Bench hardest tier (22% → 96% with the agent, rules 54%, $0.0066 per world) plus the System ID honest note (97%) and a link into Gap-Bench; the case views below are unchanged.
- film/footage.py studio_plan rewritten for the new flow (same mark names); recorded once into scratch (62.2 s, 1498 frames, headless Chrome 1440×810): run screen, summary with ghost video, hidden-answer check, Every number, Retrain, CARLA export + Newton check all render. Existing film/out footage and the submitted film were not touched.
- Verified: make check 146 passed; live server (TETHER_LLM=none, no paid calls) robot-log, phone-video, simulated video + "run these pushes in Newton" second take; recorded standalone flick sample; KO copy; 390 px width without horizontal scroll. Real upload verified on the live server: an uploaded copy of the phone sample opens How we measured with auto-found corners; Track → analysis → summary in 8.9 s; the topic bar links back. Not verified: user comprehension (no users tested).
- Impact: the submitted film (147.85 s) shows the old Studio; film/footage.py selectors (#to-res, #track, #to-x → retrain) target the old flow and need updating before any re-record.

## 1. Problem (from the code, not from user tests)

- `tether/web/studio.html` (1,922 lines) has six panels (data, measure, diagnose, results, retrain, export), a phase nav, a view-tab bar, three input modes, domain tabs, a floating Ask chat, and a verify box. The first screen already offers three ways in plus a "30 seconds" explainer.
- Vocabulary is expert-only: "sysID", "bootstrap 90% interval", "ghost boxes", "EventTermCfg", "μ", "predictive vs parameter band".
- No user has tried it (NEXT_PLAN: comprehension check is "explicitly not tested"). Every item below is a hypothesis until 3-5 people test it.

## 2. Design principles (with sources)

1. One question per screen, one primary button. Matches the owner's "one focus per screen" rule.
2. Show the whole path up front, 3-6 steps, allow going back (Singapore GovTech stepper guidance, Lollypop, Visa wizard pattern: https://design.visa.com/patterns/wizard, https://www.designsystem.tech.gov.sg/components/stepper). Use a stepper only for the guided path; keep Benchmark/Overview as tabs.
3. Progressive disclosure, at most two levels: answer first, numbers one click away, never removed (Nielsen via https://concepts.dsebastien.net/concept/progressive-disclosure/, https://app.uxcel.com/glossary/progressive-disclosure).
4. Uncertainty: do not rely on words like "likely" (people read them as 0.5-0.99) and do not rely on bare interval bars (viewers read them as a fixed value). Use a plain sentence with a range ("friction is about 0.55, probably between 0.50 and 0.60") plus one picture that shows spread, e.g. an ensemble of sample outcomes (Joslyn & Savelli 2021, https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2020.590232/full; van der Bles et al., https://arxiv.org/pdf/2011.07586; overview https://ehudreiter.com/2024/02/13/communicating-uncertainty-to-non-experts/).
5. Keep the NVIDIA-grounded look in `docs/design/REFERENCE.md` (near-black, `#76B900` as the single accent, square corners, no logo). Legibility fix needed, not a restyle: body copy size and Korean line length.

Source caveat: the searches returned general UX guidance, no NVIDIA design-system documentation and no scientific-dashboard studies; the application to Tether is inference.

## 3. Proposed information architecture (owner direction 2026-10-15)

Owner direction: "Easy to learn, hard to master". The first screen is simple enough for the general public; engineers get depth by entering a feature or topic page. Never pile everything into one place: each page carries one topic, and detail lives on the page whose topic it is.

Three depth layers, each on its own surface:

| Layer | Who | What they see | Where |
|---|---|---|---|
| L1 Try | anyone | one sentence, one picture, one button | Home and the Studio guided path |
| L2 Understand | curious user | why, in plain words; one chart per question | topic pages, reached by a "Why?" / "See how" link from L1 |
| L3 Master | engineer | numbers, intervals, reliability flags, agent log, configs, JSON | the same topic page, an "Engineer view" section below the plain one, or its own sub-page |

Page map (each page = one topic):

| Page | L1 (simple) | Detail it owns (L2/L3) | Comes from today |
|---|---|---|---|
| Home `/` | "Make your simulator match your real table." One button: Try a sample. Three field cards. | none: no result numbers on Home | overview.html (remove the Results block) |
| Studio `/studio` | 3 steps: show the table → what we found (one verdict sentence + before/after video) → take it with you | none: each step links out to its topic page | studio.html panels data/measure/results/export, slimmed |
| Measurement `/studio/measure` | how the video became pushes | A4 calibration, tracking, push segmentation, re-place corners | p-measure |
| Diagnosis `/studio/diagnosis` | what differs, in words | agent notebook, cross-check, hypotheses, what-if worlds, intervals, reliability | p-diag + technical half of p-results |
| Retrain `/studio/retrain` | "the robot now stops where it should" | policy comparison lanes, Newton replay | p-train |
| Export `/studio/export` | pick your tool, download | Newton / Isaac Lab / Markdown / JSON, verify box, round-trip check | p-export |
| Evidence `/benchmark` | "We test the AI on worlds where we know the answer" | Gap-Bench, Nemotron comparison, real objects (EV-RealPhys), limits | benchmark.html, split into Benchmark and Real objects sections or sub-pages |

Rules for every page: one primary button, at most one chart above the fold, technical terms only in L3 or with a tooltip, Korean in natural 합니다체. The Ask chat stays as a docked help button with three suggested questions per page.

Uncertainty on L1/L2 is a plain range sentence; the interval/ensemble chart lives in L3 of Diagnosis.

## 4. Work plan

A. Research and baseline (0.5 day, no cost)
 - Screenshot every Studio state in Chrome (EN and KO); list every term a non-expert would not know (glossary table).
 - Heuristic review against the principles above; record in `runs/qa/ux-baseline-2026-10-15.md`.
B. Pre-submission slice (1 day, copy and layout only, risk-limited)
 - Rewrite headings/CTAs into task language (EN + natural 합니다체 KO); glossary tooltips for μ, interval, sysID.
 - Put the plain-language verdict above the numbers on the results panel; move technical tables lower, under an "Engineer view" heading (full split into topic pages waits for C).
 - Re-run `make check` and the browser check; re-record only if film footage changes (it must not: film bytes are frozen).
C. Post-submission redesign (3-5 days)
 - Low-fidelity wireframes (HTML, no JS) for Home, the Studio 3-step path and one topic page (Diagnosis) → owner picks → build over the existing API (`/api/studio/*` unchanged; the session state carries across topic pages).
 - Move each Studio panel to its topic page; Studio keeps only the guided path with "See how" links. Remove result numbers from Home.
 - Replace tabs/phase nav with the 3-step stepper; mobile-first layout for phone users who film the table.
 - Ensemble-outcome picture for uncertainty in Diagnosis L3.
D. Test (1 day)
 - 3-5 first-time users, think-aloud, task: "calibrate the sample and export it". Metrics: task completion, time to first export, which words they stumble on. Report honestly as a small qualitative check.

## 5. Decisions

- Decided 2026-10-15: target is the general public first, engineers deeper (layered pages above); Home stays simple, details split by topic page.
- Open: do slice B before the 10-29 submission, or leave all UI untouched until after (the film shows the current UI)? Recommended: after submission, except copy fixes that do not change what the film shows.

## New-UI film (2026-10-15, local only)

- film/out/footage/studio re-recorded with the new flow (previous footage backed up in the session scratchpad); the Ask clip is unchanged (needs paid live calls to redo).
- film/stage.html zoom frames moved to the centred layout (x 100, width 1240).
- `TETHER_TTS_CACHE_ONLY=1 python -m film.render --voice cache-or-local --out film/out/tether_film_v2.mp4`: 147.9 s, 1920×1080, 48.6 MB; same scene lengths and narration as the submitted film (export line in local Samantha as before); no paid TTS.
- submission/tether_film.mp4 is untouched. Replacing it, rebuilding `make submission`, and uploading to YouTube are owner decisions.

