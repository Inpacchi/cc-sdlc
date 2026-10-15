---
type: handoff
slug: ci-tier-gpu-comparison
created: 2026-10-15
status: pending
trigger: deferred-work
recommended_next_skill: direct-dispatch
source_session_summary: "The factory CI tier's first real browser suites needed 24 CPUs a job, because Chromium renders WebGL in software. CD asked whether a GPU would help, or a dedicated PC; the measurement to answer it was designed, then parked by CD (2026-10-15) until after the v2.1.0 release and the incubator's migration"
active_deliverable: null
related_files:
  - bundles/factory/tree/host/ci_launcher.py
  - bundles/factory/tree/host/setup-ci.sh
  - process/factory.md
  - process/sdlc_changelog.md
---

# Would a GPU make the CI tier's browser jobs cheaper?

## Why this is a handoff

The pilot project's browser (Playwright, Chromium) end-to-end suites on the factory CI tier timed out at 8 and 16 CPUs and passed only at 24. Chromium in a container renders WebGL in software (SwiftShader) and wants about 7 CPUs a browser. The pilot project now runs one CI job at a time with 24 CPUs (`CI_RUNNERS=1`, `CI_JOB_CPUS=24`), which leaves its runner host room for little else. The host has GPUs.

CD asked (2026-10-15) whether a GPU would help, or whether CI belongs on a dedicated PC. The session's answer:
- **A GPU** would probably help speed, but it's risky on this tier: a pull request's code would get the GPU.
- **A dedicated PC** isn't needed for speed, but would help isolation.

CD parked the measurement that settles it (2026-10-15) until after z-sdlc v2.1.0 and the incubator's move to it. That session was about the release, so nothing here was started.

## What needs to happen

**1. Measure before deciding anything.** This uses trusted code only, and stays outside the CI tier: no runner registers, and no pull request's code runs.
- **What runs:** the pilot project's two browser suites (front door, and exemplars), from its default branch at one pinned commit.
- **Where:** a debug container built from the CI tier's job image, with the same limits as a CI job (`--memory`, `--pids-limit`, `--shm-size 4g`, the seccomp profile, `no-new-privileges`).
- **The variants:**
  - **A, no GPU (today):** `--cpus 24`. It should reproduce today's times: about 31.7 min for front door (30 passed, 3 skipped) and 10.7 min for exemplars (32 passed).
  - **B, one GPU:** one GPU passed through (`--gpus device=0`, or the device nodes), with Chromium told to use it, at `--cpus 24`.
  - **C, B at less CPU:** B again at `--cpus 8` and at `--cpus 12`. This is the real payoff: if a job passes at 8–12 CPUs with a GPU, the host can run two slots instead of one.
- **For each run, record:**
  - wall time per suite;
  - pass and fail counts against variant A's;
  - the share of throttled CPU periods (`cpu.stat`'s `nr_throttled` over `nr_periods`);
  - GPU use (`nvidia-smi dmon`).
- **Repetitions:** three runs of each, since browser suites flake.

**2. Bring the numbers to CD with a recommendation.**
- **Thresholds, as a starting point:** a GPU is worth it if C passes at 12 CPUs or fewer, or if B cuts wall time by 30% or more. Otherwise, stay on CPU.
- **CD's decision:** whether a pull request's code may touch a GPU at all. If it may, a GPU option for the CI tier is a z-sdlc change, planned and reviewed like the CI tier itself:
  - a `CI_JOB_GPUS` setting;
  - the device in `job_flags()`;
  - the NVIDIA container toolkit for the runner user's rootless Docker, in `setup-ci.sh`;
  - the isolation check proving each slot sees only its own GPU;
  - Enablement step 10.

## Evidence

- **Code locations:**
  - `bundles/factory/tree/host/ci_launcher.py:328`, `job_flags()`: every flag a job container gets (CPU, memory, PIDs, shm, `no-new-privileges`, seccomp). A GPU would be one more.
  - `bundles/factory/tree/host/setup-ci.sh`: builds the job image and the runner user's rootless Docker. A GPU needs the container toolkit there.
- **Docs:** `process/factory.md` Enablement step 10, "Browser suites need more than their test count suggests" (the 7-CPUs-a-browser finding, `/dev/shm`, fonts).
- **Recorded measurements:** `process/sdlc_changelog.md`, "The CI tier, review round 3; the runner audit", item 14 ("What the first real e2e runs needed"):
  - `--cpus 8`: throttled in 75–80% of periods, failed;
  - pinned to 8 CPUs with no quota: no throttling, but only about 4 CPUs used, failed;
  - `--cpus 16`: failed;
  - `--cpus 24`, with Chromium on a 4 GB `/dev/shm` and fonts: 32/32 in 10.0 minutes, matching the uncapped runner.
- **The tier, green:** the pilot project's settings are `CI_RUNNERS=1`, `CI_JOB_CPUS=24`, `CI_CPU_QUOTA=2600%`, `CI_JOB_SHM=4g`, `CI_MEMORY_HIGH=10G`, `CI_MEMORY_MAX=12G`. Its default-branch run 38715604437 (attempt 2, 2026-10-15) took 31.7 min for front door (30 passed, 3 skipped) and 10.7 min for exemplars (32 passed), with 0.7% of CPU periods throttled.
- **Ruled out:** per-slot CPU pinning. It removed throttling but not the shortage, and was dropped.

## Recommended next step

Open a new session, with access to the runner host and the pilot project's checkout, and run the measurement as **direct dispatch**, with this file as the seed.

Reasoning: the experiment's design is settled, and it changes nothing on the tier, so it needs no plan. Its result feeds a CD decision. Only if that decision is yes does a GPU option become z-sdlc work, and then it goes through `sdlc-lite-plan` and a review like the CI tier's.

## Open questions

- **Driver and toolkit:** does the runner host have a working NVIDIA driver (`nvidia-smi`), and can the runner user's rootless Docker use the NVIDIA container toolkit? Installing it needs CD's sudo.
- **Chromium's flags:** which flags make headless Chromium in this image use the GPU, rather than fall back to SwiftShader? `chrome://gpu` in the debug container, or `--enable-logging`, shows which renderer it got.
- **Other users of the GPUs:** do the host's GPUs have other users, and would a CI job's GPU use slow them?
- **Isolation, if a GPU is ever given to pull requests' code:**
  - the driver's attack surface (its ioctls) from inside a job;
  - what one job leaves in GPU memory for the next;
  - one GPU per slot, never shared;
  - whether a dedicated CI machine is the better answer for isolation anyway.

## Out of scope (do NOT pursue)

- **Changing the CI tier's settings, or the pilot project's CI, during the measurement:** the measurement uses a debug container only.
- **GPU use by the strict or planning tiers:** they run agents, not browsers.
- **Buying or setting up a dedicated CI machine.** That's CD's call after the numbers.
