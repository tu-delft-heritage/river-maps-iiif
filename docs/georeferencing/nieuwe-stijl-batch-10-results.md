# Nieuwe Stijl batch 10 — D.10 ready for review

> Series D.10 was approved by the user on 20 November 2026. Acceptance is recorded against the exact geometry in the [dashboard](../../dashboard/index.html). The initial processing report below is retained for provenance.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-10/review-annotations.json) contains all 43 digitized D.10 maps. The [dashboard](../../dashboard/index.html) provides a combined download and a direct Allmaps Viewer link. Human review remains pending. Sheet indices are excluded; nothing was committed.

## Results

- 43 native masks, 172 fitted controls and 43 held-out checks. Native labels and crosses, final frame/title patches, all 215 final control/check patches and 43 mask overlays were visually inspected.
- 19 pass the unchanged numerical screen; 24 retain QA flags. RMS ranges from 0.73 to 3.19 native pixels; maximum held-out error is 5.40 pixels.
- 23 maps use RD Old and 20 use RD New. Original projected coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; residuals are not survey accuracy.
- 226 cached evidence images total 38,160,947 bytes. Overviews and bounded native sections were acquired serially with at least one second between requests. No full native scans were requested.

## Corrections and verification

D.10 includes 200-metre grids, editions with RD Old or RD New coordinates, changed extents, faint crosses and title boxes along the side of the frame. Native source inspection corrected false CV proposals and resolved the printed coordinate systems. Caption notches exclude marginal text and retain cartography around the title boxes. Additional bounded sections resolved frame corners outside initial crops. Final control and frame corrections are recorded in `final-visual-corrections.json`. No overlap tie points enter the absolute fit. Geometry fingerprints bind AI visual review to the final controls and masks; human review remains separate.

## Measured processing time

The recorded preparation interval is 128.64 minutes, from 2026-11-19T20:21:26.993052+00:00 to 2026-11-19T22:30:05.162Z. This is wall-clock time from initial preparation through first export, including waits and visual review. Acquisition overlaps other series; intervals are not additive. Instrumented command durations are also available in the dashboard; helper work and model latency are not separately measured.

## Per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 1253 | EPSG:28992 | 2.02 | 1.33 | rms-above-2px |
| 660 | EPSG:28992 | 3.04 | 3.00 | rms-above-2px |
| 1257 | EPSG:28991 | 2.31 | 1.30 | rms-above-2px |
| 1255 | EPSG:28992 | 1.12 | 0.56 | Pass |
| 1254 | EPSG:28992 | 1.82 | 1.44 | Pass |
| 1256 | EPSG:28992 | 1.35 | 1.20 | Pass |
| 1259 | EPSG:28991 | 2.43 | 1.33 | rms-above-2px |
| 1258 | EPSG:28992 | 2.08 | 1.96 | rms-above-2px |
| 661 | EPSG:28992 | 2.21 | 1.65 | rms-above-2px |
| 662 | EPSG:28991 | 1.14 | 1.19 | Pass |
| 1260 | EPSG:28991 | 2.44 | 1.83 | rms-above-2px |
| 663 | EPSG:28992 | 2.81 | 2.07 | rms-above-2px |
| 1261 | EPSG:28991 | 1.05 | 3.18 | Pass |
| 664 | EPSG:28992 | 2.11 | 1.66 | rms-above-2px |
| 1262 | EPSG:28991 | 2.44 | 2.06 | rms-above-2px |
| 665 | EPSG:28991 | 2.27 | 1.63 | rms-above-2px |
| 1263 | EPSG:28991 | 0.93 | 0.77 | Pass |
| 666 | EPSG:28991 | 0.98 | 0.85 | Pass |
| 1264 | EPSG:28991 | 3.19 | 1.95 | rms-above-2px |
| 667 | EPSG:28991 | 2.10 | 1.58 | rms-above-2px |
| 1265 | EPSG:28991 | 2.51 | 1.93 | rms-above-2px |
| 668 | EPSG:28992 | 1.35 | 1.33 | Pass |
| 669 | EPSG:28991 | 0.73 | 0.92 | Pass |
| 670 | EPSG:28991 | 1.31 | 2.06 | Pass |
| 1266 | EPSG:28991 | 1.81 | 1.43 | Pass |
| 671 | EPSG:28992 | 2.25 | 1.13 | rms-above-2px |
| 1268 | EPSG:28991 | 1.77 | 4.10 | Pass |
| 1267 | EPSG:28992 | 1.25 | 3.88 | Pass |
| 672 | EPSG:28992 | 1.75 | 5.40 | check-above-5px |
| 1269 | EPSG:28991 | 1.29 | 1.43 | Pass |
| 673 | EPSG:28992 | 2.33 | 2.11 | rms-above-2px |
| 1270 | EPSG:28991 | 2.51 | 1.22 | rms-above-2px |
| 674 | EPSG:28992 | 2.06 | 2.01 | rms-above-2px |
| 675 | EPSG:28991 | 1.68 | 2.29 | Pass |
| 676 | EPSG:28991 | 1.87 | 1.42 | Pass |
| 677 | EPSG:28991 | 2.07 | 2.87 | rms-above-2px |
| 1271 | EPSG:28991 | 1.50 | 1.45 | Pass |
| 678 | EPSG:28992 | 1.53 | 0.29 | Pass |
| 1272 | EPSG:28991 | 2.76 | 2.46 | rms-above-2px |
| 679 | EPSG:28992 | 2.07 | 0.91 | rms-above-2px |
| 1355 | EPSG:28992 | 1.58 | 2.25 | Pass |
| 1356 | EPSG:28992 | 2.43 | 1.81 | rms-above-2px |
| 1357 | EPSG:28992 | 2.55 | 0.90 | rms-above-2px |
