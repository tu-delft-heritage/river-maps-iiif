# Nieuwe Stijl batch 03 — D.03 visually accepted

The [new-batch AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-03/review-annotations.json) contains all 81 previously unprocessed digitized maps in D.03. The [full-series AnnotationPage](../../dashboard/annotations/series-D.03.json) contains 83 maps, including two previously accepted pilot maps. The [dashboard](../../dashboard/index.html) provides direct Allmaps Viewer `#data=` links and JSON downloads for both. Sheet indices and undigitized material are excluded.

The user accepted D.03 on 2026-11-19: all 83 maps are now visually accepted. Together with the pilot and batches 01–02, 179 maps are accepted. Current totals for subsequent series appear on the dashboard. Exact geometry fingerprints bind this acceptance; numerical flags are retained. Nothing was committed, pushed or deployed.

## Results

- 81 individual native-pixel masks, 324 fitted controls and 81 held-out check points.
- 26 maps pass the unchanged numerical screen; 55 retain the two-pixel RMS flag. No held-out check exceeds five pixels.
- Fit RMS ranges from 0.36 to 3.49 native pixels; held-out errors range from 0.39 to 4.93 pixels.
- 32 scans use RD Old (EPSG:28991), and 49 use RD New (EPSG:28992). Original coordinates and printed units are retained alongside normalized RD New and WGS84 coordinates. Source metadata, border transcriptions and evidence checksums remain in canonical records.
- All 81 final masks and 405 cross-centre patches were visually inspected, together with native frame, title and border evidence. Exact geometry snapshots invalidate review if the observations change.
- The maximum sampled difference between Allmaps' Mercator polynomial1 transform and the authoritative RD affine is 0.89 ground metres. This is a numerical compatibility check, not independent positional validation.

## Acquisition and lessons applied

The cache contains 81 overviews and 326 native sections: 407 images totalling 62,372,171 bytes. Requests were serial and throttled at least one second apart. Two additional narrow sections resolved ambiguous frame corners on inventories 896 and 903. The failed first attempt to acquire an adaptive section is retained in the timing ledger; it produced no cached image. No whole native-resolution scans were requested. Subsequent measurement and export were offline.

Repeat-edition SIFT/RANSAC registration and bounded cross-template searches supplied proposals only. Every map's printed coordinates and grid assignment were checked; several proposals selected lettering or the adjacent grid line. Inventories 911 and 912 required a 500-metre northing correction at two proposed crosses after re-reading the borders. Final cross refinement is local image measurement, not optimization against geographic residuals. Title boxes moving between corners, and the separate bottom tables on 904 and 916, receive individual mask cutouts. Original proposals remain available beside the corrected observations.

No `@allmaps/attach` tie points enter the absolute fits. Numerical flags and release eligibility remain unchanged by visual checks. The assumed two-pixel observation uncertainty is not calibrated, and controls/checks share border anchors, so residuals do not establish historical survey accuracy or independently exclude a uniform grid-origin error.

## Recorded processing statistics

The initial preparation interval was **25.94 minutes** (2026-11-19T19:00:43.278911+00:00 to 2026-11-19T19:26:39.858Z). It includes setup, preparation, AI visual review and waits through the first completed export. It is not CPU time or model latency. Replaying an exported batch preserves this initial interval.

At first export, **9.76 minutes** were recorded across 12 processing commands, including one failed command. This cumulative total includes only instrumented commands, not ad hoc preparation scripts or model/tool activity; the dashboard updates it for later recorded replays. Durations come from wall clocks and monotonic command timers, not estimates.

Earlier batch processing times are shown as not recorded.

## Reproduction and subsequent series

```sh
# Restore exact checksum-verified evidence only if missing.
.venv/bin/python scripts/georeferencing/georeference_batch.py hydrate --batch batch-03
# Recompute from saved observations and cached images without network requests.
.venv/bin/python scripts/georeferencing/georeference_batch.py measure --batch batch-03 --offline
node scripts/georeferencing/georeference-batch-export.ts batch-03
pnpm georeference:validate

# Select the next complete remaining series when starting the next batch.
.venv/bin/python scripts/georeferencing/georeference_batch.py select --batch batch-04 --series D.04
```

Omitting `--limit` selects the entire remaining series, in saved archival order, excluding pilot and previous batch scans. Both Python measurement and TypeScript export reject incomplete, reordered or wrong-series selections. Selection alone does not approve geometry or the user's visual review.

## Per-scan diagnostics

| Inventory | Original CRS | RMS (native px) | Held-out error (px) | Numerical screen |
| --- | --- | ---: | ---: | --- |
| 880 | EPSG:28991 | 1.68 | 4.58 | Pass |
| 879 | EPSG:28991 | 2.42 | 4.93 | rms-above-2px |
| 886 | EPSG:28991 | 2.90 | 2.83 | rms-above-2px |
| 499 | EPSG:28992 | 2.25 | 1.15 | rms-above-2px |
| 881 | EPSG:28992 | 1.94 | 1.38 | Pass |
| 882 | EPSG:28991 | 3.26 | 1.98 | rms-above-2px |
| 883 | EPSG:28991 | 2.26 | 0.96 | rms-above-2px |
| 884 | EPSG:28992 | 2.75 | 1.62 | rms-above-2px |
| 885 | EPSG:28992 | 3.00 | 1.68 | rms-above-2px |
| 500 | EPSG:28992 | 2.30 | 2.03 | rms-above-2px |
| 888 | EPSG:28991 | 2.05 | 1.85 | rms-above-2px |
| 890 | EPSG:28991 | 2.23 | 1.37 | rms-above-2px |
| 889 | EPSG:28992 | 1.82 | 0.94 | Pass |
| 887 | EPSG:28992 | 2.51 | 1.16 | rms-above-2px |
| 501 | EPSG:28992 | 1.38 | 0.85 | Pass |
| 891 | EPSG:28991 | 2.72 | 1.81 | rms-above-2px |
| 892 | EPSG:28992 | 3.08 | 0.87 | rms-above-2px |
| 502 | EPSG:28992 | 1.65 | 1.36 | Pass |
| 893 | EPSG:28991 | 2.68 | 0.52 | rms-above-2px |
| 894 | EPSG:28991 | 2.17 | 1.08 | rms-above-2px |
| 895 | EPSG:28992 | 1.72 | 0.96 | Pass |
| 503 | EPSG:28992 | 2.29 | 1.29 | rms-above-2px |
| 896 | EPSG:28991 | 0.50 | 3.20 | Pass |
| 897 | EPSG:28992 | 1.24 | 2.18 | Pass |
| 504 | EPSG:28992 | 1.43 | 2.47 | Pass |
| 898 | EPSG:28991 | 3.03 | 1.31 | rms-above-2px |
| 899 | EPSG:28992 | 2.41 | 1.25 | rms-above-2px |
| 505 | EPSG:28992 | 2.08 | 2.30 | rms-above-2px |
| 900 | EPSG:28991 | 2.88 | 1.61 | rms-above-2px |
| 901 | EPSG:28991 | 2.66 | 1.66 | rms-above-2px |
| 902 | EPSG:28992 | 2.08 | 1.18 | rms-above-2px |
| 506 | EPSG:28992 | 1.52 | 2.13 | Pass |
| 904 | EPSG:28991 | 2.58 | 0.94 | rms-above-2px |
| 905 | EPSG:28991 | 2.81 | 0.39 | rms-above-2px |
| 903 | EPSG:28992 | 2.46 | 1.88 | rms-above-2px |
| 507 | EPSG:28992 | 2.53 | 1.79 | rms-above-2px |
| 907 | EPSG:28991 | 1.89 | 4.22 | Pass |
| 908 | EPSG:28991 | 2.42 | 1.38 | rms-above-2px |
| 906 | EPSG:28992 | 2.30 | 0.47 | rms-above-2px |
| 508 | EPSG:28992 | 2.26 | 2.63 | rms-above-2px |
| 909 | EPSG:28991 | 2.17 | 1.96 | rms-above-2px |
| 910 | EPSG:28992 | 2.00 | 1.90 | Pass |
| 509 | EPSG:28992 | 1.20 | 1.03 | Pass |
| 912 | EPSG:28991 | 2.28 | 2.62 | rms-above-2px |
| 911 | EPSG:28992 | 1.64 | 2.43 | Pass |
| 510 | EPSG:28992 | 1.83 | 4.08 | Pass |
| 913 | EPSG:28991 | 1.31 | 2.91 | Pass |
| 914 | EPSG:28992 | 1.06 | 1.02 | Pass |
| 511 | EPSG:28992 | 2.39 | 0.50 | rms-above-2px |
| 916 | EPSG:28991 | 2.81 | 1.17 | rms-above-2px |
| 917 | EPSG:28991 | 2.91 | 2.79 | rms-above-2px |
| 915 | EPSG:28992 | 3.49 | 2.12 | rms-above-2px |
| 918 | EPSG:28991 | 1.80 | 1.52 | Pass |
| 919 | EPSG:28992 | 2.54 | 1.41 | rms-above-2px |
| 921 | EPSG:28991 | 3.47 | 1.06 | rms-above-2px |
| 920 | EPSG:28992 | 2.40 | 0.98 | rms-above-2px |
| 512 | EPSG:28992 | 1.55 | 1.86 | Pass |
| 922 | EPSG:28991 | 3.20 | 1.21 | rms-above-2px |
| 923 | EPSG:28992 | 2.78 | 1.37 | rms-above-2px |
| 513 | EPSG:28992 | 2.82 | 1.81 | rms-above-2px |
| 925 | EPSG:28991 | 2.35 | 1.48 | rms-above-2px |
| 926 | EPSG:28991 | 2.77 | 0.75 | rms-above-2px |
| 924 | EPSG:28992 | 2.26 | 1.03 | rms-above-2px |
| 514 | EPSG:28992 | 2.52 | 2.09 | rms-above-2px |
| 927 | EPSG:28991 | 1.64 | 1.91 | Pass |
| 928 | EPSG:28992 | 1.06 | 2.22 | Pass |
| 515 | EPSG:28992 | 0.36 | 1.20 | Pass |
| 932 | EPSG:28991 | 2.04 | 2.55 | rms-above-2px |
| 931 | EPSG:28992 | 2.61 | 2.03 | rms-above-2px |
| 930 | EPSG:28992 | 2.51 | 1.68 | rms-above-2px |
| 933 | EPSG:28992 | 3.30 | 1.43 | rms-above-2px |
| 929 | EPSG:28992 | 2.73 | 2.18 | rms-above-2px |
| 516 | EPSG:28992 | 2.58 | 2.78 | rms-above-2px |
| 937 | EPSG:28991 | 1.84 | 1.54 | Pass |
| 936 | EPSG:28992 | 1.67 | 1.62 | Pass |
| 935 | EPSG:28992 | 1.59 | 1.18 | Pass |
| 934 | EPSG:28992 | 2.11 | 1.28 | rms-above-2px |
| 517 | EPSG:28992 | 1.32 | 2.78 | Pass |
| 939 | EPSG:28991 | 2.08 | 1.64 | rms-above-2px |
| 938 | EPSG:28992 | 2.81 | 1.74 | rms-above-2px |
| 518 | EPSG:28992 | 3.04 | 2.38 | rms-above-2px |
