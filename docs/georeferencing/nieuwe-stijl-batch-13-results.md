# Nieuwe Stijl batch 13 — D.13 ready for review

> Series D.13 was approved by the user on 20 November 2026. Acceptance is recorded against the exact geometry in the [dashboard](../../dashboard/index.html). The initial processing report below is retained for provenance.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-13/review-annotations.json) contains all 11 digitized D.13 maps. The [dashboard](../../dashboard/index.html) provides a combined download and a direct Allmaps Viewer link. Human review remains pending. Sheet indices are excluded; nothing was committed.

## Results

- 11 native masks, 44 fitted controls and 11 held-out checks. Native labels and crosses, final frame/title patches, all 55 final control/check patches and 11 mask overlays were visually inspected.
- 3 pass the unchanged numerical screen; 8 retain QA flags. RMS ranges from 1.66 to 4.28 native pixels; maximum held-out error is 3.89 pixels.
- 6 maps use RD Old and 5 use RD New. Original projected coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; residuals are not survey accuracy.
- 58 cached evidence images total 8,232,144 bytes. Overviews and bounded native sections were acquired serially with at least one second between requests. No full native scans were requested.

## Corrections and verification

D.13 includes 200-metre grids, RD Old and RD New editions, faint crosses, and captions inside the frame and title boxes in different corners. Native source inspection corrected false CV proposals and resolved the printed coordinate systems. Caption notches exclude marginal text and retain cartography around the title boxes. Additional bounded sections resolved frame corners outside initial crops. Native source reviews record the corrected control proposals, frame corners, title notches and additional evidence. No overlap tie points enter the absolute fit. Geometry fingerprints bind AI visual review to the final controls and masks; human review remains separate.

## Measured processing time

The recorded preparation interval is 147.43 minutes, from 2026-11-19T20:33:22.954990+00:00 to 2026-11-19T23:00:48.803Z. This is wall-clock time from initial preparation through first export, including waits and visual review. Acquisition overlaps other series; intervals are not additive. Instrumented command durations are also available in the dashboard; helper work and model latency are not separately measured.

## Per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 1336 | EPSG:28991 | 2.48 | 2.16 | rms-above-2px |
| 713 | EPSG:28991 | 2.19 | 2.45 | rms-above-2px |
| 1338 | EPSG:28991 | 3.31 | 2.07 | rms-above-2px |
| 714 | EPSG:28992 | 1.87 | 3.89 | Pass |
| 1340 | EPSG:28991 | 4.28 | 2.42 | rms-above-2px |
| 1339 | EPSG:28992 | 2.20 | 3.54 | rms-above-2px |
| 715 | EPSG:28992 | 1.66 | 3.36 | Pass |
| 1341 | EPSG:28991 | 2.39 | 2.47 | rms-above-2px |
| 716 | EPSG:28992 | 1.67 | 0.78 | Pass |
| 1342 | EPSG:28991 | 2.26 | 1.53 | rms-above-2px |
| 744 | EPSG:28992 | 3.54 | 1.19 | rms-above-2px |
