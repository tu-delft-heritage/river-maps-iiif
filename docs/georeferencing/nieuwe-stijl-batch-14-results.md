# Nieuwe Stijl batch 14 — D.14 ready for review

> Series D.14 was approved by the user on 20 November 2026. Acceptance is recorded against the exact geometry in the [dashboard](../../dashboard/index.html). The initial processing report below is retained for provenance.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-14/review-annotations.json) contains all 22 digitized D.14 maps. The [dashboard](../../dashboard/index.html) provides a combined download and a direct Allmaps Viewer link. Human review remains pending. Sheet indices are excluded; nothing was committed.

## Results

- 22 native masks, 88 fitted controls and 22 held-out checks. Native labels and crosses, final frame/title patches, all 110 final control/check patches and 22 mask overlays were visually inspected.
- 4 pass the unchanged numerical screen; 18 retain QA flags. RMS ranges from 1.27 to 3.30 native pixels; maximum held-out error is 4.34 pixels.
- 9 maps use RD Old and 13 use RD New. Original projected coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; residuals are not survey accuracy.
- 111 cached evidence images total 14,933,586 bytes. Overviews and bounded native sections were acquired serially with at least one second between requests. No full native scans were requested.

## Corrections and verification

D.14 includes 200-metre grids and RD Old and RD New editions. Native inspection corrected false CV proposals, resolved coordinate systems and traced separate border ticks to the correct crosses. The two editions of sheet 773/870 required corrections of one northing interval at two controls, confirmed with independent grid steps. An extra bounded section resolved a frame corner outside its initial crop. Title edges and caption notches were refined and rechecked. No overlap tie points enter the absolute fit. Geometry fingerprints bind AI visual review to the final controls and masks; human review remains separate.

## Measured processing time

The recorded preparation interval is 153.81 minutes, from 2026-11-19T20:34:18.551430+00:00 to 2026-11-19T23:08:07.174Z. This is wall-clock time from initial preparation through first export, including waits and visual review. Acquisition overlaps other series; intervals are not additive. Instrumented command durations are also available in the dashboard; helper work and model latency are not separately measured.

## Per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 1343 | EPSG:28992 | 2.66 | 2.17 | rms-above-2px |
| 717 | EPSG:28992 | 1.60 | 1.64 | Pass |
| 1346 | EPSG:28991 | 2.62 | 3.04 | rms-above-2px |
| 1345 | EPSG:28992 | 2.70 | 4.34 | rms-above-2px |
| 718 | EPSG:28992 | 2.73 | 4.01 | rms-above-2px |
| 1347 | EPSG:28991 | 2.73 | 1.28 | rms-above-2px |
| 719 | EPSG:28992 | 2.38 | 1.04 | rms-above-2px |
| 1348 | EPSG:28991 | 1.71 | 0.71 | Pass |
| 720 | EPSG:28992 | 2.82 | 0.45 | rms-above-2px |
| 1349 | EPSG:28991 | 2.28 | 1.42 | rms-above-2px |
| 721 | EPSG:28992 | 2.09 | 0.36 | rms-above-2px |
| 1350 | EPSG:28991 | 1.27 | 1.16 | Pass |
| 722 | EPSG:28992 | 1.87 | 0.85 | Pass |
| 1351 | EPSG:28991 | 2.38 | 0.71 | rms-above-2px |
| 723 | EPSG:28992 | 2.91 | 1.38 | rms-above-2px |
| 1352 | EPSG:28991 | 3.05 | 0.99 | rms-above-2px |
| 724 | EPSG:28992 | 2.96 | 0.69 | rms-above-2px |
| 1353 | EPSG:28991 | 2.99 | 1.60 | rms-above-2px |
| 725 | EPSG:28992 | 3.08 | 1.39 | rms-above-2px |
| 1354 | EPSG:28991 | 2.61 | 1.94 | rms-above-2px |
| 1442 | EPSG:28992 | 3.14 | 2.24 | rms-above-2px |
| 802 | EPSG:28992 | 3.30 | 2.81 | rms-above-2px |
