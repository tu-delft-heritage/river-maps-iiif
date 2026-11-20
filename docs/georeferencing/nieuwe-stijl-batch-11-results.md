# Nieuwe Stijl batch 11 — D.11 visually approved

> Follow-up on 20 November: the user approved the corrected placements and the complete D.11 series. See the [eight-map review report](nieuwe-stijl-review-2026-11-20.md) and the dashboard for current placements. The original export diagnostics below are retained as the processing history.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-11/review-annotations.json) contains all 79 digitized D.11 maps. The [dashboard](../../dashboard/index.html) provides a combined download and a direct Allmaps Viewer link. The complete series is visually approved. Sheet indices are excluded; nothing was committed.

## Initial export results

- 79 native masks, 316 fitted controls and 79 held-out checks. Native labels and crosses, final frame/title patches, all 395 final control/check patches and 79 mask overlays were visually inspected.
- 20 pass the unchanged numerical screen; 59 retain QA flags. RMS ranges from 0.61 to 4.10 native pixels; maximum held-out error is 5.66 pixels.
- 29 maps use RD Old and 50 use RD New. Original projected coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; residuals are not survey accuracy.
- 408 cached evidence images total 61,849,744 bytes. Overviews and bounded native sections were acquired serially with at least one second between requests. No full native scans were requested.

## Corrections and verification

D.11 includes 200-metre grids, editions with RD Old or RD New coordinates, changed extents, faint crosses and title boxes along the side of the frame. Native source inspection corrected false CV proposals and resolved the printed coordinate systems. Caption notches exclude marginal text and retain cartography around the title boxes. Additional bounded sections resolved frame corners outside initial crops. Final control and frame corrections are recorded in `final-visual-corrections.json`. No overlap tie points enter the absolute fit. Geometry fingerprints bind AI visual review to the final controls and masks; human review remains separate.

## Measured processing time

The recorded preparation interval is 145.53 minutes, from 2026-11-19T20:25:21.708071+00:00 to 2026-11-19T22:50:53.799Z. This is wall-clock time from initial preparation through first export, including waits and visual review. Acquisition overlaps other series; intervals are not additive. Instrumented command durations are also available in the dashboard; helper work and model latency are not separately measured.

## Original per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 680 | EPSG:28992 | 2.80 | 2.18 | rms-above-2px |
| 1274 | EPSG:28991 | 2.95 | 1.86 | rms-above-2px |
| 681 | EPSG:28992 | 2.39 | 1.07 | rms-above-2px |
| 1275 | EPSG:28991 | 1.64 | 3.62 | Pass |
| 682 | EPSG:28991 | 0.61 | 0.81 | Pass |
| 1276 | EPSG:28991 | 2.82 | 1.17 | rms-above-2px |
| 683 | EPSG:28992 | 2.99 | 0.82 | rms-above-2px |
| 1277 | EPSG:28991 | 2.90 | 3.69 | rms-above-2px |
| 1278 | EPSG:28991 | 2.52 | 3.32 | rms-above-2px |
| 684 | EPSG:28992 | 1.71 | 3.48 | Pass |
| 1280 | EPSG:28991 | 2.53 | 2.35 | rms-above-2px |
| 1279 | EPSG:28991 | 2.12 | 2.79 | rms-above-2px |
| 685 | EPSG:28992 | 1.63 | 2.58 | Pass |
| 1281 | EPSG:28991 | 3.40 | 2.16 | rms-above-2px |
| 1282 | EPSG:28992 | 2.91 | 1.86 | rms-above-2px |
| 686 | EPSG:28992 | 2.00 | 0.56 | rms-above-2px |
| 1284 | EPSG:28991 | 1.96 | 1.53 | Pass |
| 1283 | EPSG:28992 | 1.87 | 2.35 | Pass |
| 687 | EPSG:28992 | 1.23 | 0.81 | Pass |
| 1285 | EPSG:28991 | 2.98 | 4.97 | rms-above-2px |
| 1286 | EPSG:28992 | 2.26 | 1.88 | rms-above-2px |
| 688 | EPSG:28992 | 2.03 | 2.12 | rms-above-2px |
| 1287 | EPSG:28991 | 3.16 | 2.27 | rms-above-2px |
| 1288 | EPSG:28992 | 2.74 | 0.73 | rms-above-2px |
| 689 | EPSG:28992 | 2.52 | 3.55 | rms-above-2px |
| 1289 | EPSG:28991 | 4.10 | 0.69 | rms-above-2px |
| 1290 | EPSG:28992 | 2.61 | 2.60 | rms-above-2px |
| 690 | EPSG:28992 | 3.22 | 0.59 | rms-above-2px |
| 1291 | EPSG:28991 | 2.14 | 1.24 | rms-above-2px |
| 1292 | EPSG:28992 | 2.13 | 0.70 | rms-above-2px |
| 691 | EPSG:28992 | 2.05 | 2.18 | rms-above-2px |
| 1294 | EPSG:28991 | 1.97 | 4.15 | Pass |
| 1293 | EPSG:28992 | 2.58 | 0.32 | rms-above-2px |
| 1295 | EPSG:28992 | 2.21 | 2.77 | rms-above-2px |
| 692 | EPSG:28992 | 1.40 | 5.66 | check-above-5px |
| 1296 | EPSG:28991 | 2.82 | 1.49 | rms-above-2px |
| 1297 | EPSG:28992 | 2.11 | 3.29 | rms-above-2px |
| 1298 | EPSG:28992 | 3.16 | 1.78 | rms-above-2px |
| 693 | EPSG:28992 | 2.43 | 2.14 | rms-above-2px |
| 1299 | EPSG:28991 | 1.81 | 1.34 | Pass |
| 1301 | EPSG:28992 | 2.78 | 2.30 | rms-above-2px |
| 1300 | EPSG:28992 | 1.81 | 0.75 | Pass |
| 694 | EPSG:28992 | 1.78 | 0.62 | Pass |
| 1302 | EPSG:28991 | 2.94 | 2.01 | rms-above-2px |
| 1303 | EPSG:28992 | 2.44 | 1.08 | rms-above-2px |
| 695 | EPSG:28992 | 2.12 | 1.99 | rms-above-2px |
| 1304 | EPSG:28991 | 2.31 | 1.86 | rms-above-2px |
| 1305 | EPSG:28992 | 3.30 | 1.49 | rms-above-2px |
| 696 | EPSG:28992 | 1.52 | 1.26 | Pass |
| 1306 | EPSG:28991 | 2.69 | 1.41 | rms-above-2px |
| 1307 | EPSG:28992 | 2.22 | 1.80 | rms-above-2px |
| 697 | EPSG:28992 | 2.56 | 1.55 | rms-above-2px |
| 1308 | EPSG:28991 | 2.57 | 0.62 | rms-above-2px |
| 1309 | EPSG:28992 | 2.97 | 2.09 | rms-above-2px |
| 698 | EPSG:28992 | 2.17 | 0.90 | rms-above-2px |
| 1310 | EPSG:28991 | 1.64 | 2.00 | Pass |
| 1311 | EPSG:28992 | 2.72 | 2.04 | rms-above-2px |
| 699 | EPSG:28992 | 2.41 | 0.59 | rms-above-2px |
| 1312 | EPSG:28991 | 2.01 | 0.92 | rms-above-2px |
| 1313 | EPSG:28992 | 2.24 | 3.03 | rms-above-2px |
| 700 | EPSG:28992 | 1.68 | 0.84 | Pass |
| 1314 | EPSG:28991 | 2.04 | 1.81 | rms-above-2px |
| 1315 | EPSG:28992 | 2.44 | 0.94 | rms-above-2px |
| 701 | EPSG:28992 | 3.16 | 2.13 | rms-above-2px |
| 1316 | EPSG:28991 | 1.90 | 1.57 | Pass |
| 1317 | EPSG:28992 | 2.81 | 1.35 | rms-above-2px |
| 1318 | EPSG:28992 | 3.19 | 2.12 | rms-above-2px |
| 702 | EPSG:28992 | 2.34 | 1.40 | rms-above-2px |
| 1319 | EPSG:28991 | 2.02 | 0.97 | rms-above-2px |
| 1322 | EPSG:28991 | 1.19 | 0.82 | Pass |
| 1320 | EPSG:28992 | 2.83 | 1.12 | rms-above-2px |
| 1321 | EPSG:28992 | 2.67 | 0.99 | rms-above-2px |
| 703 | EPSG:28992 | 1.56 | 0.77 | Pass |
| 1323 | EPSG:28991 | 2.18 | 0.76 | rms-above-2px |
| 1324 | EPSG:28992 | 1.93 | 4.68 | Pass |
| 704 | EPSG:28992 | 1.41 | 2.35 | Pass |
| 1325 | EPSG:28991 | 1.24 | 1.19 | Pass |
| 1326 | EPSG:28992 | 2.15 | 1.00 | rms-above-2px |
| 705 | EPSG:28992 | 2.34 | 1.87 | rms-above-2px |
