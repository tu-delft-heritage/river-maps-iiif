# Nieuwe Stijl batch 15 — D.15 visually approved

> Follow-up on 20 November: the user approved the corrected placements and the complete D.15 series. See the [eight-map review report](nieuwe-stijl-review-2026-11-20.md) and the dashboard for current placements. The original export diagnostics below are retained as the processing history.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-15/review-annotations.json) contains all 68 digitized D.15 maps. The [dashboard](../../dashboard/index.html) provides a combined download and a direct Allmaps Viewer link. The complete series is visually approved. Sheet indices are excluded; nothing was committed.

## Initial export results

- 68 native masks, 272 fitted controls and 68 held-out checks. Native labels and crosses, final frame/title patches, all 340 final control/check patches and 68 mask overlays were visually inspected.
- 15 pass the unchanged numerical screen; 53 retain QA flags. RMS ranges from 1.13 to 13.03 native pixels; maximum held-out error is 45.74 pixels.
- 16 maps use RD Old and 52 use RD New. Original projected coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; residuals are not survey accuracy.
- 355 cached evidence images total 46,604,504 bytes. Overviews and bounded native sections were acquired serially with at least one second between requests. No full native scans were requested.

## Corrections and verification

D.15 includes 200-metre grids and RD Old and RD New editions, including rotated copies with different orientations. Native inspection corrected false registration candidates, frame corners outside initial crops, and shifted title positions. Two top-right handwritten sheet numbers required small caption notches. On scan 1381 the printed northing prefixes look plus-shaped; their signed RD Old interpretation is explicitly preserved alongside the verbatim labels. Scans 751 and 1381 retain larger affine and held-out residuals after source reinspection; their cause is not established. A cross on an overprinted wharf edge on 1367 was replaced with the adjacent clean grid cross. No overlap tie points enter the absolute fit. Geometry fingerprints bind AI visual review to final controls and masks; human review remains separate. All 31 pipeline tests passed.

## Measured processing time

The recorded preparation interval is 176.24 minutes, from 2026-11-19T20:36:10.628114+00:00 to 2026-11-19T23:32:24.987Z. This is wall-clock time from initial preparation through first export, including waits and visual review. Acquisition overlaps other series; intervals are not additive. Instrumented command durations are also available in the dashboard; helper work and model latency are not separately measured.

## Original per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 741 | EPSG:28992 | 3.01 | 1.10 | rms-above-2px |
| 1360 | EPSG:28991 | 2.01 | 1.01 | rms-above-2px |
| 742 | EPSG:28992 | 2.32 | 0.58 | rms-above-2px |
| 1361 | EPSG:28991 | 3.08 | 2.24 | rms-above-2px |
| 743 | EPSG:28992 | 2.62 | 2.51 | rms-above-2px |
| 745 | EPSG:28992 | 2.71 | 0.65 | rms-above-2px |
| 746 | EPSG:28992 | 2.71 | 2.17 | rms-above-2px |
| 1362 | EPSG:28992 | 2.59 | 1.05 | rms-above-2px |
| 747 | EPSG:28992 | 2.65 | 0.89 | rms-above-2px |
| 1363 | EPSG:28992 | 2.36 | 0.26 | rms-above-2px |
| 748 | EPSG:28992 | 2.65 | 1.74 | rms-above-2px |
| 1364 | EPSG:28992 | 2.45 | 0.83 | rms-above-2px |
| 749 | EPSG:28992 | 2.24 | 0.85 | rms-above-2px |
| 1365 | EPSG:28992 | 3.34 | 2.94 | rms-above-2px |
| 750 | EPSG:28992 | 3.09 | 1.57 | rms-above-2px |
| 1366 | EPSG:28992 | 2.74 | 3.22 | rms-above-2px |
| 751 | EPSG:28992 | 13.03 | 45.74 | rms-above-2px, check-above-5px |
| 1367 | EPSG:28992 | 1.36 | 0.52 | Pass |
| 1368 | EPSG:28992 | 2.39 | 2.44 | rms-above-2px |
| 1369 | EPSG:28992 | 1.62 | 0.66 | Pass |
| 1370 | EPSG:28992 | 2.51 | 2.59 | rms-above-2px |
| 752 | EPSG:28992 | 2.26 | 1.09 | rms-above-2px |
| 1371 | EPSG:28992 | 3.01 | 1.36 | rms-above-2px |
| 753 | EPSG:28992 | 2.79 | 1.74 | rms-above-2px |
| 754 | EPSG:28992 | 1.50 | 1.30 | Pass |
| 1372 | EPSG:28992 | 2.06 | 1.15 | rms-above-2px |
| 755 | EPSG:28992 | 1.58 | 0.61 | Pass |
| 1373 | EPSG:28992 | 2.77 | 0.91 | rms-above-2px |
| 756 | EPSG:28992 | 1.61 | 1.15 | Pass |
| 757 | EPSG:28992 | 2.12 | 2.89 | rms-above-2px |
| 758 | EPSG:28992 | 1.76 | 0.71 | Pass |
| 1375 | EPSG:28992 | 2.13 | 1.88 | rms-above-2px |
| 1376 | EPSG:28992 | 2.42 | 2.07 | rms-above-2px |
| 1374 | EPSG:28992 | 2.46 | 1.27 | rms-above-2px |
| 759 | EPSG:28992 | 1.87 | 2.02 | Pass |
| 1378 | EPSG:28992 | 2.34 | 0.97 | rms-above-2px |
| 1377 | EPSG:28992 | 2.86 | 3.73 | rms-above-2px |
| 760 | EPSG:28992 | 2.19 | 0.49 | rms-above-2px |
| 761 | EPSG:28992 | 2.08 | 1.98 | rms-above-2px |
| 762 | EPSG:28992 | 1.45 | 1.95 | Pass |
| 1379 | EPSG:28992 | 2.37 | 1.34 | rms-above-2px |
| 763 | EPSG:28992 | 1.70 | 0.90 | Pass |
| 1381 | EPSG:28991 | 5.25 | 30.93 | rms-above-2px, check-above-5px |
| 1380 | EPSG:28992 | 2.98 | 3.07 | rms-above-2px |
| 1382 | EPSG:28992 | 2.63 | 3.22 | rms-above-2px |
| 764 | EPSG:28992 | 1.63 | 1.18 | Pass |
| 1384 | EPSG:28991 | 3.11 | 1.31 | rms-above-2px |
| 1383 | EPSG:28991 | 2.72 | 0.62 | rms-above-2px |
| 1385 | EPSG:28992 | 2.06 | 2.15 | rms-above-2px |
| 1386 | EPSG:28992 | 1.13 | 3.27 | Pass |
| 765 | EPSG:28992 | 2.60 | 1.81 | rms-above-2px |
| 1389 | EPSG:28991 | 3.08 | 2.63 | rms-above-2px |
| 1388 | EPSG:28992 | 2.99 | 2.20 | rms-above-2px |
| 1387 | EPSG:28992 | 1.26 | 6.80 | check-above-5px |
| 766 | EPSG:28992 | 2.53 | 1.60 | rms-above-2px |
| 1390 | EPSG:28992 | 3.19 | 1.76 | rms-above-2px |
| 1392 | EPSG:28991 | 2.69 | 1.21 | rms-above-2px |
| 1391 | EPSG:28991 | 2.43 | 1.47 | rms-above-2px |
| 767 | EPSG:28992 | 2.47 | 0.60 | rms-above-2px |
| 1393 | EPSG:28991 | 1.86 | 2.24 | Pass |
| 1394 | EPSG:28991 | 1.80 | 0.57 | Pass |
| 1396 | EPSG:28991 | 1.98 | 1.46 | Pass |
| 1395 | EPSG:28991 | 2.19 | 0.56 | rms-above-2px |
| 1397 | EPSG:28991 | 2.07 | 0.93 | rms-above-2px |
| 1398 | EPSG:28991 | 3.25 | 0.76 | rms-above-2px |
| 1399 | EPSG:28991 | 3.25 | 1.96 | rms-above-2px |
| 1400 | EPSG:28991 | 2.70 | 2.75 | rms-above-2px |
| 768 | EPSG:28992 | 1.78 | 1.76 | Pass |
