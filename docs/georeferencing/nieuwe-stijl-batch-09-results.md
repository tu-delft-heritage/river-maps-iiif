# Nieuwe Stijl batch 09 — D.09 ready for review

> Series D.09 was approved by the user on 20 November 2026. Acceptance is recorded against the exact geometry in the [dashboard](../../dashboard/index.html). The initial processing report below is retained for provenance.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-09/review-annotations.json) contains all 43 digitized D.09 maps. The [dashboard](../../dashboard/index.html) provides a combined download and a direct Allmaps Viewer link. Human review remains pending. Sheet indices are excluded; nothing was committed.

## Results

- 43 native masks, 172 fitted controls and 43 held-out checks. Native labels and crosses, final frame/title patches, all 215 final control/check patches and 43 mask overlays were visually inspected.
- 12 pass the unchanged numerical screen; 31 retain QA flags. RMS ranges from 1.66 to 2.94 native pixels; maximum held-out error is 3.45 pixels.
- 17 maps use RD Old and 26 use RD New. Original projected coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; residuals are not survey accuracy.
- 216 cached evidence images total 31,188,900 bytes. Overviews and bounded native sections were acquired serially with at least one second between requests. No full native scans were requested.

## Corrections and verification

D.09 includes 200-metre grids, editions with RD Old or RD New coordinates, changed extents, faint crosses and title boxes along the side of the frame. Native source inspection corrected false CV proposals and resolved the printed coordinate systems. Caption notches exclude marginal text and retain cartography around the title boxes. Additional bounded sections resolved frame corners outside initial crops. Final control and frame corrections are recorded in `final-visual-corrections.json`. No overlap tie points enter the absolute fit. Geometry fingerprints bind AI visual review to the final controls and masks; human review remains separate.

## Measured processing time

The recorded preparation interval is 118.26 minutes, from 2026-11-19T20:17:48.490091+00:00 to 2026-11-19T22:16:03.836Z. This is wall-clock time from initial preparation through first export, including waits and visual review. Acquisition overlaps other series; intervals are not additive. Instrumented command durations are also available in the dashboard; helper work and model latency are not separately measured.

## Per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 1213 | EPSG:28991 | 1.66 | 0.78 | Pass |
| 1214 | EPSG:28992 | 2.23 | 1.73 | rms-above-2px |
| 1215 | EPSG:28992 | 2.62 | 1.82 | rms-above-2px |
| 652 | EPSG:28992 | 2.01 | 1.56 | rms-above-2px |
| 1217 | EPSG:28991 | 2.55 | 2.33 | rms-above-2px |
| 1218 | EPSG:28991 | 2.84 | 2.49 | rms-above-2px |
| 1216 | EPSG:28992 | 1.93 | 0.88 | Pass |
| 1219 | EPSG:28992 | 2.33 | 1.66 | rms-above-2px |
| 1223 | EPSG:28991 | 1.90 | 1.61 | Pass |
| 1222 | EPSG:28991 | 2.47 | 2.27 | rms-above-2px |
| 1221 | EPSG:28992 | 1.71 | 1.45 | Pass |
| 1220 | EPSG:28992 | 2.77 | 1.92 | rms-above-2px |
| 1224 | EPSG:28992 | 2.20 | 1.46 | rms-above-2px |
| 1225 | EPSG:28991 | 2.43 | 1.89 | rms-above-2px |
| 1226 | EPSG:28991 | 2.18 | 1.92 | rms-above-2px |
| 1227 | EPSG:28992 | 1.84 | 1.36 | Pass |
| 1228 | EPSG:28992 | 2.42 | 1.26 | rms-above-2px |
| 654 | EPSG:28992 | 2.04 | 1.51 | rms-above-2px |
| 1230 | EPSG:28991 | 2.38 | 0.94 | rms-above-2px |
| 1231 | EPSG:28991 | 2.58 | 0.62 | rms-above-2px |
| 1229 | EPSG:28992 | 1.71 | 1.09 | Pass |
| 1232 | EPSG:28992 | 2.25 | 1.30 | rms-above-2px |
| 655 | EPSG:28992 | 2.08 | 1.33 | rms-above-2px |
| 1233 | EPSG:28991 | 1.70 | 2.53 | Pass |
| 1234 | EPSG:28991 | 1.81 | 2.88 | Pass |
| 1235 | EPSG:28992 | 1.87 | 1.40 | Pass |
| 1236 | EPSG:28992 | 1.68 | 1.49 | Pass |
| 656 | EPSG:28992 | 1.81 | 1.61 | Pass |
| 1239 | EPSG:28991 | 2.70 | 1.15 | rms-above-2px |
| 1238 | EPSG:28991 | 2.52 | 1.93 | rms-above-2px |
| 1237 | EPSG:28992 | 2.37 | 0.52 | rms-above-2px |
| 1240 | EPSG:28992 | 2.83 | 1.93 | rms-above-2px |
| 657 | EPSG:28992 | 2.04 | 1.13 | rms-above-2px |
| 1241 | EPSG:28991 | 2.30 | 1.29 | rms-above-2px |
| 1242 | EPSG:28991 | 2.02 | 1.22 | rms-above-2px |
| 1243 | EPSG:28992 | 2.19 | 1.65 | rms-above-2px |
| 1244 | EPSG:28992 | 1.79 | 0.91 | Pass |
| 658 | EPSG:28992 | 2.02 | 1.06 | rms-above-2px |
| 1247 | EPSG:28991 | 2.75 | 3.13 | rms-above-2px |
| 1246 | EPSG:28991 | 2.57 | 2.76 | rms-above-2px |
| 1245 | EPSG:28992 | 2.47 | 3.45 | rms-above-2px |
| 1248 | EPSG:28992 | 2.94 | 2.54 | rms-above-2px |
| 659 | EPSG:28992 | 2.38 | 2.38 | rms-above-2px |
