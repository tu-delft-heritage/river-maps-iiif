# Nieuwe Stijl batch 06 — D.06 ready for review

> Series D.06 was approved by the user on 20 November 2026. Acceptance is recorded against the exact geometry in the [dashboard](../../dashboard/index.html). The initial processing report below is retained for provenance.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-06/review-annotations.json) contains all 37 digitized D.06 maps. The [dashboard](../../dashboard/index.html) has a combined download and a direct Allmaps Viewer link. These maps await user review. Sheet indices are excluded; nothing was committed.

## Results

- 37 native masks, 148 fitted controls and 37 held-out checks. All source observations, final cross patches, frame/title edges and mask overlays were visually inspected.
- Four maps pass the unchanged numerical screen; 33 retain RMS-above-two-pixels flags. RMS ranges from 1.52 to 3.72 pixels; the largest held-out error is 3.32 pixels.
- Eight maps use RD Old and 29 use RD New. Original coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; fit residuals are not survey accuracy.
- 37 cached overviews and 207 bounded sections total 38,731,987 bytes. Serial acquisition retains at least one second between requests. No full native scans were requested.

## Corrections and verification

Native evidence resolved rotated earlier editions, false cross candidates on roads, faint labels, top-corner titles, central bottom tables, and frame corners outside initial crops. Inventory 1086 has a different grid orientation from its later editions. Inventory 589 prints 415.0 at the row corresponding to 415.5 on the opposite border; the printed text and interpretation are retained. Labels without a visible decimal separator on 1098, 1099 and 1104 retain explicit metre interpretations. No overlap tie points enter the fit. Geometry fingerprints bind the AI visual review; human review remains pending.

## Measured processing time

The recorded preparation interval is 57.41 minutes, from 2026-11-19T20:00:48.040104+00:00 to 2026-11-19T20:58:12.843Z. It includes preparation, visual review and waits through first export. Acquisition overlaps other series, so series intervals are not additive. The dashboard also reports cumulative instrumented command durations; ad hoc helpers and model latency are not separately measured.

## Reproduction

```sh
.venv/bin/python scripts/georeferencing/georeference_batch.py hydrate --batch batch-06
.venv/bin/python scripts/georeferencing/georeference_batch.py measure --batch batch-06 --offline
node scripts/georeferencing/georeference-batch-export.ts batch-06
pnpm georeference:validate
```

## Per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 1086 | EPSG:28991 | 2.58 | 0.81 | rms-above-2px |
| 1087 | EPSG:28992 | 1.87 | 2.11 | Pass |
| 579 | EPSG:28992 | 2.04 | 2.27 | rms-above-2px |
| 1090 | EPSG:28991 | 2.51 | 0.88 | rms-above-2px |
| 1089 | EPSG:28991 | 2.96 | 2.24 | rms-above-2px |
| 580 | EPSG:28991 | 2.81 | 1.78 | rms-above-2px |
| 1088 | EPSG:28991 | 2.38 | 0.58 | rms-above-2px |
| 1092 | EPSG:28991 | 2.30 | 2.18 | rms-above-2px |
| 1091 | EPSG:28991 | 1.82 | 2.79 | Pass |
| 581 | EPSG:28991 | 2.06 | 1.41 | rms-above-2px |
| 1093 | EPSG:28992 | 2.63 | 0.64 | rms-above-2px |
| 1094 | EPSG:28992 | 3.03 | 0.45 | rms-above-2px |
| 582 | EPSG:28992 | 3.29 | 1.53 | rms-above-2px |
| 583 | EPSG:28992 | 3.16 | 1.39 | rms-above-2px |
| 1095 | EPSG:28992 | 2.80 | 2.26 | rms-above-2px |
| 584 | EPSG:28992 | 3.63 | 3.32 | rms-above-2px |
| 585 | EPSG:28992 | 3.72 | 3.07 | rms-above-2px |
| 586 | EPSG:28992 | 2.65 | 1.87 | rms-above-2px |
| 1096 | EPSG:28992 | 2.45 | 1.79 | rms-above-2px |
| 587 | EPSG:28992 | 2.59 | 0.91 | rms-above-2px |
| 1097 | EPSG:28992 | 2.26 | 1.93 | rms-above-2px |
| 588 | EPSG:28992 | 1.52 | 1.63 | Pass |
| 1099 | EPSG:28992 | 2.37 | 1.08 | rms-above-2px |
| 1098 | EPSG:28992 | 2.30 | 1.64 | rms-above-2px |
| 589 | EPSG:28992 | 2.02 | 2.27 | rms-above-2px |
| 590 | EPSG:28992 | 3.49 | 2.80 | rms-above-2px |
| 1100 | EPSG:28992 | 2.61 | 1.01 | rms-above-2px |
| 591 | EPSG:28992 | 2.55 | 2.46 | rms-above-2px |
| 1102 | EPSG:28992 | 2.61 | 1.10 | rms-above-2px |
| 1101 | EPSG:28992 | 2.57 | 1.50 | rms-above-2px |
| 592 | EPSG:28992 | 3.12 | 2.65 | rms-above-2px |
| 1103 | EPSG:28992 | 1.87 | 2.11 | Pass |
| 593 | EPSG:28992 | 2.21 | 1.09 | rms-above-2px |
| 1104 | EPSG:28992 | 2.28 | 1.42 | rms-above-2px |
| 594 | EPSG:28992 | 2.55 | 2.98 | rms-above-2px |
| 1105 | EPSG:28992 | 2.48 | 2.01 | rms-above-2px |
| 595 | EPSG:28992 | 2.47 | 1.17 | rms-above-2px |
