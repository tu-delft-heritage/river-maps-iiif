# Nieuwe Stijl batch 05 — D.05 ready for review

> Series D.05 was approved by the user on 20 November 2026. Acceptance is recorded against the exact geometry in the [dashboard](../../dashboard/index.html). The initial processing report below is retained for provenance.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-05/review-annotations.json) contains all 71 previously unprocessed digitized D.05 maps. The [full-series AnnotationPage](../../dashboard/annotations/series-D.05.json) includes two accepted pilot maps, for 73 maps. The [dashboard](../../dashboard/index.html) has combined downloads and direct Allmaps Viewer links. These new maps await user review. Sheet indices are excluded; nothing was committed.

## Results

- 71 native masks, 284 fitted controls and 71 held-out checks. All source observations, final cross patches, frame/title edges and mask overlays were visually inspected.
- 31 maps pass the unchanged numerical screen; 40 retain RMS-above-two-pixels flags. RMS ranges from 0.43 to 3.08 pixels; the largest held-out error is 3.01 pixels.
- 19 maps use RD Old and 52 use RD New. Original coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; fit residuals are not survey accuracy.
- 71 cached overviews and 309 bounded sections total 62,560,106 bytes. Serial acquisition retains at least one second between requests. No full native scans were requested.

## Corrections and verification

Native evidence resolved changed grid origins and layouts, faint crosses, moved title boxes, and frame corners outside the first crop. Inventory 1070 required a corrected 500-metre northing assignment. Inventory 1082 has a different map orientation from its later editions. The original grid observations were transcribed directly; repeat-edition registration only proposed image locations. No overlap tie points enter the fit. Geometry fingerprints bind the AI visual review; human review remains pending.

## Measured processing time

The recorded preparation interval is 50.80 minutes, from 2026-11-19T19:54:16.309192+00:00 to 2026-11-19T20:45:04.365Z. It includes preparation, visual review and waits through first export. Acquisition overlaps other series, so series intervals are not additive. The dashboard also reports cumulative instrumented command durations; ad hoc helpers and model latency are not separately measured.

## Reproduction

```sh
.venv/bin/python scripts/georeferencing/georeference_batch.py hydrate --batch batch-05
.venv/bin/python scripts/georeferencing/georeference_batch.py measure --batch batch-05 --offline
node scripts/georeferencing/georeference-batch-export.ts batch-05
pnpm georeference:validate
```

## Per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 1049 | EPSG:28991 | 2.44 | 1.14 | rms-above-2px |
| 1051 | EPSG:28992 | 2.03 | 1.85 | rms-above-2px |
| 558 | EPSG:28992 | 1.41 | 0.07 | Pass |
| 1053 | EPSG:28991 | 3.08 | 1.00 | rms-above-2px |
| 1054 | EPSG:28992 | 2.36 | 2.08 | rms-above-2px |
| 1052 | EPSG:28992 | 2.57 | 1.61 | rms-above-2px |
| 559 | EPSG:28992 | 2.25 | 2.60 | rms-above-2px |
| 1055 | EPSG:28991 | 2.43 | 0.60 | rms-above-2px |
| 1056 | EPSG:28992 | 2.53 | 0.63 | rms-above-2px |
| 560 | EPSG:28992 | 2.87 | 2.48 | rms-above-2px |
| 1058 | EPSG:28992 | 2.98 | 1.55 | rms-above-2px |
| 1057 | EPSG:28992 | 2.51 | 1.60 | rms-above-2px |
| 561 | EPSG:28992 | 3.04 | 1.55 | rms-above-2px |
| 1060 | EPSG:28991 | 2.53 | 1.61 | rms-above-2px |
| 1059 | EPSG:28992 | 2.59 | 1.52 | rms-above-2px |
| 562 | EPSG:28992 | 2.77 | 2.52 | rms-above-2px |
| 1062 | EPSG:28991 | 1.09 | 1.46 | Pass |
| 1061 | EPSG:28992 | 1.87 | 1.14 | Pass |
| 563 | EPSG:28992 | 1.33 | 1.19 | Pass |
| 1064 | EPSG:28991 | 2.26 | 0.65 | rms-above-2px |
| 1063 | EPSG:28992 | 1.44 | 1.67 | Pass |
| 564 | EPSG:28992 | 1.51 | 1.52 | Pass |
| 1065 | EPSG:28991 | 1.50 | 1.52 | Pass |
| 1066 | EPSG:28992 | 2.15 | 0.58 | rms-above-2px |
| 565 | EPSG:28992 | 1.33 | 1.16 | Pass |
| 1067 | EPSG:28991 | 2.81 | 1.90 | rms-above-2px |
| 566 | EPSG:28992 | 1.32 | 1.95 | Pass |
| 1069 | EPSG:28991 | 1.86 | 1.95 | Pass |
| 1068 | EPSG:28992 | 1.74 | 1.28 | Pass |
| 567 | EPSG:28992 | 1.93 | 2.30 | Pass |
| 568 | EPSG:28992 | 1.93 | 2.84 | Pass |
| 569 | EPSG:28992 | 1.77 | 2.56 | Pass |
| 1070 | EPSG:28991 | 2.99 | 2.82 | rms-above-2px |
| 1071 | EPSG:28992 | 2.49 | 1.44 | rms-above-2px |
| 570 | EPSG:28992 | 2.15 | 3.01 | rms-above-2px |
| 1073 | EPSG:28991 | 3.08 | 1.91 | rms-above-2px |
| 1072 | EPSG:28992 | 2.62 | 2.06 | rms-above-2px |
| 571 | EPSG:28992 | 2.31 | 2.17 | rms-above-2px |
| 1074 | EPSG:28991 | 1.79 | 0.73 | Pass |
| 1075 | EPSG:28992 | 1.65 | 1.72 | Pass |
| 572 | EPSG:28992 | 0.89 | 2.56 | Pass |
| 573 | EPSG:28992 | 1.39 | 1.81 | Pass |
| 1077 | EPSG:28991 | 1.96 | 1.66 | Pass |
| 1076 | EPSG:28992 | 1.94 | 0.94 | Pass |
| 574 | EPSG:28992 | 0.87 | 1.41 | Pass |
| 1078 | EPSG:28991 | 2.76 | 1.89 | rms-above-2px |
| 1079 | EPSG:28992 | 2.27 | 0.57 | rms-above-2px |
| 575 | EPSG:28992 | 1.59 | 1.50 | Pass |
| 1082 | EPSG:28991 | 2.82 | 1.52 | rms-above-2px |
| 1081 | EPSG:28992 | 2.13 | 2.79 | rms-above-2px |
| 1080 | EPSG:28992 | 2.34 | 1.04 | rms-above-2px |
| 576 | EPSG:28992 | 2.77 | 2.00 | rms-above-2px |
| 1083 | EPSG:28991 | 2.26 | 1.95 | rms-above-2px |
| 577 | EPSG:28991 | 1.52 | 1.20 | Pass |
| 1084 | EPSG:28991 | 2.56 | 1.51 | rms-above-2px |
| 578 | EPSG:28991 | 1.77 | 0.96 | Pass |
| 727 | EPSG:28992 | 2.50 | 1.43 | rms-above-2px |
| 1358 | EPSG:28992 | 2.92 | 2.75 | rms-above-2px |
| 728 | EPSG:28992 | 2.52 | 1.26 | rms-above-2px |
| 729 | EPSG:28992 | 1.41 | 3.00 | Pass |
| 730 | EPSG:28992 | 1.91 | 1.59 | Pass |
| 731 | EPSG:28992 | 2.05 | 2.25 | rms-above-2px |
| 732 | EPSG:28992 | 1.27 | 1.08 | Pass |
| 733 | EPSG:28992 | 2.32 | 1.67 | rms-above-2px |
| 734 | EPSG:28992 | 1.46 | 1.22 | Pass |
| 735 | EPSG:28992 | 2.10 | 1.63 | rms-above-2px |
| 736 | EPSG:28992 | 2.64 | 1.36 | rms-above-2px |
| 737 | EPSG:28992 | 2.95 | 2.55 | rms-above-2px |
| 738 | EPSG:28992 | 0.84 | 2.14 | Pass |
| 739 | EPSG:28992 | 0.79 | 0.91 | Pass |
| 740 | EPSG:28992 | 0.43 | 1.61 | Pass |
