# Nieuwe Stijl georeferencing pilot

The [pilot results](nieuwe-stijl-pilot-results.md) cover 24 digitized scans from all 16 map groups. This implements the pilot stages of the [plan](nieuwe-stijl-georeferencing-plan.md); the 50-scan batch and the other 975 selected scans are not part of this run. Work is on `codex/nieuwe-stijl-georeferencing-plan`. Do not commit without the user's explicit instruction.

## Reproduce the saved pilot

Use Node 24+, pnpm 10.17.1, and Python 3.12. The Python environment is isolated and ignored. Normal catalog builds read the saved JSON outputs and do not need Python or network access.

```sh
pnpm install --frozen-lockfile
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-georeference.txt
pnpm georeference:hydrate
pnpm georeference:pilot
pnpm georeference:validate
```

Hydration defaults to **offline**. In a fresh checkout with no photographic cache, explicitly allow the serial, rate-limited fetcher to obtain the saved evidence:

```sh
.venv/bin/python scripts/georeferencing/georeference.py hydrate --fetch
```

It retrieves the exact recorded URLs and rejects a response with a changed checksum. It never downloads full native scans. The cache is keyed by URL and stores checksum-verified bytes and response metadata; one process at a time may acquire images. Each missing image is written atomically. A failed acquisition can be resumed with the same command. No IIIF `info.json` is refetched: the source snapshot supplies image dimensions and service limits.

The successful pilot consumes 137 cached images, including 7 reused from the planning work. It uses 24 overviews, 113 details and about 20.93 MB. The per-scan maximum is 11 details, below the budget of 12. Details have at most 1.8 megapixels. The cache includes one earlier exploratory section that is not a fitted observation.

## Files and commands

| File or command | Purpose |
|---|---|
| `data/georeferencing/nieuwe-stijl/selection.json` | Stable identities for 999 digitized map scans; explicit exclusion of 10 indices/legends |
| `reviews.json` | Saved visual readings, original signed/projected values, printed labels, units, mask corrections and correction history |
| `geometry-review.json` | Exact masks and control/check geometry reviewed by vision; changed geometry requires another review |
| `evidence-inputs.json`, `acquisition-catalog.json` | Portable cache/work recipes with exact URLs, native regions, decoded sizes, hashes and provenance |
| `maps/*.json` | Canonical source metadata, masks, observations, conversions and adjustment diagnostics |
| `crs/`, `projection.json`, `projection-checks.json` | Supplied CRS, checksum, pinned operation and external coordinate checks |
| `coverage.json`, `pilot-report.json` | Accounting for all 999 selected scans and the 24 pilot outcomes |
| `draft-annotations/` | Candidate Annotation Pages for all 24 scans, including quality failures; not published by the build |
| `data/iiif-annotations/nieuwe-stijl/` | Release pages containing only maps passing the provisional screen |
| `.cache/georeferencing/review/index.html` | Offline gallery of every mask, five grid crosses per map and paired overlap ties |
| `pnpm build` | Offline IIIF output, canonical provenance and standalone `seeAlso` links from relevant Manifests |
| `pnpm georeference:pilot` | Offline replay of measurement, attachment experiment, export and reporting |
| `pnpm georeference:validate` | Python tests, TypeScript checks, catalog tests, Allmaps round-trips and offline build |

The `scripts/georeferencing/georeference.py` CLI also provides `select`, `overviews`, `prepare`, `ties` and `ocr`. `overviews` and `prepare` work only on the selected pilot unless changed deliberately. `--inventory` limits those commands; `--offline` prohibits missing-image requests. Running `ties` creates **unreviewed** candidates; the attachment solver refuses them until visual review is recorded. Tesseract 5 is needed only for optional OCR proposals, not replay or normal builds.

CV is an aid to measurement. Overview Canny/Hough lines propose the inner frame; native corner evidence supports saved corrections. The rotated grid is traced from border labels independently. A bounded, symmetric short cross-arm template refines reviewed seed positions and avoids the arrow tips. Failed refinement retains the reviewed seed and records why. The implementation does not infer trusted absolute coordinates from OCR. All pilot masks and all 120 cross centres received an AI visual check; this is not an independent human survey.

## Observations, adjustment and export

Original projected coordinates remain immutable in `originalProjected`. The pilot encountered both RD New and signed RD Old. Only reviewed RD Old sheets receive the explicit false-origin offset `[155000, 463000]` metres. Kilometre labels and metre labels with thousands separators have separate provenance. Border strings are verbatim; coordinate pairs derived by following grid intervals are labelled as derivations with shared anchor dependencies. The appendix's Belgian coordinate tables are not RD controls.

The authoritative adjustment fits six affine parameters from RD to original scan pixels. It centres/scales the RD coordinates, uses SVD, checks rank and conditioning, and propagates an assumed pixel covariance. Four fitted points give two residual degrees of freedom; the fifth point remains held out. The provisional 2-pixel RMS / 5-pixel check limits are unchanged. A `pilot-pass` is a processing screen, not a calibrated statistical or ground-accuracy assertion. The 17 flagged scans need additional checks before release. Absolute coordinate offsets can evade residual tests; the tests explicitly demonstrate this limitation.

The geographic conversion pins inverse RD New plus EPSG:4833, with longitude/latitude order, no ballpark fallback and no network grid dependencies. Its stated 1 m accuracy is distinct from scan-fit and historical map accuracy. External RDNAP/ETRS89 reference pairs are compared within that accuracy, not treated as a current-epoch WGS84 centimetre reference.

Each exported map is a standalone Georeference Annotation targeting its `ImageService3`, with native dimensions, Canvas/Manifest parents, a simple polygon `SvgSelector` and polynomial order 1. Selectors have no `viewBox` or transforms. Only the four observed controls are exported. Check points remain in the canonical record.

The published context `contexts/river-maps-georeferencing.json` defines the `rm:` feature extensions. `rm:originalProjected`, `rm:rdNew`, `rm:coordinateDerivation`, and annotation-level `rm:quality` use JSON literals; `rm:pointId` and `rm:evidenceId` identify their source observations. Every annotation links to published canonical provenance. Allmaps/editor parsers may discard these extensions: the canonical record is authoritative, and parser round-trip tests assert geometry separately. Do not replace original RD observations with inverse-projected editor coordinates.

`IIIF_BASE_URL` rebases generated annotation, provenance and parent links. Archive image-service URLs retain their query-string identifiers. ImageService-targeted pages are linked as standalone datasets with `seeAlso`; they are not attached to Canvases as though they targeted Canvas pixels.

## Overlap experiment

`@allmaps/attach` solves a joint transformation from supplied corresponding image positions; it does not detect the matches. The separate Python step uses SIFT, descriptor-ratio filtering, affine RANSAC, spatial coverage selection and native detail matching. Six matches between 947/948 were visually checked. Three train the attachment and three evaluate it.

The TypeScript experiment solves in RD metres with explicit equal weights and `averageOut: false`. It evaluates the solved transformations directly, reports held-out overlap error, displacement at original controls, and held-out grid checks. Ties are correlated observations of the same sheet, not new independent geographic controls. The slight improvement in overlap comes with worse absolute grid checks, so attached results are **not** used in baseline annotations. A weighted joint model and other dates/sheets require a separate experiment.

## Deliberate pilot limits

- Frame proposals use this collection's near-horizontal film layout; saved visual vertices handle errors and cropped captures. This is not an automatic detector for arbitrary map layouts.
- OCR tries orthogonal orientations and records failures. The pilot still relies on visual label reading, especially oblique and handwritten text.
- Masks remove appendix tables with conservative concave notches through blank margins. The plan allowed retaining internal tables when holes were unsupported; these sheets permit exclusion without cutting mapped detail.
- Localization uncertainty is assumed, not calibrated from repeated independent picks. Covariance/chi-square outputs are diagnostic only.
- Allmaps geometry is numerically checked on a dense sample grid in both Web Mercator and longitude/latitude fits. No browser rendering screenshot or editor save round-trip was used.
- No bulk processing or publication/deployment was performed. All changes remain uncommitted.
