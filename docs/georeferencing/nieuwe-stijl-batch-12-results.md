# Nieuwe Stijl batch 12 — D.12 ready for review

> Series D.12 was approved by the user on 20 November 2026. Acceptance is recorded against the exact geometry in the [dashboard](../../dashboard/index.html). The initial processing report below is retained for provenance.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-12/review-annotations.json) contains all 15 digitized D.12 maps. The [dashboard](../../dashboard/index.html) provides a combined download and a direct Allmaps Viewer link. Human review remains pending. Sheet indices are excluded; nothing was committed.

## Results

- 15 native masks, 60 fitted controls and 15 held-out checks. Native labels and crosses, final frame/title patches, all 75 final control/check patches and 15 mask overlays were visually inspected.
- 0 pass the unchanged numerical screen; 15 retain QA flags. RMS ranges from 2.32 to 3.54 native pixels; maximum held-out error is 3.68 pixels.
- 7 maps use RD Old and 8 use RD New. Original projected coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; residuals are not survey accuracy.
- 78 cached evidence images total 12,859,302 bytes. Overviews and bounded native sections were acquired serially with at least one second between requests. No full native scans were requested.

## Corrections and verification

D.12 includes 200-metre grids, RD Old and RD New editions, faint crosses, and changed map orientations between editions. Native source inspection corrected false CV proposals and resolved the printed coordinate systems. Caption notches exclude marginal text and retain cartography around the title boxes. Additional bounded sections resolved frame corners outside initial crops. Native source reviews record the corrected control proposals, frame corners, title notches and additional evidence. No overlap tie points enter the absolute fit. Geometry fingerprints bind AI visual review to the final controls and masks; human review remains separate.

## Measured processing time

The recorded preparation interval is 143.53 minutes, from 2026-11-19T20:32:04.979362+00:00 to 2026-11-19T22:55:36.646Z. This is wall-clock time from initial preparation through first export, including waits and visual review. Acquisition overlaps other series; intervals are not additive. Instrumented command durations are also available in the dashboard; helper work and model latency are not separately measured.

## Per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 706 | EPSG:28992 | 2.50 | 2.70 | rms-above-2px |
| 1328 | EPSG:28991 | 2.48 | 2.47 | rms-above-2px |
| 707 | EPSG:28992 | 2.91 | 3.68 | rms-above-2px |
| 1329 | EPSG:28991 | 3.31 | 1.20 | rms-above-2px |
| 708 | EPSG:28992 | 2.39 | 1.72 | rms-above-2px |
| 1330 | EPSG:28991 | 3.54 | 2.09 | rms-above-2px |
| 709 | EPSG:28992 | 3.31 | 3.11 | rms-above-2px |
| 1331 | EPSG:28991 | 3.08 | 2.02 | rms-above-2px |
| 710 | EPSG:28992 | 2.94 | 2.20 | rms-above-2px |
| 1332 | EPSG:28991 | 2.38 | 1.38 | rms-above-2px |
| 711 | EPSG:28992 | 2.53 | 0.23 | rms-above-2px |
| 1333 | EPSG:28991 | 2.72 | 0.85 | rms-above-2px |
| 1335 | EPSG:28991 | 2.32 | 0.91 | rms-above-2px |
| 1334 | EPSG:28992 | 2.88 | 2.24 | rms-above-2px |
| 712 | EPSG:28992 | 2.63 | 1.24 | rms-above-2px |
