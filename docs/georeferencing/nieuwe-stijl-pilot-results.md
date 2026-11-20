# Nieuwe Stijl: 24-scan pilot results

Completed on 2026-11-19 on `codex/nieuwe-stijl-georeferencing-plan`: **24 measured scans, 7 provisional passes, 17 needing further review**. No commit was made.

All 16 map groups D.02–D.17 are represented. D.01 sheet indices/legends were excluded from georeferencing. The selection accounts for 999 digitized maps: 24 pilot scans and 975 not yet processed. Existing archival Collections and Manifests retain their metadata and Canvas identities.

## What was measured

Each scan has a reviewed native-pixel polygon mask, four fitted grid crosses and one held-out cross. The 120 crosses were read from cached native details, refined with a short symmetric cross-arm CV template and visually checked again. Masks follow the inner map frame and exclude the margins, title blocks and appendix tables. Conservative notches connect internal tables to blank lower margins so masks remain simple polygons without holes. Scans 947/948 retain separate pixel spaces and share the Appendix A sheet identity.

The pilot found signed **RD Old (EPSG:28991)** as well as RD New. RD Old is normalized by explicitly adding `[155000, 463000]` metres after checking the printed border values. Original signed values, units and verbatim label strings remain in the canonical records. Decimal kilometre labels and metre labels with thousands dots are distinguished. Enlarged evidence corrected 3/5 and 4/8 digit ambiguities on 821 and 1337; corrections are recorded.

OCR proposals are retained separately. They were not trusted to assign coordinates: faint, rotated and handwritten labels frequently fail the orthogonal OCR passes. Grid steps traced from border anchors are marked as derived, and shared-anchor dependencies are explicit.

## Quality results

The original thresholds remain **RMS ≤ 2 native pixels; held-out error ≤ 5 pixels**. No point was discarded to force a pass. The 17 flagged scans retain complete observations and draft annotations; they are excluded from release pages. These are processing thresholds, not claimed map or ground accuracy. Four controls give two residual degrees of freedom. The assumed 2-pixel observation sigma is not calibrated, so covariance, standardized residuals and chi-square probabilities are diagnostics only. No statistical-pass claim is made. Held-out grid checks share some absolute border anchors; independent label review remains essential.

| Inventory | Original CRS | RMS px | Check px | Status |
|---|---|---:|---:|---|
| 478 | EPSG:28992 | 2.855 | 0.714 | needs-review |
| 821 | EPSG:28991 | 0.559 | 5.091 | needs-review |
| 878 | EPSG:28991 | 1.999 | 0.225 | pilot-pass |
| 498 | EPSG:28992 | 2.355 | 2.135 | needs-review |
| 940 | EPSG:28991 | 2.812 | 0.701 | needs-review |
| 542 | EPSG:28992 | 2.442 | 1.857 | needs-review |
| 1050 | EPSG:28991 | 2.428 | 2.067 | needs-review |
| 726 | EPSG:28992 | 1.837 | 0.891 | pilot-pass |
| 1085 | EPSG:28992 | 1.524 | 1.829 | pilot-pass |
| 596 | EPSG:28992 | 3.497 | 2.907 | needs-review |
| 1139 | EPSG:28991 | 2.000 | 1.733 | pilot-pass |
| 1140 | EPSG:28992 | 2.385 | 2.653 | needs-review |
| 1212 | EPSG:28991 | 2.695 | 4.778 | needs-review |
| 1252 | EPSG:28992 | 2.263 | 1.314 | needs-review |
| 1273 | EPSG:28991 | 2.663 | 0.964 | needs-review |
| 1327 | EPSG:28991 | 3.384 | 3.604 | needs-review |
| 1337 | EPSG:28991 | 3.238 | 0.791 | needs-review |
| 1344 | EPSG:28991 | 1.696 | 0.735 | pilot-pass |
| 1359 | EPSG:28991 | 2.551 | 1.939 | needs-review |
| 1401 | EPSG:28992 | 1.822 | 3.480 | pilot-pass |
| 769 | EPSG:28992 | 2.142 | 2.914 | needs-review |
| 947 | EPSG:28992 | 3.122 | 5.358 | needs-review |
| 948 | EPSG:28992 | 1.349 | 2.137 | pilot-pass |
| 949 | EPSG:28992 | 2.239 | 2.859 | needs-review |

## Tie-point experiment

`@allmaps/attach@1.0.0-beta.51` jointly fitted the 947/948 pair using three SIFT matches, checked in native-resolution patches. Three separate matches were held out. Their overlap RMS changed from **2.988 m to 2.266 m**. The independent grid check worsened from **5.151 m to 5.300 m** on 947 and **2.058 m to 2.299 m** on 948. The largest displacement at an original control was **0.630 m**.

The package solves attachments; image matching is a separate CV step. The experiment uses affine image-to-RD fits with equal equation weights, explicit options, `averageOut: false`, and evaluation of the solved transforms. Ties were not exported as observed GCPs or used to replace original RD coordinates. Better relative agreement does not establish better absolute accuracy. Keep the grid-only baseline; test other overlap pairs and a calibrated weighting model before adopting attachment.

## Conversion and viewer checks

PROJ uses the pinned non-ballpark EPSG:4833 Amersfoort-to-WGS84 Helmert operation, with network grids disabled and longitude/latitude order explicit. Its stated accuracy is 1 metre. The supplied EPSG:28992 PROJJSON and checksum, local EPSG/PROJ versions, exact pipeline and RD Old definition are retained. Two external RDNAP reference coordinate pairs agree within 0.027 m at this operation’s accuracy; this is not a current-epoch or centimetre-accuracy claim.

Allmaps parses every candidate annotation without changing its mask or observed GCPs. Held-out checks are excluded from exported controls. Dense numerical comparisons of Allmaps polynomial-order-1 renderer geometry against the RD affine followed by PROJ show at most **0.711 m** difference for released pilot maps (**1.523 m** across all candidates). Both Web Mercator and longitude/latitude fits are reported. This tests the transformation numerically; no browser renderer screenshot was used.

## Archive requests

The cache contains **24 overviews and 113 bounded details**, **20.93 MB** in total, including images reused from planning. No full-resolution scans were fetched. At most **11 details per scan** were needed, below the budget of 12. Fetches are serial, rate-limited to one new request per second, checksum-verified, resumable and respect Retry-After. The completed pilot replays with zero network requests.

## Outputs and reproduction

- [Canonical maps and preserved observations](../../data/georeferencing/nieuwe-stijl/maps)
- [Machine-readable pilot report](../../data/georeferencing/nieuwe-stijl/pilot-report.json) and [coverage ledger](../../data/georeferencing/nieuwe-stijl/coverage.json)
- [Draft annotations for all 24 scans](../../data/georeferencing/nieuwe-stijl/draft-annotations) and [release pages for the 7 passing scans](../../data/iiif-annotations/nieuwe-stijl)
- [Attachment diagnostics](../../data/georeferencing/nieuwe-stijl/attach-report.json) and [viewer diagnostics](../../data/georeferencing/nieuwe-stijl/viewer-report.json)
- [Setup and commands](nieuwe-stijl-georeferencing.md)

The local gallery is `.cache/georeferencing/review/index.html`. Photographs stay ignored; their exact URLs, regions, decoded sizes, checksums and retrieval metadata are saved. `pnpm georeference:pilot` reproduces canonical records, experimental diagnostics, annotations and this report offline after evidence hydration. `pnpm georeference:validate` runs Python geometry/acquisition tests and the existing TypeScript/catalog/build suite. Normal `pnpm build` reads saved outputs and needs neither Python nor network access.

## Before expanding beyond the pilot

Resolve the flagged residuals with additional spread-out crosses and independent repeat localization. Calibrate observation uncertainty and freeze acceptance limits before the planned 50-scan batch. Do not relax thresholds merely to increase the pass count. Review any geometry change again; saved approved geometry prevents a changed detector or edited coordinate from silently retaining visual approval. The remaining 975 maps have not been georeferenced.

## Sources

- [Supplied RD New definition](https://epsg.io/28992.json)
- [Allmaps attach package](https://docs.allmaps.org/packages/attach)
- [PROJ RDNAP reference-coordinate discussion](https://github.com/OSGeo/PROJ/issues/1663)
- [TU Delft Testing Theory](https://books.open.tudelft.nl/home/catalog/book/178)
- [Stuttgart Adjustment Theory](https://www.gis.uni-stuttgart.de/lehre/campus-docs/LN_Ausgl.pdf)
- [IIIF Georeference Extension](https://iiif.io/api/extension/georef/)
