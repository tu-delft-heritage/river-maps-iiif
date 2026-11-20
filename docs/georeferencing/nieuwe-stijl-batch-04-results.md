# Nieuwe Stijl batch 04 — D.04 ready for review

> Series D.04 was approved by the user on 20 November 2026. Acceptance is recorded against the exact geometry in the [dashboard](../../dashboard/index.html). The initial processing report below is retained for provenance.


The [batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-04/review-annotations.json) contains all 143 previously unprocessed digitized D.04 maps. The [full-series AnnotationPage](../../dashboard/annotations/series-D.04.json) also includes the two accepted pilot maps, for 145 maps. The [dashboard](../../dashboard/index.html) provides combined downloads and direct Allmaps Viewer `#data=` links. Sheet indices and undigitized material are excluded. These new maps await the user's review; nothing was committed, pushed or deployed.

## Results

- 143 native-pixel masks, 572 fitted controls and 143 held-out checks; all masks, native frame/title edges, border labels and 715 cross-centre patches were visually inspected.
- 45 maps pass the unchanged numerical screen. 98 retain numerical flags: 97 have RMS above two pixels, and inventories 546 and 552 have held-out errors above five pixels (552 has both flags).
- RMS ranges from 0.83 to 3.98 native pixels. The largest held-out error is 5.39 pixels. The largest sampled Allmaps Mercator polynomial1/RD-affine difference is 0.86 ground metres.
- 41 scans use RD Old (EPSG:28991) and 102 use RD New (EPSG:28992). Original coordinates, printed units, source metadata, border transcriptions and evidence checksums are retained.
- Geometry fingerprints bind the AI visual review. Numerical flags remain; visual review does not establish survey accuracy or release eligibility. Controls and checks share border anchors.

## Evidence and corrections

The saved evidence comprises 143 overviews and 601 bounded native sections, totalling 127,277,263 bytes. Acquisition used a serial queue with at least one second between requests. Additional narrow sections resolved frame corners outside the initial crop. No full native-resolution scans were requested. Measurement and export run offline.

CV registration, cross templates and redundant grid consistency supplied proposals. Native evidence resolved changed grid origins, moved title boxes, faint crosses and incorrect proposed grid intervals. Inventories 1035 and 1036 required corrected northing assignments, and 552 required corrected easting assignments; the source corrections remain documented. Inventory 1030 contains a duplicated printed northing label: the literal transcription is preserved with an explanation of how the surrounding grid resolves it. No overlap tie points enter the absolute fit.

## Measured processing time

The instrumented preparation interval was 46.65 minutes, from 2026-11-19T19:36:51.768519+00:00 to 2026-11-19T20:23:30.740Z. This elapsed interval includes preparation, AI visual checks and waits through the first export, not just CPU time. The dashboard separately reports cumulative durations of instrumented commands; ad hoc scripts and model latency are not separately measured. Later replays preserve the first completion interval.

## Reproduction

```sh
.venv/bin/python scripts/georeferencing/georeference_batch.py hydrate --batch batch-04
.venv/bin/python scripts/georeferencing/georeference_batch.py measure --batch batch-04 --offline
node scripts/georeferencing/georeference-batch-export.ts batch-04
pnpm georeference:validate
```

## Per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 946 | EPSG:28991 | 1.76 | 0.03 | Pass |
| 941 | EPSG:28992 | 1.41 | 1.21 | Pass |
| 945 | EPSG:28992 | 1.33 | 0.13 | Pass |
| 943 | EPSG:28992 | 1.02 | 0.54 | Pass |
| 944 | EPSG:28992 | 1.60 | 0.80 | Pass |
| 942 | EPSG:28992 | 2.01 | 2.35 | rms-above-2px |
| 520 | EPSG:28992 | 2.08 | 2.97 | rms-above-2px |
| 519 | EPSG:28992 | 1.61 | 3.29 | Pass |
| 953 | EPSG:28991 | 2.27 | 2.68 | rms-above-2px |
| 950 | EPSG:28991 | 1.81 | 1.45 | Pass |
| 952 | EPSG:28992 | 1.93 | 1.45 | Pass |
| 951 | EPSG:28992 | 0.90 | 0.89 | Pass |
| 521 | EPSG:28992 | 0.83 | 1.74 | Pass |
| 955 | EPSG:28991 | 2.16 | 1.85 | rms-above-2px |
| 956 | EPSG:28992 | 2.30 | 1.11 | rms-above-2px |
| 957 | EPSG:28992 | 2.91 | 0.50 | rms-above-2px |
| 954 | EPSG:28992 | 3.14 | 0.85 | rms-above-2px |
| 522 | EPSG:28992 | 2.41 | 3.03 | rms-above-2px |
| 960 | EPSG:28991 | 1.95 | 3.20 | Pass |
| 958 | EPSG:28992 | 1.53 | 2.67 | Pass |
| 959 | EPSG:28992 | 2.27 | 4.93 | rms-above-2px |
| 961 | EPSG:28992 | 2.25 | 3.10 | rms-above-2px |
| 523 | EPSG:28992 | 0.84 | 3.33 | Pass |
| 965 | EPSG:28991 | 2.62 | 3.05 | rms-above-2px |
| 963 | EPSG:28992 | 2.07 | 1.55 | rms-above-2px |
| 964 | EPSG:28992 | 2.09 | 1.40 | rms-above-2px |
| 962 | EPSG:28992 | 2.08 | 1.90 | rms-above-2px |
| 524 | EPSG:28992 | 2.06 | 1.82 | rms-above-2px |
| 968 | EPSG:28991 | 3.18 | 2.46 | rms-above-2px |
| 967 | EPSG:28992 | 3.02 | 2.61 | rms-above-2px |
| 969 | EPSG:28992 | 2.62 | 2.00 | rms-above-2px |
| 966 | EPSG:28992 | 2.59 | 0.97 | rms-above-2px |
| 525 | EPSG:28992 | 1.70 | 2.09 | Pass |
| 971 | EPSG:28991 | 2.67 | 4.35 | rms-above-2px |
| 970 | EPSG:28992 | 3.00 | 3.84 | rms-above-2px |
| 972 | EPSG:28992 | 2.96 | 2.97 | rms-above-2px |
| 973 | EPSG:28992 | 2.73 | 1.20 | rms-above-2px |
| 526 | EPSG:28992 | 2.52 | 3.46 | rms-above-2px |
| 977 | EPSG:28991 | 2.22 | 0.90 | rms-above-2px |
| 976 | EPSG:28992 | 1.55 | 1.80 | Pass |
| 975 | EPSG:28992 | 1.81 | 1.72 | Pass |
| 974 | EPSG:28992 | 2.45 | 1.84 | rms-above-2px |
| 527 | EPSG:28992 | 1.43 | 1.52 | Pass |
| 978 | EPSG:28991 | 2.23 | 2.91 | rms-above-2px |
| 979 | EPSG:28992 | 3.02 | 2.28 | rms-above-2px |
| 980 | EPSG:28992 | 2.43 | 0.70 | rms-above-2px |
| 528 | EPSG:28992 | 2.22 | 3.31 | rms-above-2px |
| 982 | EPSG:28991 | 2.49 | 3.42 | rms-above-2px |
| 983 | EPSG:28991 | 2.32 | 0.52 | rms-above-2px |
| 981 | EPSG:28992 | 2.90 | 2.94 | rms-above-2px |
| 529 | EPSG:28992 | 1.99 | 4.01 | Pass |
| 986 | EPSG:28991 | 2.50 | 2.51 | rms-above-2px |
| 985 | EPSG:28992 | 1.96 | 2.79 | Pass |
| 984 | EPSG:28992 | 2.79 | 1.20 | rms-above-2px |
| 530 | EPSG:28992 | 2.64 | 2.68 | rms-above-2px |
| 988 | EPSG:28991 | 2.64 | 0.57 | rms-above-2px |
| 987 | EPSG:28992 | 2.66 | 1.91 | rms-above-2px |
| 989 | EPSG:28992 | 2.89 | 1.44 | rms-above-2px |
| 531 | EPSG:28992 | 2.66 | 1.34 | rms-above-2px |
| 991 | EPSG:28991 | 2.89 | 3.12 | rms-above-2px |
| 992 | EPSG:28992 | 2.72 | 1.26 | rms-above-2px |
| 990 | EPSG:28992 | 2.76 | 1.77 | rms-above-2px |
| 532 | EPSG:28992 | 2.83 | 1.86 | rms-above-2px |
| 994 | EPSG:28991 | 2.67 | 2.13 | rms-above-2px |
| 993 | EPSG:28992 | 2.23 | 1.68 | rms-above-2px |
| 995 | EPSG:28992 | 2.55 | 1.29 | rms-above-2px |
| 533 | EPSG:28992 | 2.19 | 3.53 | rms-above-2px |
| 998 | EPSG:28991 | 2.10 | 2.40 | rms-above-2px |
| 996 | EPSG:28992 | 1.85 | 1.45 | Pass |
| 997 | EPSG:28992 | 1.92 | 1.48 | Pass |
| 534 | EPSG:28992 | 1.99 | 3.65 | Pass |
| 1001 | EPSG:28991 | 2.84 | 2.85 | rms-above-2px |
| 1000 | EPSG:28992 | 1.73 | 3.16 | Pass |
| 999 | EPSG:28992 | 2.56 | 2.90 | rms-above-2px |
| 535 | EPSG:28992 | 1.69 | 1.92 | Pass |
| 1002 | EPSG:28991 | 2.46 | 0.88 | rms-above-2px |
| 1003 | EPSG:28992 | 2.14 | 1.51 | rms-above-2px |
| 536 | EPSG:28992 | 2.07 | 1.69 | rms-above-2px |
| 1006 | EPSG:28991 | 1.48 | 0.82 | Pass |
| 1005 | EPSG:28992 | 1.79 | 1.00 | Pass |
| 1004 | EPSG:28992 | 1.78 | 0.78 | Pass |
| 537 | EPSG:28992 | 1.32 | 1.95 | Pass |
| 1008 | EPSG:28991 | 1.58 | 2.85 | Pass |
| 1007 | EPSG:28992 | 1.43 | 1.93 | Pass |
| 538 | EPSG:28992 | 2.15 | 3.82 | rms-above-2px |
| 1011 | EPSG:28991 | 2.65 | 3.31 | rms-above-2px |
| 1010 | EPSG:28991 | 2.01 | 3.33 | rms-above-2px |
| 1009 | EPSG:28992 | 2.80 | 0.94 | rms-above-2px |
| 1014 | EPSG:28991 | 3.03 | 1.87 | rms-above-2px |
| 1013 | EPSG:28991 | 2.54 | 1.25 | rms-above-2px |
| 1012 | EPSG:28992 | 2.29 | 1.76 | rms-above-2px |
| 539 | EPSG:28992 | 2.98 | 1.00 | rms-above-2px |
| 1017 | EPSG:28991 | 2.20 | 1.64 | rms-above-2px |
| 1016 | EPSG:28991 | 2.13 | 1.56 | rms-above-2px |
| 1015 | EPSG:28992 | 2.70 | 2.57 | rms-above-2px |
| 540 | EPSG:28992 | 1.27 | 1.19 | Pass |
| 1020 | EPSG:28991 | 2.47 | 2.70 | rms-above-2px |
| 1021 | EPSG:28991 | 2.41 | 3.75 | rms-above-2px |
| 1019 | EPSG:28992 | 2.59 | 3.35 | rms-above-2px |
| 1018 | EPSG:28992 | 2.63 | 2.61 | rms-above-2px |
| 541 | EPSG:28992 | 2.21 | 3.27 | rms-above-2px |
| 543 | EPSG:28992 | 2.35 | 2.37 | rms-above-2px |
| 1024 | EPSG:28991 | 2.38 | 3.37 | rms-above-2px |
| 1023 | EPSG:28991 | 2.44 | 1.89 | rms-above-2px |
| 1022 | EPSG:28992 | 1.76 | 4.03 | Pass |
| 544 | EPSG:28992 | 1.72 | 4.27 | Pass |
| 545 | EPSG:28992 | 1.53 | 4.03 | Pass |
| 546 | EPSG:28992 | 1.47 | 5.10 | check-above-5px |
| 1027 | EPSG:28991 | 2.50 | 1.43 | rms-above-2px |
| 1026 | EPSG:28991 | 2.45 | 1.48 | rms-above-2px |
| 1025 | EPSG:28992 | 2.65 | 2.93 | rms-above-2px |
| 547 | EPSG:28992 | 2.42 | 3.06 | rms-above-2px |
| 1029 | EPSG:28991 | 2.71 | 1.82 | rms-above-2px |
| 1028 | EPSG:28991 | 2.72 | 1.48 | rms-above-2px |
| 1030 | EPSG:28992 | 2.40 | 2.00 | rms-above-2px |
| 548 | EPSG:28992 | 1.14 | 1.27 | Pass |
| 1032 | EPSG:28991 | 1.02 | 0.80 | Pass |
| 1031 | EPSG:28992 | 2.11 | 2.04 | rms-above-2px |
| 549 | EPSG:28992 | 2.94 | 4.17 | rms-above-2px |
| 1033 | EPSG:28991 | 1.53 | 2.37 | Pass |
| 1034 | EPSG:28992 | 2.26 | 1.35 | rms-above-2px |
| 550 | EPSG:28992 | 2.60 | 2.70 | rms-above-2px |
| 1036 | EPSG:28991 | 2.12 | 0.74 | rms-above-2px |
| 1035 | EPSG:28992 | 2.13 | 1.65 | rms-above-2px |
| 551 | EPSG:28992 | 2.46 | 2.78 | rms-above-2px |
| 1037 | EPSG:28991 | 1.89 | 1.86 | Pass |
| 1038 | EPSG:28992 | 2.00 | 0.85 | rms-above-2px |
| 552 | EPSG:28992 | 3.98 | 5.39 | rms-above-2px, check-above-5px |
| 1040 | EPSG:28991 | 2.23 | 3.91 | rms-above-2px |
| 1039 | EPSG:28992 | 2.16 | 2.04 | rms-above-2px |
| 553 | EPSG:28992 | 1.07 | 1.68 | Pass |
| 1041 | EPSG:28991 | 1.63 | 1.68 | Pass |
| 1042 | EPSG:28992 | 1.84 | 1.28 | Pass |
| 1043 | EPSG:28992 | 1.86 | 1.26 | Pass |
| 554 | EPSG:28992 | 2.10 | 3.07 | rms-above-2px |
| 1045 | EPSG:28992 | 2.05 | 1.36 | rms-above-2px |
| 1044 | EPSG:28992 | 1.87 | 2.52 | Pass |
| 555 | EPSG:28992 | 1.24 | 3.00 | Pass |
| 1047 | EPSG:28992 | 2.73 | 1.71 | rms-above-2px |
| 1046 | EPSG:28992 | 2.77 | 4.18 | rms-above-2px |
| 556 | EPSG:28992 | 2.92 | 4.51 | rms-above-2px |
| 1048 | EPSG:28992 | 2.63 | 1.64 | rms-above-2px |
| 557 | EPSG:28992 | 0.83 | 0.66 | Pass |
