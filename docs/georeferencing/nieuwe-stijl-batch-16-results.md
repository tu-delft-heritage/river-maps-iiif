# Nieuwe Stijl batch 16 — D.16 ready for review

> Series D.16 was approved by the user on 20 November 2026. Acceptance is recorded against the exact geometry in the [dashboard](../../dashboard/index.html). The initial processing report below is retained for provenance.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-16/review-annotations.json) contains all 127 previously unprocessed digitized D.16 maps. The [full-series AnnotationPage](../../dashboard/annotations/series-D.16.json) includes its two accepted pilot maps, for 129 maps. The [dashboard](../../dashboard/index.html) provides a combined download and a direct Allmaps Viewer link per series. All 999 digitized maps are now prepared: 179 accepted by the user and 820 awaiting review. Sheet indices are excluded; nothing was committed.

## Results

- 127 native masks, 508 fitted controls and 127 held-out checks. Source labels and crosses, final frame/title patches, all 635 final control/check patches and 127 mask overlays were visually inspected.
- 57 pass the unchanged numerical screen; 70 retain QA flags. RMS ranges from 0.88 to 3.68 native pixels; maximum held-out error is 6.12 pixels.
- 23 maps use RD Old and 104 use RD New. Original projected coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; residuals are not survey accuracy.
- 651 cached evidence images total 83,444,886 bytes. Overviews and bounded native sections were acquired serially with at least one second between requests. No full native scans were requested.

## Corrections and verification

D.16 includes 200-metre grids, RD Old and RD New editions, and labels printed in metres, hectometres and kilometres. Visual inspection corrected registration proposals, outer-paper borders, title positions, grid-step assignments and several cross centres. Fourteen top-frame and two bottom-frame sections supplemented cached corners. No overlap tie points enter the absolute fit.

Scan 812 has no surviving easting labels in its four native corner crops. Its absolute easting is established by visually matching the printed grid and cartography with labelled editions of sheet 880 (1459 and 1460); its canonical record explicitly preserves the external border anchor, source inventory, crop evidence and coordinate provenance. Its northings use its own surviving labels. This dependency is not an independent absolute-position check.

Scan 1455 visibly prints a northing of `-50.000` on its lower/right border, inconsistent with the other labels and 200-metre grid. The raw anomaly is retained in the review record. It is not used as an absolute anchor; grid tracing uses the consistent top/left labels.

Geometry fingerprints bind AI visual review to final controls and masks. Human acceptance remains separate. All 32 pipeline tests, 13 annotation/dashboard tests and TypeScript checking passed. Export validates the Allmaps parser and compares the Viewer transformation numerically against the projected affine fit.

## Measured processing time

The recorded preparation interval is 207.10 minutes, from 2026-11-19T20:42:13.972430+00:00 to 2026-11-20T00:09:20.029Z. This is wall-clock time from initial preparation through first export, including waits and visual review. Acquisition overlaps other series; intervals are not additive. Instrumented command durations are available in the dashboard; helper work and model latency are not separately measured. Token statistics have been removed.

## Per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 1402 | EPSG:28992 | 1.46 | 1.25 | Pass |
| 770 | EPSG:28992 | 1.57 | 1.22 | Pass |
| 771 | EPSG:28992 | 1.83 | 2.35 | Pass |
| 772 | EPSG:28992 | 2.16 | 0.68 | rms-above-2px |
| 1403 | EPSG:28992 | 2.77 | 3.01 | rms-above-2px |
| 773 | EPSG:28992 | 2.08 | 1.02 | rms-above-2px |
| 1404 | EPSG:28992 | 2.70 | 2.63 | rms-above-2px |
| 774 | EPSG:28992 | 2.25 | 0.87 | rms-above-2px |
| 1405 | EPSG:28991 | 2.31 | 1.70 | rms-above-2px |
| 1406 | EPSG:28992 | 1.58 | 2.77 | Pass |
| 775 | EPSG:28992 | 1.75 | 1.47 | Pass |
| 1407 | EPSG:28991 | 2.71 | 0.54 | rms-above-2px |
| 776 | EPSG:28992 | 2.04 | 2.82 | rms-above-2px |
| 1408 | EPSG:28992 | 2.25 | 1.16 | rms-above-2px |
| 1409 | EPSG:28992 | 2.50 | 0.91 | rms-above-2px |
| 1410 | EPSG:28992 | 2.95 | 0.97 | rms-above-2px |
| 777 | EPSG:28992 | 1.92 | 1.73 | Pass |
| 1411 | EPSG:28992 | 2.21 | 1.45 | rms-above-2px |
| 778 | EPSG:28992 | 2.31 | 1.92 | rms-above-2px |
| 1412 | EPSG:28992 | 1.69 | 3.42 | Pass |
| 779 | EPSG:28992 | 1.72 | 0.65 | Pass |
| 1413 | EPSG:28992 | 2.26 | 3.65 | rms-above-2px |
| 1414 | EPSG:28992 | 2.65 | 1.09 | rms-above-2px |
| 781 | EPSG:28992 | 2.69 | 1.46 | rms-above-2px |
| 1415 | EPSG:28992 | 2.16 | 0.50 | rms-above-2px |
| 1417 | EPSG:28991 | 2.25 | 0.53 | rms-above-2px |
| 1416 | EPSG:28992 | 2.08 | 0.28 | rms-above-2px |
| 782 | EPSG:28992 | 1.44 | 1.24 | Pass |
| 783 | EPSG:28992 | 1.03 | 0.46 | Pass |
| 784 | EPSG:28992 | 1.54 | 1.52 | Pass |
| 1419 | EPSG:28991 | 2.74 | 0.97 | rms-above-2px |
| 1418 | EPSG:28992 | 1.92 | 1.20 | Pass |
| 785 | EPSG:28992 | 1.80 | 2.35 | Pass |
| 1420 | EPSG:28992 | 2.55 | 0.90 | rms-above-2px |
| 786 | EPSG:28992 | 2.54 | 0.93 | rms-above-2px |
| 787 | EPSG:28992 | 1.97 | 2.14 | Pass |
| 1421 | EPSG:28992 | 2.44 | 2.17 | rms-above-2px |
| 1422 | EPSG:28992 | 2.52 | 3.12 | rms-above-2px |
| 788 | EPSG:28992 | 1.73 | 1.40 | Pass |
| 789 | EPSG:28992 | 1.42 | 1.74 | Pass |
| 1423 | EPSG:28992 | 1.45 | 2.08 | Pass |
| 1424 | EPSG:28992 | 2.18 | 1.42 | rms-above-2px |
| 790 | EPSG:28992 | 1.55 | 1.62 | Pass |
| 1425 | EPSG:28991 | 2.39 | 4.73 | rms-above-2px |
| 1426 | EPSG:28992 | 1.76 | 3.21 | Pass |
| 791 | EPSG:28992 | 1.57 | 2.24 | Pass |
| 1428 | EPSG:28991 | 3.41 | 1.75 | rms-above-2px |
| 1427 | EPSG:28992 | 1.82 | 1.09 | Pass |
| 793 | EPSG:28992 | 1.75 | 0.71 | Pass |
| 1429 | EPSG:28992 | 2.38 | 3.48 | rms-above-2px |
| 792 | EPSG:28992 | 1.83 | 2.25 | Pass |
| 1430 | EPSG:28992 | 1.80 | 0.81 | Pass |
| 1431 | EPSG:28992 | 2.46 | 2.08 | rms-above-2px |
| 794 | EPSG:28992 | 1.79 | 0.36 | Pass |
| 1432 | EPSG:28992 | 1.93 | 1.32 | Pass |
| 795 | EPSG:28992 | 2.23 | 2.49 | rms-above-2px |
| 1433 | EPSG:28992 | 2.40 | 0.95 | rms-above-2px |
| 796 | EPSG:28992 | 1.33 | 1.16 | Pass |
| 1434 | EPSG:28992 | 2.14 | 1.17 | rms-above-2px |
| 797 | EPSG:28992 | 2.49 | 0.54 | rms-above-2px |
| 1435 | EPSG:28992 | 1.81 | 1.72 | Pass |
| 798 | EPSG:28992 | 2.37 | 1.04 | rms-above-2px |
| 1436 | EPSG:28991 | 2.50 | 1.22 | rms-above-2px |
| 1437 | EPSG:28992 | 1.64 | 0.50 | Pass |
| 799 | EPSG:28992 | 1.24 | 1.57 | Pass |
| 1439 | EPSG:28991 | 1.99 | 1.48 | Pass |
| 1438 | EPSG:28992 | 2.29 | 1.16 | rms-above-2px |
| 800 | EPSG:28992 | 1.71 | 0.54 | Pass |
| 1440 | EPSG:28992 | 2.01 | 2.33 | rms-above-2px |
| 1441 | EPSG:28992 | 0.88 | 2.37 | Pass |
| 801 | EPSG:28992 | 0.98 | 1.74 | Pass |
| 1443 | EPSG:28992 | 1.82 | 1.15 | Pass |
| 803 | EPSG:28992 | 1.78 | 1.23 | Pass |
| 1444 | EPSG:28992 | 1.72 | 2.98 | Pass |
| 804 | EPSG:28992 | 1.70 | 2.18 | Pass |
| 1445 | EPSG:28992 | 2.76 | 1.93 | rms-above-2px |
| 1446 | EPSG:28992 | 2.29 | 1.01 | rms-above-2px |
| 805 | EPSG:28992 | 1.68 | 1.30 | Pass |
| 1447 | EPSG:28991 | 2.65 | 3.71 | rms-above-2px |
| 1448 | EPSG:28992 | 2.35 | 3.33 | rms-above-2px |
| 806 | EPSG:28992 | 1.29 | 1.73 | Pass |
| 1450 | EPSG:28991 | 2.36 | 5.79 | rms-above-2px, check-above-5px |
| 1449 | EPSG:28992 | 1.19 | 6.12 | check-above-5px |
| 807 | EPSG:28992 | 1.00 | 2.55 | Pass |
| 1452 | EPSG:28992 | 3.00 | 2.09 | rms-above-2px |
| 1451 | EPSG:28992 | 2.12 | 3.17 | rms-above-2px |
| 1453 | EPSG:28992 | 2.81 | 1.68 | rms-above-2px |
| 1454 | EPSG:28992 | 2.55 | 2.25 | rms-above-2px |
| 808 | EPSG:28992 | 1.96 | 1.22 | Pass |
| 1455 | EPSG:28991 | 3.36 | 3.28 | rms-above-2px |
| 1456 | EPSG:28992 | 1.50 | 0.94 | Pass |
| 809 | EPSG:28992 | 0.96 | 2.11 | Pass |
| 1458 | EPSG:28992 | 1.69 | 0.80 | Pass |
| 1457 | EPSG:28992 | 1.87 | 2.21 | Pass |
| 810 | EPSG:28992 | 2.10 | 0.86 | rms-above-2px |
| 1459 | EPSG:28992 | 2.23 | 2.50 | rms-above-2px |
| 1460 | EPSG:28992 | 1.89 | 1.94 | Pass |
| 812 | EPSG:28992 | 1.69 | 1.24 | Pass |
| 1461 | EPSG:28992 | 2.80 | 1.03 | rms-above-2px |
| 811 | EPSG:28992 | 1.77 | 0.56 | Pass |
| 1462 | EPSG:28992 | 1.84 | 1.60 | Pass |
| 1463 | EPSG:28992 | 2.28 | 2.50 | rms-above-2px |
| 813 | EPSG:28992 | 2.11 | 0.74 | rms-above-2px |
| 1466 | EPSG:28991 | 2.57 | 0.37 | rms-above-2px |
| 1464 | EPSG:28992 | 3.68 | 4.44 | rms-above-2px |
| 1465 | EPSG:28992 | 2.67 | 3.37 | rms-above-2px |
| 814 | EPSG:28992 | 1.83 | 3.35 | Pass |
| 1468 | EPSG:28991 | 2.09 | 2.74 | rms-above-2px |
| 1467 | EPSG:28992 | 2.94 | 5.59 | rms-above-2px, check-above-5px |
| 815 | EPSG:28992 | 2.04 | 3.93 | rms-above-2px |
| 1469 | EPSG:28991 | 1.73 | 1.76 | Pass |
| 816 | EPSG:28992 | 2.04 | 0.54 | rms-above-2px |
| 1471 | EPSG:28991 | 2.56 | 1.22 | rms-above-2px |
| 1470 | EPSG:28992 | 2.74 | 0.80 | rms-above-2px |
| 817 | EPSG:28992 | 1.83 | 1.03 | Pass |
| 1472 | EPSG:28992 | 2.41 | 4.84 | rms-above-2px |
| 1473 | EPSG:28992 | 1.71 | 2.83 | Pass |
| 818 | EPSG:28992 | 1.09 | 3.77 | Pass |
| 1474 | EPSG:28991 | 1.39 | 0.98 | Pass |
| 819 | EPSG:28992 | 2.90 | 1.70 | rms-above-2px |
| 1475 | EPSG:28991 | 2.15 | 1.76 | rms-above-2px |
| 1476 | EPSG:28991 | 2.67 | 0.84 | rms-above-2px |
| 1478 | EPSG:28991 | 2.44 | 0.87 | rms-above-2px |
| 1477 | EPSG:28991 | 2.54 | 1.29 | rms-above-2px |
| 1479 | EPSG:28991 | 1.98 | 1.61 | Pass |
| 1480 | EPSG:28991 | 2.47 | 0.65 | rms-above-2px |
| 1481 | EPSG:28991 | 2.03 | 0.79 | rms-above-2px |
