# Performance Lab Demo Scenario

A scripted series of 20 commits per application that tells a realistic development story.
Each commit specifies the mean CPU (%), Memory (MB), and Execution Time (s) per workflow.
Std dev is auto-computed as 10% of the mean.

**Regression detection uses z-scores (window of 20 points, min 5):**
- |z| >= 3.0 → **strong** regression
- |z| >= 2.0 → **possible** regression

---

## Final Cut Pro (mock_final_cut)

Baseline defaults: Import(CPU 40, Mem 900, Time 3.0) | Edit(CPU 55, Mem 1200, Time 2.0) | Export(CPU 75, Mem 1500, Time 8.0)

| # | Commit Message | Importing Video | Editing Video | Exporting Video | Notes |
|---|---|---|---|---|---|
| 1 | Initial benchmark baseline | 40 / 900 / 3.0 | 55 / 1200 / 2.0 | 75 / 1500 / 8.0 | Establish baseline |
| 2 | Add ProRes RAW codec support | 42 / 920 / 3.1 | 55 / 1200 / 2.0 | 75 / 1500 / 8.0 | Slight import increase |
| 3 | Optimize media thumbnail generation | 38 / 880 / 2.8 | 55 / 1200 / 2.0 | 75 / 1500 / 8.0 | Import improves |
| 4 | Refactor timeline rendering engine | 40 / 900 / 3.0 | 52 / 1150 / 1.9 | 75 / 1500 / 8.0 | Edit slightly faster |
| 5 | Add multicam sync detection | 43 / 950 / 3.2 | 55 / 1200 / 2.0 | 75 / 1500 / 8.0 | Import a bit heavier |
| 6 | Enable GPU-accelerated transitions | 40 / 900 / 3.0 | 48 / 1100 / 1.7 | 70 / 1400 / 7.5 | Edit + Export improve |
| 7 | Update color grading LUT pipeline | 40 / 900 / 3.0 | 54 / 1200 / 2.0 | 73 / 1480 / 7.8 | Minor export change |
| 8 | Fix memory leak in clip browser | 39 / 860 / 2.9 | 53 / 1100 / 1.9 | 74 / 1450 / 7.8 | Memory improves |
| 9 | Add spatial audio import support | 41 / 910 / 3.0 | 55 / 1200 / 2.0 | 75 / 1500 / 8.0 | Back to normal |
| 10 | Parallelize background rendering | 40 / 900 / 3.0 | 50 / 1150 / 1.8 | 68 / 1350 / 7.0 | Export noticeably faster |
| 11 | Optimize XML project parser | 38 / 870 / 2.7 | 50 / 1150 / 1.8 | 68 / 1350 / 7.0 | Import improves |
| 12 | Add HEVC hardware decode path | 37 / 850 / 2.6 | 50 / 1150 / 1.8 | 68 / 1350 / 7.0 | Import keeps improving |
| 13 | Refactor audio waveform cache | 40 / 900 / 3.0 | 49 / 1130 / 1.8 | 68 / 1350 / 7.0 | Stable |
| 14 | Add 8K timeline support | 40 / 900 / 3.0 | 53 / 1250 / 2.0 | 72 / 1450 / 7.5 | Edit/Export slightly heavier |
| 15 | Enable Smart Conform auto-crop | 40 / 900 / 3.0 | 51 / 1200 / 1.9 | 70 / 1400 / 7.2 | Settles down |
| 16 | Upgrade motion templates engine | 40 / 900 / 3.0 | 52 / 1200 / 1.9 | 70 / 1400 / 7.2 | Stable |
| 17 | Add AI scene detection for imports | 58 / 1300 / 4.8 | 52 / 1200 / 1.9 | 70 / 1400 / 7.2 | **STRONG regression on Import** — CPU +45%, Mem +44%, Time +60% |
| 18 | Optimize AI model batch inference | 46 / 1000 / 3.5 | 52 / 1200 / 1.9 | 70 / 1400 / 7.2 | Partial fix — still elevated |
| 19 | Switch to on-demand scene detection | 40 / 900 / 3.0 | 52 / 1200 / 1.9 | 85 / 1800 / 12.0 | Import fixed but **STRONG regression on Export** — new export pipeline bug |
| 20 | Hotfix: revert export pipeline change | 40 / 900 / 3.0 | 52 / 1200 / 1.9 | 70 / 1400 / 7.2 | Export recovered |

**Story:** Steady optimization through commits 1-16. Commit 17 introduces AI scene detection that hammers import performance. Commits 18-19 try to fix it — 18 partially, 19 fixes import but accidentally breaks export. Commit 20 hotfixes export.

---

## Logic Pro (mock_logic_pro)

Baseline defaults: Load(CPU 35, Mem 600, Time 2.5) | Playback(CPU 50, Mem 800, Time 1.0) | Bounce(CPU 65, Mem 700, Time 5.0)

| # | Commit Message | Loading Project | Real-Time Playback | Bouncing Final Mix | Notes |
|---|---|---|---|---|---|
| 1 | Initial benchmark baseline | 35 / 600 / 2.5 | 50 / 800 / 1.0 | 65 / 700 / 5.0 | Establish baseline |
| 2 | Add ARA2 plugin bridge layer | 36 / 620 / 2.6 | 51 / 810 / 1.0 | 65 / 700 / 5.0 | Minor load increase |
| 3 | Optimize sample library indexing | 33 / 570 / 2.3 | 50 / 800 / 1.0 | 65 / 700 / 5.0 | Load improves |
| 4 | Refactor audio engine thread pool | 35 / 600 / 2.5 | 46 / 770 / 0.9 | 62 / 680 / 4.7 | Playback + Bounce improve |
| 5 | Add MIDI 2.0 protocol support | 35 / 600 / 2.5 | 50 / 800 / 1.0 | 65 / 700 / 5.0 | Back to normal |
| 6 | Enable multi-threaded plugin scanning | 32 / 560 / 2.2 | 50 / 800 / 1.0 | 65 / 700 / 5.0 | Load faster |
| 7 | Add Dolby Atmos spatial panner | 35 / 600 / 2.5 | 52 / 830 / 1.1 | 67 / 720 / 5.2 | Playback + Bounce slightly heavier |
| 8 | Optimize reverb convolution FFT | 35 / 600 / 2.5 | 47 / 780 / 0.9 | 63 / 690 / 4.8 | Playback + Bounce improve |
| 9 | Fix sample rate conversion edge case | 35 / 600 / 2.5 | 49 / 790 / 1.0 | 64 / 700 / 4.9 | Stable |
| 10 | Add live looping engine | 35 / 600 / 2.5 | 48 / 790 / 0.95 | 64 / 700 / 4.9 | Stable |
| 11 | Parallelize offline bounce | 35 / 600 / 2.5 | 48 / 790 / 0.95 | 58 / 650 / 4.2 | Bounce much faster |
| 12 | Optimize project auto-save | 34 / 580 / 2.4 | 48 / 790 / 0.95 | 58 / 650 / 4.2 | Stable |
| 13 | Add stem export functionality | 35 / 600 / 2.5 | 48 / 790 / 0.95 | 60 / 670 / 4.4 | Bounce slightly heavier |
| 14 | Refactor plugin delay compensation | 35 / 600 / 2.5 | 47 / 780 / 0.9 | 58 / 650 / 4.2 | Good |
| 15 | Enable 192kHz session support | 36 / 640 / 2.6 | 50 / 820 / 1.0 | 60 / 670 / 4.5 | Slight increase across board |
| 16 | Optimize automation envelope rendering | 35 / 600 / 2.5 | 46 / 770 / 0.9 | 58 / 650 / 4.2 | Good |
| 17 | Add real-time pitch correction plugin | 35 / 600 / 2.5 | 72 / 1100 / 1.8 | 58 / 650 / 4.2 | **STRONG regression on Playback** — CPU +57%, Mem +43%, Time +100% |
| 18 | Throttle pitch correction to half rate | 35 / 600 / 2.5 | 58 / 900 / 1.3 | 58 / 650 / 4.2 | Partial fix — still elevated (**possible regression**) |
| 19 | Move pitch correction to dedicated DSP thread | 35 / 600 / 2.5 | 48 / 800 / 0.95 | 58 / 650 / 4.2 | Playback recovered |
| 20 | Add AI mastering assistant (bounce only) | 35 / 600 / 2.5 | 48 / 800 / 0.95 | 78 / 950 / 6.8 | **STRONG regression on Bounce** — new AI feature is expensive |

**Story:** Gradual improvements through commit 16. Commit 17 adds a real-time pitch correction plugin that destroys playback performance. Commit 18 partially mitigates, commit 19 fully fixes it by offloading to a dedicated thread. But commit 20 introduces an AI mastering feature that causes a new bounce regression — left unresolved to show an open issue.

---

## Xcode (mock_xcode)

Baseline defaults: Clean(CPU 80, Mem 2000, Time 6.0) | Incremental(CPU 45, Mem 1200, Time 1.5) | Tests(CPU 60, Mem 1500, Time 4.0)

| # | Commit Message | Clean Build | Incremental Build | Run Unit Tests | Notes |
|---|---|---|---|---|---|
| 1 | Initial benchmark baseline | 80 / 2000 / 6.0 | 45 / 1200 / 1.5 | 60 / 1500 / 4.0 | Establish baseline |
| 2 | Add Swift 6 strict concurrency checks | 82 / 2050 / 6.2 | 46 / 1220 / 1.6 | 60 / 1500 / 4.0 | Build slightly heavier |
| 3 | Enable incremental build caching | 80 / 2000 / 6.0 | 40 / 1100 / 1.2 | 60 / 1500 / 4.0 | Incremental build improves |
| 4 | Optimize dependency graph resolver | 76 / 1950 / 5.7 | 38 / 1080 / 1.1 | 60 / 1500 / 4.0 | Both builds improve |
| 5 | Add SwiftUI preview compilation | 78 / 2000 / 5.9 | 42 / 1150 / 1.3 | 60 / 1500 / 4.0 | Slight increase |
| 6 | Parallelize module compilation | 72 / 1900 / 5.3 | 38 / 1080 / 1.1 | 60 / 1500 / 4.0 | Clean build improves |
| 7 | Optimize linker symbol resolution | 70 / 1850 / 5.1 | 37 / 1050 / 1.1 | 60 / 1500 / 4.0 | Steady improvement |
| 8 | Add distributed test execution | 80 / 2000 / 6.0 | 38 / 1080 / 1.1 | 52 / 1350 / 3.2 | Tests faster, build reverts |
| 9 | Enable code coverage instrumentation | 80 / 2000 / 6.0 | 38 / 1080 / 1.1 | 56 / 1450 / 3.6 | Tests slightly heavier with coverage |
| 10 | Optimize XCTest assertion macros | 80 / 2000 / 6.0 | 38 / 1080 / 1.1 | 53 / 1400 / 3.3 | Tests improve |
| 11 | Add precompiled bridging header cache | 75 / 1900 / 5.5 | 36 / 1020 / 1.0 | 53 / 1400 / 3.3 | Builds improve |
| 12 | Refactor build system plist handling | 74 / 1880 / 5.4 | 36 / 1020 / 1.0 | 53 / 1400 / 3.3 | Stable |
| 13 | Enable explicit module builds | 76 / 1920 / 5.6 | 37 / 1050 / 1.1 | 53 / 1400 / 3.3 | Slight build increase |
| 14 | Optimize asset catalog compilation | 73 / 1870 / 5.3 | 35 / 1000 / 1.0 | 53 / 1400 / 3.3 | Builds improve |
| 15 | Add Swift macro expansion support | 75 / 1900 / 5.5 | 36 / 1020 / 1.0 | 54 / 1420 / 3.4 | Stable |
| 16 | Enable whole-module optimization by default | 73 / 1870 / 5.3 | 35 / 1000 / 1.0 | 53 / 1400 / 3.3 | Good |
| 17 | Add on-device debugging instrumentation | 73 / 1870 / 5.3 | 35 / 1000 / 1.0 | 53 / 1400 / 3.3 | No change (debug only) |
| 18 | Integrate new static analyzer passes | 92 / 2600 / 8.5 | 52 / 1600 / 2.3 | 53 / 1400 / 3.3 | **STRONG regression on Clean Build + Incremental** — analyzer doubles build work |
| 19 | Make static analysis opt-in for incremental builds | 90 / 2500 / 8.2 | 36 / 1020 / 1.0 | 53 / 1400 / 3.3 | Incremental fixed, clean still regressed (**possible regression** on clean) |
| 20 | Parallelize static analyzer with build pipeline | 76 / 1950 / 5.7 | 36 / 1020 / 1.0 | 70 / 1800 / 5.5 | Clean recovered but **STRONG regression on Tests** — analyzer now runs in test target |

**Story:** Steady build optimizations through commit 17. Commit 18 integrates a static analyzer that tanks both build workflows. Commit 19 fixes incremental builds by making analysis opt-in there. Commit 20 parallelizes the analyzer to fix clean builds, but accidentally enables it in the test target, causing a test regression — left as an open issue.

---

## How to Use

For each commit in the sequence, enter the workflow metrics in the dashboard sliders for that app, type the commit message, and press **Commit & Push**. The CI pipeline will run and write the data to InfluxDB. Wait for each CI run to complete before making the next commit (check GitHub Actions).

The Grafana dashboards will show:
- **Commits 1-16**: Gradual improvements and stable baselines
- **Commits 17-18**: Dramatic regressions appear as spikes
- **Commits 19-20**: Partial fixes with new regressions cascading elsewhere
