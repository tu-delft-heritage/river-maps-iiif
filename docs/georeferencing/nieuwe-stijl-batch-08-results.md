# Nieuwe Stijl batch 08 — D.08 visually approved

> Follow-up on 20 November: the user approved the corrected placements and the complete D.08 series. See the [eight-map review report](nieuwe-stijl-review-2026-11-20.md) and the dashboard for current placements. The original export diagnostics below are retained as the processing history.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-08/review-annotations.json) contains all 107 digitized D.08 maps. The [dashboard](../../dashboard/index.html) provides a combined download and a direct Allmaps Viewer link. The complete series is visually approved. Sheet indices are excluded; nothing was committed.

## Initial export results

- 107 native masks, 428 fitted controls and 107 held-out checks. Native labels and crosses, final frame/title patches, all 535 final control/check patches and 107 mask overlays were visually inspected.
- 52 pass the unchanged numerical screen; 55 retain QA flags. RMS ranges from 0.52 to 3.61 native pixels; maximum held-out error is 4.35 pixels.
- 32 maps use RD Old and 75 use RD New. Original projected coordinates, printed labels, units, metadata and evidence checksums are retained. Controls and checks share border anchors; residuals are not survey accuracy.
- 681 cached evidence images total 118,170,956 bytes. Overviews and bounded native sections were acquired serially with at least one second between requests. No full native scans were requested.

## Corrections and verification

D.08 includes 200-metre grids, editions with RD Old or RD New coordinates, changed extents, faint crosses and title boxes along the side of the frame. Native source inspection corrected false CV proposals and resolved the printed coordinate systems. Side notches retain cartography above and below title boxes; caption notches exclude marginal text. Additional bounded sections resolved frame corners outside initial crops. Final control and frame corrections are recorded in `final-visual-corrections.json`. No overlap tie points enter the absolute fit. Geometry fingerprints bind AI visual review to the final controls and masks; human review remains separate.

## Measured processing time

The recorded preparation interval is 115.42 minutes, from 2026-11-19T20:08:25.899885+00:00 to 2026-11-19T22:03:51.296Z. This is wall-clock time from initial preparation through first export, including waits and visual review. Acquisition overlaps other series; intervals are not additive. Instrumented command durations are also available in the dashboard; helper work and model latency are not separately measured.

## Original per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 1138 | EPSG:28992 | 2.27 | 1.89 | rms-above-2px |
| 1137 | EPSG:28992 | 2.58 | 1.11 | rms-above-2px |
| 620 | EPSG:28992 | 3.10 | 3.06 | rms-above-2px |
| 621 | EPSG:28992 | 2.94 | 2.32 | rms-above-2px |
| 1141 | EPSG:28991 | 2.20 | 3.52 | rms-above-2px |
| 1142 | EPSG:28992 | 2.83 | 2.35 | rms-above-2px |
| 622 | EPSG:28992 | 2.22 | 1.08 | rms-above-2px |
| 1250 | EPSG:28991 | 2.98 | 0.28 | rms-above-2px |
| 1144 | EPSG:28991 | 2.72 | 0.96 | rms-above-2px |
| 1143 | EPSG:28992 | 1.96 | 1.18 | Pass |
| 623 | EPSG:28992 | 2.90 | 1.70 | rms-above-2px |
| 1146 | EPSG:28991 | 2.44 | 1.60 | rms-above-2px |
| 1145 | EPSG:28992 | 2.12 | 1.77 | rms-above-2px |
| 1147 | EPSG:28992 | 1.09 | 1.34 | Pass |
| 624 | EPSG:28992 | 1.05 | 1.73 | Pass |
| 1249 | EPSG:28991 | 2.97 | 0.79 | rms-above-2px |
| 1150 | EPSG:28991 | 3.01 | 3.15 | rms-above-2px |
| 1149 | EPSG:28992 | 2.56 | 1.69 | rms-above-2px |
| 1148 | EPSG:28992 | 2.27 | 0.70 | rms-above-2px |
| 1151 | EPSG:28992 | 1.87 | 0.50 | Pass |
| 625 | EPSG:28992 | 1.77 | 2.59 | Pass |
| 1154 | EPSG:28991 | 3.21 | 2.33 | rms-above-2px |
| 1153 | EPSG:28992 | 2.37 | 1.95 | rms-above-2px |
| 1155 | EPSG:28992 | 1.73 | 0.98 | Pass |
| 1152 | EPSG:28992 | 1.68 | 1.41 | Pass |
| 626 | EPSG:28992 | 1.61 | 1.78 | Pass |
| 1156 | EPSG:28991 | 1.96 | 2.72 | Pass |
| 630 | EPSG:28992 | 2.41 | 2.05 | rms-above-2px |
| 1158 | EPSG:28991 | 2.35 | 0.64 | rms-above-2px |
| 1159 | EPSG:28992 | 2.43 | 1.88 | rms-above-2px |
| 1160 | EPSG:28992 | 1.73 | 1.37 | Pass |
| 628 | EPSG:28992 | 2.16 | 1.39 | rms-above-2px |
| 1157 | EPSG:28992 | 1.85 | 1.63 | Pass |
| 627 | EPSG:28992 | 1.98 | 1.45 | Pass |
| 1161 | EPSG:28991 | 1.55 | 1.69 | Pass |
| 1162 | EPSG:28992 | 1.94 | 1.06 | Pass |
| 629 | EPSG:28992 | 1.49 | 1.19 | Pass |
| 1164 | EPSG:28991 | 2.44 | 0.67 | rms-above-2px |
| 1163 | EPSG:28992 | 2.08 | 1.71 | rms-above-2px |
| 631 | EPSG:28992 | 1.45 | 1.13 | Pass |
| 1167 | EPSG:28991 | 1.23 | 1.57 | Pass |
| 1166 | EPSG:28992 | 1.93 | 1.57 | Pass |
| 1165 | EPSG:28992 | 1.52 | 1.20 | Pass |
| 632 | EPSG:28992 | 0.94 | 4.35 | Pass |
| 1168 | EPSG:28991 | 1.88 | 1.48 | Pass |
| 1169 | EPSG:28992 | 2.07 | 0.93 | rms-above-2px |
| 1170 | EPSG:28992 | 1.08 | 0.65 | Pass |
| 633 | EPSG:28992 | 2.76 | 1.09 | rms-above-2px |
| 1172 | EPSG:28991 | 1.71 | 3.67 | Pass |
| 1171 | EPSG:28992 | 1.00 | 1.49 | Pass |
| 1173 | EPSG:28992 | 1.57 | 3.65 | Pass |
| 634 | EPSG:28992 | 1.64 | 3.77 | Pass |
| 1174 | EPSG:28991 | 3.03 | 1.69 | rms-above-2px |
| 1175 | EPSG:28992 | 1.52 | 1.74 | Pass |
| 1176 | EPSG:28992 | 1.61 | 1.17 | Pass |
| 635 | EPSG:28992 | 1.69 | 0.92 | Pass |
| 1178 | EPSG:28991 | 1.88 | 1.52 | Pass |
| 1177 | EPSG:28992 | 1.93 | 0.59 | Pass |
| 1179 | EPSG:28992 | 1.79 | 1.28 | Pass |
| 636 | EPSG:28992 | 1.83 | 1.06 | Pass |
| 1182 | EPSG:28991 | 2.22 | 0.95 | rms-above-2px |
| 1181 | EPSG:28992 | 2.80 | 1.99 | rms-above-2px |
| 1180 | EPSG:28992 | 2.29 | 2.24 | rms-above-2px |
| 637 | EPSG:28992 | 2.27 | 2.20 | rms-above-2px |
| 1184 | EPSG:28991 | 1.17 | 0.51 | Pass |
| 1183 | EPSG:28992 | 1.35 | 0.53 | Pass |
| 638 | EPSG:28992 | 1.27 | 0.52 | Pass |
| 1185 | EPSG:28991 | 1.67 | 0.21 | Pass |
| 1186 | EPSG:28992 | 2.72 | 1.77 | rms-above-2px |
| 639 | EPSG:28992 | 1.35 | 3.05 | Pass |
| 1188 | EPSG:28991 | 2.39 | 3.66 | rms-above-2px |
| 1187 | EPSG:28992 | 2.18 | 2.28 | rms-above-2px |
| 640 | EPSG:28992 | 1.76 | 1.65 | Pass |
| 1190 | EPSG:28991 | 1.07 | 1.28 | Pass |
| 1191 | EPSG:28991 | 1.82 | 2.43 | Pass |
| 1189 | EPSG:28992 | 2.73 | 1.81 | rms-above-2px |
| 641 | EPSG:28992 | 2.83 | 1.49 | rms-above-2px |
| 1193 | EPSG:28991 | 2.23 | 2.95 | rms-above-2px |
| 1192 | EPSG:28992 | 2.46 | 1.86 | rms-above-2px |
| 642 | EPSG:28992 | 2.03 | 2.90 | rms-above-2px |
| 1195 | EPSG:28991 | 1.80 | 3.54 | Pass |
| 1196 | EPSG:28991 | 2.35 | 2.39 | rms-above-2px |
| 1194 | EPSG:28992 | 1.41 | 1.09 | Pass |
| 643 | EPSG:28992 | 1.97 | 0.96 | Pass |
| 1197 | EPSG:28991 | 2.23 | 0.83 | rms-above-2px |
| 1198 | EPSG:28992 | 1.60 | 1.85 | Pass |
| 644 | EPSG:28992 | 1.69 | 0.59 | Pass |
| 1200 | EPSG:28991 | 2.89 | 1.90 | rms-above-2px |
| 1199 | EPSG:28992 | 2.12 | 1.88 | rms-above-2px |
| 645 | EPSG:28992 | 2.09 | 2.41 | rms-above-2px |
| 1202 | EPSG:28991 | 0.94 | 3.25 | Pass |
| 1201 | EPSG:28991 | 0.52 | 2.48 | Pass |
| 1203 | EPSG:28992 | 1.91 | 1.92 | Pass |
| 646 | EPSG:28992 | 0.99 | 1.97 | Pass |
| 1205 | EPSG:28991 | 1.96 | 0.33 | Pass |
| 1204 | EPSG:28992 | 2.86 | 0.68 | rms-above-2px |
| 647 | EPSG:28992 | 2.07 | 2.25 | rms-above-2px |
| 1206 | EPSG:28991 | 2.59 | 2.03 | rms-above-2px |
| 648 | EPSG:28992 | 2.16 | 1.73 | rms-above-2px |
| 1207 | EPSG:28991 | 2.30 | 2.02 | rms-above-2px |
| 1208 | EPSG:28992 | 2.28 | 2.21 | rms-above-2px |
| 649 | EPSG:28992 | 2.92 | 1.51 | rms-above-2px |
| 1209 | EPSG:28992 | 1.98 | 1.65 | Pass |
| 650 | EPSG:28992 | 2.16 | 1.60 | rms-above-2px |
| 651 | EPSG:28992 | 2.49 | 2.31 | rms-above-2px |
| 1211 | EPSG:28992 | 2.39 | 1.69 | rms-above-2px |
| 653 | EPSG:28992 | 3.61 | 1.59 | rms-above-2px |
