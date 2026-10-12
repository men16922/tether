# Devpost draft — Tether

Status: final 2026-10-11. Numbers come from `runs/proof/*.json` (`make prove`), `runs/bench/open_newton_super_n15.json`
(Gap-Bench) and `runs/studio-demo/*.json` (recorded Studio runs with Nemotron). Demo film: `film/out/tether_film.mp4`
(2:28). Live demo: https://tether-454741001655.us-central1.run.app · Code: https://github.com/men16922/tether.
How to fill in each Devpost field: `docs/submission/SUBMIT.md`.

## Tagline

Tie your simulator to the real world: measured physics, honest intervals, and configs for NVIDIA Newton, Isaac Lab and CARLA.

## Inspiration

A policy that works 98% of the time in simulation misses in the real world because the simulator is wrong in ways
nobody wrote down: a wet section of road, an oily stretch of rail, a weaker actuator, a camera that misjudges
distance. Engineers close this gap by hand: watch failures, guess a cause, edit the simulator, retrain, repeat. Each
cycle takes days, and tuning scripts only adjust the parameters someone thought of in advance.

The same gap shows up in three industries with the same physics underneath: an object launched toward a target
slides to a stop. A robot pushing a box onto a line, a car braking to a stop line and a pusher sliding a part to an
inspection camera differ in scale and vocabulary, not in the equations. We built one tool for all three.

Tether estimates the physics gap of a pushing task from video or logs, shows where measurements are missing, and provides the next experiment and a verifiable setup.

Robot and factory pushing are the lead cases. Driving is the same simplified model, scaled; real vehicle dynamics are not validated. User comprehension has not been tested with users.

## What it does

Tether has three connected pages: an **Overview**, a **Benchmark** that tests the AI on worlds whose answer is known, and
**Studio**, where you bring your own data.

**Studio (your data → a calibrated simulator)**

1. **Pick a domain:** robot manipulation, autonomous vehicles or factory inspection.
2. **Bring data:** a phone, roadside or line-camera video (any rectangle of known size gives scale and camera pose),
   or the log your robot, car or pusher already writes. No data? Set the hidden physics yourself and **NVIDIA
   Newton** renders the video or writes the log.
3. **Measure:** the reference rectangle is found automatically (on Newton-rendered video: about 1 px clean, 3 px shaky,
   blurred and compressed); homography from it gives focal length, height and angle; tracking is parallax-corrected;
   launch speeds come from a local deceleration fit. On Newton-rendered video this is within 1 mm and 0.6%.
4. **Diagnose:** **NVIDIA Nemotron 3 Super** on **Nebius Token Factory** works as a tool-using agent. It profiles
   deceleration along the surface, checks perception, fits candidate *structures* ("uniform friction + a wet section
   from 8.5 m") and asks for the runs that would settle the rest. The language model chooses structures and
   experiments; least squares computes every number. A library search cross-checks the agent and overrules it if its
   model leaves evidence unexplained.
5. **Calibrated sim:** every value with a 90% interval (bootstrap that also redraws measurement error), friction
   painted on your own video, ghost objects replaying each run in the old and the calibrated simulator, predicted
   success before/after, and an explicit "unknown" where nothing was measured.
6. **Retrain and test:** the same learner trains a policy three ways in parallel NVIDIA Newton worlds (each world
   with its own friction, region and actuator through a per-body Warp kernel): on your current simulator, on wide
   domain randomization, and on worlds drawn from Tether's bootstrap ensemble. When the hidden world is known, each
   policy is scored there, and Newton renders the three policies acting side by side.
7. **Verify in NVIDIA Newton:** read the exported JSON, check the generated Newton constants, and execute new pushes in a separate process. With at least six usable pushes, roughly the first 80% calibrates and the rest evaluates; otherwise the output explicitly says fit replay.
8. **Export:** NVIDIA Newton materials and friction region, an Isaac Lab `EventTermCfg` whose randomization ranges
   are the measured intervals, and for driving a **CARLA 0.9.16** script (tire friction scaled by measured/simulated
   μ, a `static.trigger.friction` box on the wet section, and a braking-distance check), plus a report and JSON.

**Benchmark (how the AI is tested)** runs the full loop on hidden worlds: train a policy in Newton, measure it in a
world whose physics the agent cannot see, let Nemotron investigate, fix the simulator, retrain. Each example has a
"Run this case yourself in Studio" button that opens Studio's virtual table with the same hidden physics.
**NVIDIA Cosmos Reason 2**, running locally, watches the clips as a second opinion on whether the object slid or tipped.

## How we built it

- **NVIDIA Newton** (Warp, CPU) for physics, camera rendering (SensorTiledCamera) and the replay check. A small Warp
  kernel switches the body's friction when it crosses a region, because a seam between two surface bodies tipped
  sliding objects.
- **Three domains, one engine:** driving uses Froude similarity. Lengths ×25, speeds ×5, friction unchanged, so
  stop = v²/(2μg) holds at both scales. The fit runs at the base scale; pages and exports are full size.
- **NVIDIA Nemotron 3** on **Nebius Token Factory** with OpenAI-compatible tool calling. Super is the default; we
  benchmarked Nano, Super, Ultra and 3.5 Lightning. A chat panel ("Ask Tether") answers questions grounded in the
  visitor's own session, in English or Korean.
- **NVIDIA NeMo Agent Toolkit:** the calibration agent also runs as a NAT workflow (`nat run`, `nat serve`): NAT
  holds the LLM config and every tool call of the agent lands in NAT's event stream for profiling and tracing.
- **MuJoCo** as a second, independent engine for hidden worlds (contact-driven launch, soft contacts), so Tether is
  not only scored on data made by the model family it fits.
- **NVIDIA Cosmos Reason 2 8B** locally through llama.cpp at zero cost.
- FastAPI with Server-Sent Events, a no-build front end with one shared design system (three.js for the 3D replay),
  offline tests that replay recorded Nemotron sessions without network or credits.

## Results

**Studio examples** (hidden physics in NVIDIA Newton, revealed only after the diagnosis; recorded with Nemotron):

| Example | Found (90% interval) | Truth |
|---|---|---|
| Roadside video, braking (11 runs) | road μ 0.740 (0.720–0.750), wet from 8.60 m (8.36–8.94), wet μ 0.294 (0.283–0.303) | 0.75, 8.82 m, 0.30 |
| Vehicle log, braking (18 runs) | road μ 0.786, speed control 0.927×, wet from 9.93 m, wet μ 0.381, camera 1.3° | 0.78, 0.93×, 10.0 m, 0.38, 1.2° |
| Robot log (20 pushes) | μ 0.701, arm 0.875×, region from 0.377 m at μ 0.453, camera 2.3° | 0.70, 0.88×, 0.38 m / 0.45, 2.0° |
| Pusher log (18 strokes) | μ 0.559, pusher 0.917×, oily from 0.290 m (0.281–0.300), oil μ 0.319, camera −1.2° | 0.55, 0.92×, 0.300 m, 0.32, −1.5° |
| Short pushes only (8) | μ 0.609, arm 1.00×. Nemotron proposed a region at 0.25 m; the cross-check left it out (0.8 mm better, within noise) | 0.60; region from 0.33 m, never reached |

- 21 of the 22 hidden values in the six examples fall inside their 90% intervals; the miss is the pusher log's oily
  section, estimated to start at 0.291 m (truth 0.300 m), whose interval stops 0.1 mm short. Across 24 random hidden worlds (118 values)
  the 90% intervals contain the truth 97% of the time; before we added a 1% length-scale term for logs it was 82%. That term was tuned on these
  worlds, so we checked it on fresh ones made by a different engine (MuJoCo, error model frozen): 88% of 120 values.
  `make prove` recomputes all of this, plus the replay and retraining tables, with no network (`runs/proof/PROOF.md`).
- **Export-file verification in NVIDIA Newton:** held-out RMS is 0.6–1.45 cm at table scale; on the driving examples, 19.8–44.8 cm at full scale. The generated files are read and checked before a separate process runs the withheld pushes. This uses Newton synthetic examples; real prediction is reported separately below.
- **Retrain and test** (policy learned by trial in 16 parallel Newton worlds × 11 table points, 10 iterations; success
  in the hidden world, 24 targets):

  | Example | Current sim | Wide randomization | Tether's ranges |
  |---|---|---|---|
  | Vehicle log | 42% | 0% | **100%** |
  | Robot phone video | 0% | 13% | **100%** |
  | Robot log | 63% | 0% | **100%** |
  | Pusher log | 0% | 38% | **100%** |
  | Roadside video | 29% | 8% | **96%** |
  | Short pushes only | 0% | 25% | **46%** |

  The short log stays below 100% for an honest reason: it never measured the far table, and Studio says so before you
  train. Wide randomization trains a
  policy that is mediocre everywhere; the current simulator is confidently wrong.
- **Phone robustness** (same hidden table filmed clean vs hand-held with motion blur, exposure flicker and heavy
  compression; automatic corners, tracking and fit end to end): 11 of 11 pushes found in both; launch speed reads
  0.8% low clean and 6.5% low on the bad video; the hidden values fall inside their intervals 3 of 3 on the clean video
  and 2 of 3 on the bad one.
- **Real footage** (52 public iPhone slow-motion clips of objects sliding to a stop on six real surfaces, with
  dynamometer friction; IDPP real split, Apache-2.0; `python -m tether.eval.real_friction --download`): Tether's tracker
  follows 45 of them, and constant deceleration (the Coulomb sliding Tether fits) explains each slide with median
  R² 0.9985. The clips have no size reference and no stated slow-motion factor, so friction itself is only known up
  to one constant per object and camera: calibrated on the other surfaces, the predictions correlate with the
  dynamometer (r 0.70) but are not more accurate than guessing the mean (MAE 0.068 vs 0.058). That is the reason
  Studio asks for a sheet of known size and the frame rate.
- **A different engine makes the data** (`make cross-engine`; MuJoCo, 24 random hidden worlds per condition, the
  robot's first-day log, policies run in the hidden world, 24 targets ±3 cm):

  | Hidden world (MuJoCo) | Current sim | Best-width DR | DR over the true distribution* | Exact parameters | **Tether** (95% CI) |
  |---|---|---|---|---|---|
  | In-menu effects | 9% | 12% | 25% | 82% | **89%** (85–92) |
  | + speed-dependent friction | 10% | 12% | 26% | 58% | **83%** (75–92) |
  | + a second friction region | 10% | 13% | 25% | 85% | **83%** (76–90) |
  | + a 1.5–3° tilt | 8% | 9% | 26% | 33% | **90%** (87–93) |

  \* a DR baseline no user could build. Tether is at least as good as the best DR in 94 of 96 worlds. Held-out stops:
  1.6–2.0 cm vs 18–30 cm. The new pattern check names what the model misses instead of thresholding its size: it
  reports speed dependence in 24 of 24 worlds that have it, a change along the surface in 15 of 24 two-region
  worlds, and raises 2 false alarms on 24 in-menu worlds (the old 1 cm rule flagged 23).
- **Real objects, real video, independently measured friction** (EV-RealPhys, a public MPI benchmark: YCB objects
  pushed across a real table at 30 Hz; each object's friction measured separately with a tilted table, never shown to
  Tether):

  | Object | Tilt test | Tether, motion-capture log | Tether, RGB video |
  |---|---|---|---|
  | mug | 0.110 | 0.115 | 0.120 |
  | mustard bottle | 0.159 | 0.156 | 0.164 |
  | bleach cleanser | 0.169 | 0.159 | 0.181 |
  | pitcher | 0.220 | 0.216 | 0.229 |
  | cracker box | 0.280 | 0.208 | 0.173 |

  4 of 5 objects within ±0.05 on both paths; mean error 0.019 (log) and 0.029 (video). The cracker box misses on every path, and on real data the 90% intervals are
  too narrow (3 of 5 and 2 of 5 contain the tilt-test value). The benchmark changed Tether: the fit now reads how long
  each slide takes to stop (release segmentation and tracking can affect launch-speed estimates), and tracks that jump or run backwards are
  dropped with a note.
- **Real footage, friction law:** on the 45 tracked real slides, Coulomb sliding (Tether's model) beats a viscous
  law decisively on 35 and is the best of three laws on 36 (scale-free BIC).
- **Next experiment:** reaching 95% hidden-world success takes 5.76 runs with Tether's suggestions vs 6.84 random, the
  same as a well-designed manual sweep (5.76): the suggestions match an expert's sweep without knowing the table.

Reference only: the paper reports mean error 0.082 (median 0.025) under a **different protocol: RGB-D online tracking and filtering**; this is not a same-input baseline.

Inputs and exclusions: the video path uses the **dataset camera calibration**, a **tracking start projected from the mocap rest position**, and **object centre height from mocap**. It is not an independent phone-only test. Of 45 video tracks, 25 are retained and **20/45 excluded** (4 jumps, 8 backward tracks, 8 stopping too soon). The log path retains 45/45. No tilt-test friction enters either fit.

| Input path | Tether μ MAE (matched training) | Quadratic μ median MAE | Quadratic μ mean MAE |
|---|---|---|---|
| log | 0.019 | 0.018 | 0.019 |
| video | 0.029 | 0.037 | 0.034 |

Same common training pool, release initialisation and exclusions for all three methods. One mustard-video push has too few moving frames for a positive quadratic fit; it is excluded from ALL methods’ training for this comparison (6 of 7 usable). Full-data Tether friction estimates in the preceding table remain separate. Held-out targets stay in the evaluation; eligibility is applied to the other training pushes only. These five-object results do not establish an accuracy advantage.

| Object / path | Held-out pushes | Tether stop median / p90 (cm) | Quadratic median (cm) | Quadratic mean (cm) |
|---|---|---|---|---|
| mug / log | 10 | 11.0 / 54.5 | 13.1 / 51.8 | 13.3 / 56.7 |
| mug / video | 8 | 8.2 / 34.0 | 11.2 / 37.7 | 7.9 / 33.7 |
| mustard bottle / log | 10 | 13.0 / 40.2 | 13.7 / 55.4 | 13.3 / 57.6 |
| mustard bottle / video | 7 | 2.5 / 6.1 | 2.4 / 6.7 | 2.9 / 6.6 |
| bleach cleanser / log | 10 | 9.5 / 39.3 | 9.5 / 38.4 | 9.3 / 41.0 |
| bleach cleanser / video | 5 | 10.8 / 53.1 | 10.4 / 63.6 | 12.8 / 65.8 |
| pitcher / log | 10 | 11.2 / 25.8 | 13.2 / 28.1 | 11.9 / 25.6 |
| pitcher / video | 4 | 5.3 / 38.1 | 9.8 / 29.7 | 7.3 / 34.9 |
| cracker box / log | 5 | 26.2 / 29.7 | 25.7 / 28.8 | 25.8 / 29.5 |
| cracker box / video | 0 | not evaluable (one push) | — | — |

Leave-one-push-out: remove the held-out push first, form a common eligible training pool, select the structure and fit, then predict from the held-out measured launch speed alone. Held-out stop/track never enters training or its eligibility filter. Prediction errors are distinct from friction-estimation errors and still include launch-speed/tracking limits. No LLM calls are used.


**Gap-Bench** (Benchmark page; NVIDIA Newton, 15 hidden worlds per tier, mean hidden-world success ± 95% CI):

| Tier | Nominal sim | Domain randomization | Rule-based | System-ID baseline | Nemotron tool agent |
|---|---|---|---|---|---|
| Closed (known params) | 46% | 0% | 100% | 100% | 100% |
| Open (friction region or lens) | 39% | 6% | 83% ±9 | 100% | 100% |
| Compound (region + lens + 1) | 22% | 14% | 54% ±15 | 97% ±4 | 96% ±6 |

- Rules break once the world has an effect they have no parameter for. The agent closes those gaps for about
  $0.007 per world on Token Factory.
- We keep an honest strong baseline: system identification with a hand-ordered structure library matches the agent.
  The agent chooses from the same structure menu without a hand-set order or thresholds, ties System-ID, and uses
  5–9% more hidden-world pushes (it probes); what it adds today is the experiments it asks for and the explanation of each fix. An early 6-world run suggested the agent was ahead on compound worlds; at 15 worlds that gap
  disappeared, so we do not claim it.
- Nemotron family (open + compound, 6 worlds each): Super 100/99%, 3.5 Lightning 100/95% (cheapest), Ultra 100/83%,
  Nano 97/53%. Bigger was not better.

### Nemotron contribution: complete 35-case comparison (2026-10-13)

The last ~20% of pushes are withheld before any agent call. Offline structure search, Nemotron alone, and Nemotron plus the cross-check use the same training pushes and fitter. One recorded agent conversation is shared by the two agent conditions.

| Method | Cases | Mean case-median stop error (cm) | Mean case-p90 error (cm) | Exact fitted field-set matches |
|---|---|---|---|---|
| Offline structure search | 35 | 3.027 | 4.840 | 29/30 |
| Nemotron alone | 35 | 3.018 | 4.844 | 3/30 |
| Nemotron + cross-check | 35 | 3.018 | 4.844 | 3/30 |

Paired difference (Nemotron + cross-check minus offline): -0.0096 cm; case-bootstrap 95% interval [-0.0288, 0.0000] cm. The interval includes zero, so no stop-prediction accuracy advantage is established. Failures: 0/35; unavailable cases: 0; cross-check overrules: 0/35.

The field-set metric requires an exact match to the known fitted-variable set in 30 synthetic cases; five public-real cases have no structure label. It checks the selected free fields, not parameter-value recovery. The agent often adds lens freedom or uses a smaller last-fit field set, so similar stop error does not establish correct structure recovery. All 24 MuJoCo field sets matched for offline search and none matched exactly for the agent; Newton examples matched 5/6 and 3/6 respectively.

| Case | Offline median cm | Agent median cm | Agent + cross-check median cm |
|---|---|---|---|
| mujoco-00 | 2.56 | 2.56 | 2.56 |
| mujoco-01 | 2.33 | 2.33 | 2.33 |
| mujoco-02 | 1.31 | 1.31 | 1.31 |
| mujoco-03 | 0.95 | 0.95 | 0.95 |
| mujoco-04 | 1.54 | 1.21 | 1.21 |
| mujoco-05 | 2.11 | 2.11 | 2.11 |
| mujoco-06 | 0.88 | 0.88 | 0.88 |
| mujoco-07 | 2.45 | 2.45 | 2.45 |
| mujoco-08 | 2.21 | 2.21 | 2.21 |
| mujoco-09 | 1.29 | 1.29 | 1.29 |
| mujoco-10 | 1.67 | 1.67 | 1.67 |
| mujoco-11 | 3.31 | 3.31 | 3.31 |
| mujoco-12 | 1.13 | 1.13 | 1.13 |
| mujoco-13 | 0.27 | 0.27 | 0.27 |
| mujoco-14 | 1.35 | 1.35 | 1.35 |
| mujoco-15 | 1.75 | 1.75 | 1.75 |
| mujoco-16 | 1.75 | 1.75 | 1.75 |
| mujoco-17 | 2.03 | 2.03 | 2.03 |
| mujoco-18 | 0.17 | 0.17 | 0.17 |
| mujoco-19 | 1.91 | 1.91 | 1.91 |
| mujoco-20 | 0.27 | 0.27 | 0.27 |
| mujoco-21 | 5.27 | 5.27 | 5.27 |
| mujoco-22 | 2.06 | 2.06 | 2.06 |
| mujoco-23 | 1.31 | 1.31 | 1.31 |
| newton-brake-log | 0.04 | 0.04 | 0.04 |
| newton-flick | 0.75 | 0.75 | 0.75 |
| newton-lab-bench | 0.25 | 0.25 | 0.25 |
| newton-press-line | 0.49 | 0.49 | 0.49 |
| newton-short-reach | 0.61 | 0.61 | 0.61 |
| newton-stop-line | 0.79 | 0.79 | 0.79 |
| real-pitcher | 10.00 | 10.00 | 10.00 |
| real-mustard-bottle | 28.96 | 28.96 | 28.96 |
| real-bleach-cleanser | 12.27 | 12.27 | 12.27 |
| real-cracker-box | 7.38 | 7.38 | 7.38 |
| real-mug | 2.53 | 2.53 | 2.53 |

Data origin: 24 in-menu MuJoCo worlds, six Newton synthetic examples, and five EV-RealPhys log objects. All 35 have complete training-only fixtures; probes are queued and were not physically executed. Reported tokens × contemporaneous model API prices total $0.3060624 within the user-approved cumulative $0.40 cap; invoice/balance not verified. Full original agent latency is available for 23 fresh cases: median 14.03 s, p90 18.41 s. Nine earlier pilot cases have no retained live latency and three resumed partial cases have continuation timing only; replay timing is not live timing. No user comprehension test was performed. Responses replay offline with identical training-input hashes.

## Challenges

- **Making the LLM useful rather than decorative:** when it tuned numbers by hand it never committed. Structure from
  the LLM, numbers from the optimizer fixed that.
- **Intervals that do not lie:** our first video intervals excluded the truth because they ignored systematic camera
  error; log intervals covered only 82%. We measured coverage and fixed both.
- **One engine, three domains:** a car is not a box on a table, but braking with locked or ABS-limited wheels is
  Coulomb sliding. Froude scaling let the same Newton scene and fitter serve driving at full-size units.
- **Physics surprises:** cubes tipping at μ≈1, a seam tipping cubes (solved with a friction-switching kernel), a
  double roll that ended upright and hid a tip (solved with peak tilt).
- **Cosmos on tiny objects:** about 10 px wide; crops and per-frame questions got slid-vs-tipped to 88%, so it stays
  a second opinion.

## Limits we state plainly

- Most results use simulated data (Newton, and MuJoCo as a second engine) so the truth can be revealed. On real
  objects (EV-RealPhys) friction lands within ±0.05 for 4 of 5, with the dataset's camera calibration standing in for
  the A4 sheet; our own sheet-referenced phone recording is not in the results yet. Intervals are too narrow on real data.
- The physics is one family: launched, sliding to a stop. No grasping, steering or lane changes.
- The CARLA export was checked against CARLA 0.9.16's documented API and run against a stand-in module, not inside
  CARLA itself. GR00T is not used.

## What's next

- Real phone and vehicle data; more structures (several regions, non-linear actuators); dynamic Franka contact and
  GR00T policies trained on the calibrated, randomized simulator.

## Built with

nvidia-newton, nvidia-warp, nemotron, nebius-token-factory, nemo-agent-toolkit, cosmos-reason, mujoco, llama.cpp, three.js,
fastapi, python, openai-python, scipy, opencv. Export targets (generated, not executed here): Isaac Lab, CARLA.

## Track

Physical AI. There is no physical hardware; the video shows the application modules in action for over a minute
(Studio on the driving domain: tracking, the Nemotron agent's notebook, the calibrated simulator, the Newton replay
check and the export; Ask Tether on the live server), plus retraining in parallel NVIDIA Newton worlds and the
validation on real objects (EV-RealPhys) and on worlds from a different engine (MuJoCo).

## How it maps to the judging criteria

| Criterion | Where to look |
|---|---|
| Technical implementation | Nemotron tool agent + cross-check (also as a NeMo Agent Toolkit workflow), bootstrap intervals with measured coverage, a pattern check for what the model misses, Newton replay of the export, retraining in parallel Newton worlds scored in the hidden world, a second engine (MuJoCo) for hidden worlds, Froude-scaled driving, offline tests |
| Design | One design system on three pages; Studio in three steps (Data → Analysis → Results) with one headline number; friction painted on the visitor's own video; ghost replays; EN/KO |
| Potential impact | Same tool for robots, vehicles and production lines; exports into Newton, Isaac Lab and CARLA |
| Quality of the idea | An agent that fixes the simulator instead of the policy, and says how sure it is |


### Reliability on public real data (2026-10-12 recomputed)

| Object / path | μ error | Reliability | Error > 0.05 flagged | Interval covers tilt |
|---|---|---|---|---|
| pitcher / log | 0.004 | limited | — | yes |
| pitcher / video | 0.009 | limited | — | yes |
| mustard bottle / log | 0.003 | limited | — | yes |
| mustard bottle / video | 0.005 | limited | — | no |
| bleach cleanser / log | 0.011 | limited | — | no |
| bleach cleanser / video | 0.012 | limited | — | yes |
| cracker box / log | 0.072 | limited | yes | no |
| cracker box / video | 0.107 | unreliable | yes | unavailable |
| mug / log | 0.005 | limited | — | yes |
| mug / video | 0.011 | limited | — | no |

This is a diagnostic flag, not a validated detector of friction bias. Both >0.05-error cases receive warnings, but other accurate cases also do. Among unflagged cases: 0 evaluable, 0 covered (coverage cannot be estimated with no unflagged cases).


If the live demo is unavailable: clone the repository, install `requirements.txt`, run `make serve`, and open `/studio`. `make pages` also produces recorded standalone pages in `tether/web/dist/`. They replay recorded responses and do not establish new live-model results.


### Coverage versus push count (2026-10-12 recomputed)

| Usable pushes | Public real coverage | MuJoCo coverage |
|---|---|---|
| 1 | 1/10 | 0/24 |
| 2 | 5/9 | 0/24 |
| 4 | 7/9 | 0/24 |
| 6 | 5/6 | 14/24 |
| 8 | 3/5 | 14/24 |

Fixed, evenly spaced subsamples; 30 bootstrap draws; ten public real cases when enough pushes exist, and 24 in-menu MuJoCo worlds. The one-push row is the **pre-change diagnostic**; the product now hides that interval. Six pushes is a conservative product policy because structure search becomes available there, not proof of statistical sufficiency. Coverage remains poor and nonmonotonic; shared bias and cross-engine differences are not covered. An OK status does not mean 90% accuracy or validated coverage.


### Export-file verification on held-out Newton pushes (2026-10-12 recomputed)

| Newton sample | Fit / held-out pushes | Calibrated RMS (base cm) | Current RMS (base cm) |
|---|---|---|---|
| brake-log | 14 / 4 | 0.79 | 5.93 |
| flick | 8 / 3 | 1.45 | 31.54 |
| lab-bench | 16 / 4 | 0.60 | 2.81 |
| press-line | 14 / 4 | 1.09 | 22.80 |
| short-reach | 6 / 2 | 0.64 | 6.72 |
| stop-line | 8 / 3 | 1.79 | 17.63 |

Data origin: Newton synthetic. Roughly the first 80% calibrates; the remaining pushes are withheld. Generated JSON and Newton constants are checked, then a separate process executes the withheld launches. Base units are shown to compare samples; driving lengths displayed/exported at full scale are 25× these values. This checks file execution and prediction within the data-generating engine; public real-data prediction is a separate evaluation. Isaac Lab and CARLA are format-checked against stand-ins and were not executed here.
