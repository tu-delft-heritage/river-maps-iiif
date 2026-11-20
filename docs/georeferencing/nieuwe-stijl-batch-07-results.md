# Nieuwe Stijl batch 07 — D.07 visually approved

> Follow-up on 20 November: the user approved the corrected placements and the complete D.07 series. See the [eight-map review report](nieuwe-stijl-review-2026-11-20.md) and the dashboard for current placements. The original export diagnostics below are retained as the processing history.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-07/review-annotations.json) contains all 54 digitized D.07 maps. The [dashboard](../../dashboard/index.html) provides a combined download and a direct Allmaps Viewer link. The complete series is visually approved. Sheet indices are excluded; nothing was committed.

## Initial export results

- 54 native masks, 216 fitted controls and 54 held-out checks. Native labels and crosses, final frame/title patches, all 270 final control/check patches and 54 mask overlays were visually inspected.
- 9 pass the unchanged numerical screen; 45 retain QA flags. RMS ranges from 1.20 to 3.54 native pixels; maximum held-out error is 3.11 pixels.
- 25 maps use RD Old and 29 use RD New. Original projected coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; residuals are not survey accuracy.
- 285 cached evidence images total 45,644,416 bytes. Overviews and bounded native sections were acquired serially with at least one second between requests. No full native scans were requested.

## Corrections and verification

Inventories 1116–1121 reverse the orientation of their reference editions. Inventories 1123 and 1127 change orientation or extent. Registration sometimes proposed a different grid intersection or border text, even where the numerical fit appeared consistent. Direct native label reading and cross inspection corrected these assignments. Enlarged rotated native crops resolved faint labels on 1106 and 1127. Additional bounded sections resolved frame corners outside initial crops. Masks exclude title boxes and their captions. No overlap tie points enter the absolute fit. Geometry fingerprints bind AI visual review to the final controls and masks; human review remains separate.

## Measured processing time

The recorded preparation interval is 75.61 minutes, from 2026-11-19T20:03:54.241972+00:00 to 2026-11-19T21:19:30.841Z. This is wall-clock time from initial preparation through first export, including waits and visual review. Acquisition overlaps other series; intervals are not additive. Instrumented command durations are also available in the dashboard; helper work and model latency are not separately measured.

## Original per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 1106 | EPSG:28991 | 2.22 | 3.07 | rms-above-2px |
| 597 | EPSG:28992 | 2.33 | 1.46 | rms-above-2px |
| 1107 | EPSG:28991 | 2.34 | 1.44 | rms-above-2px |
| 1108 | EPSG:28992 | 3.01 | 1.88 | rms-above-2px |
| 1109 | EPSG:28991 | 2.28 | 1.42 | rms-above-2px |
| 1110 | EPSG:28991 | 2.66 | 1.55 | rms-above-2px |
| 598 | EPSG:28991 | 2.75 | 1.90 | rms-above-2px |
| 599 | EPSG:28992 | 2.55 | 1.13 | rms-above-2px |
| 600 | EPSG:28992 | 1.76 | 2.52 | Pass |
| 1111 | EPSG:28991 | 1.97 | 0.89 | Pass |
| 601 | EPSG:28991 | 2.47 | 1.24 | rms-above-2px |
| 602 | EPSG:28991 | 1.57 | 2.30 | Pass |
| 603 | EPSG:28992 | 1.36 | 3.03 | Pass |
| 604 | EPSG:28991 | 2.66 | 1.54 | rms-above-2px |
| 605 | EPSG:28992 | 3.26 | 1.65 | rms-above-2px |
| 606 | EPSG:28992 | 2.50 | 0.45 | rms-above-2px |
| 1112 | EPSG:28992 | 1.91 | 1.47 | Pass |
| 1113 | EPSG:28992 | 2.25 | 1.49 | rms-above-2px |
| 607 | EPSG:28992 | 2.00 | 1.92 | rms-above-2px |
| 1115 | EPSG:28992 | 2.42 | 2.32 | rms-above-2px |
| 1114 | EPSG:28992 | 2.39 | 0.39 | rms-above-2px |
| 608 | EPSG:28992 | 1.74 | 1.73 | Pass |
| 1117 | EPSG:28992 | 2.79 | 1.11 | rms-above-2px |
| 1116 | EPSG:28992 | 2.26 | 1.16 | rms-above-2px |
| 609 | EPSG:28992 | 2.02 | 2.86 | rms-above-2px |
| 1120 | EPSG:28991 | 2.29 | 1.03 | rms-above-2px |
| 1121 | EPSG:28991 | 2.06 | 1.18 | rms-above-2px |
| 1119 | EPSG:28992 | 2.32 | 1.56 | rms-above-2px |
| 1118 | EPSG:28992 | 2.31 | 1.56 | rms-above-2px |
| 610 | EPSG:28992 | 2.25 | 1.16 | rms-above-2px |
| 1122 | EPSG:28992 | 2.52 | 1.45 | rms-above-2px |
| 611 | EPSG:28992 | 1.97 | 3.11 | Pass |
| 612 | EPSG:28992 | 2.49 | 2.70 | rms-above-2px |
| 613 | EPSG:28992 | 2.36 | 2.71 | rms-above-2px |
| 614 | EPSG:28992 | 1.66 | 2.23 | Pass |
| 1123 | EPSG:28991 | 2.87 | 1.37 | rms-above-2px |
| 615 | EPSG:28992 | 2.75 | 2.76 | rms-above-2px |
| 1124 | EPSG:28991 | 2.11 | 1.71 | rms-above-2px |
| 616 | EPSG:28992 | 2.36 | 2.97 | rms-above-2px |
| 617 | EPSG:28992 | 2.57 | 1.83 | rms-above-2px |
| 618 | EPSG:28992 | 2.52 | 1.42 | rms-above-2px |
| 1125 | EPSG:28991 | 3.04 | 1.30 | rms-above-2px |
| 1126 | EPSG:28991 | 2.03 | 0.69 | rms-above-2px |
| 1127 | EPSG:28991 | 2.12 | 1.37 | rms-above-2px |
| 619 | EPSG:28992 | 2.12 | 1.67 | rms-above-2px |
| 1128 | EPSG:28991 | 3.07 | 1.66 | rms-above-2px |
| 1129 | EPSG:28991 | 2.10 | 1.18 | rms-above-2px |
| 1130 | EPSG:28991 | 1.20 | 1.26 | Pass |
| 1131 | EPSG:28991 | 2.09 | 0.61 | rms-above-2px |
| 1132 | EPSG:28991 | 2.18 | 0.75 | rms-above-2px |
| 1133 | EPSG:28991 | 3.28 | 1.69 | rms-above-2px |
| 1134 | EPSG:28991 | 2.09 | 1.45 | rms-above-2px |
| 1135 | EPSG:28991 | 2.53 | 1.55 | rms-above-2px |
| 1136 | EPSG:28991 | 3.54 | 2.89 | rms-above-2px |
