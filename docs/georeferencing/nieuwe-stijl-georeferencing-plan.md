# Nieuwe Stijl georeferencing implementation plan

Create a polygon mask and Georeference Annotation for each digitized map in the Nieuwe Stijl edition. Derive control points from the printed RD grid crosses, their arrowheads and border coordinates. Preserve the transcribed projected coordinates alongside the converted longitude and latitude. Use computer vision to prepare candidates, then visually check the evidence before exporting a map.

Work in `river-maps` on branch `codex/nieuwe-stijl-georeferencing-plan`, based on `3c14a2c`. The [implementation and 24-scan pilot](nieuwe-stijl-pilot-results.md) now cover stages 1–4 and pilot export integration. Seven scans pass the provisional screen; seventeen need further review. Bulk processing remains pending. The reference editor was inspected at commit `7c8d650`.

## Scope and map selection

The current source is [the saved Nationaal Archief snapshot](../../data/nationaal-archief/nieuwe-stijl.json), linked to [the Nieuwe Stijl Collection](../../iiif/collections/nieuwe-stijl.json).

| Inventory groups | Scans | Action |
| --- | ---: | --- |
| D.01 | 10 | Exclude sheet indices and legends from annotation processing |
| D.02 through D.16 | 996 | Process the river maps, retaining each dated version and copy |
| D.17 | 3 | Process the map appendices, with special handling for the split sheet |
| Total selected | 999 | Account for every scan with a result or a documented unresolved status |

Inventory numbers 947 and 948 are overlapping captures of the same Appendix A sheet; 949 is a separate Appendix B map. Give each capture its own mask and image coordinates, and record the shared-sheet relationship for 947/948. Do not merge their pixel spaces or count their overlap as independent geographic evidence. Additional map insets, if discovered, need separate masks and annotations. Thus the final annotation count can differ from the scan count.

Keep the existing Collection and Manifests intact. The exclusion applies to georeferencing, not to the archival catalog. Keep first-edition annotations outside this task. Reconcile the selection against the source snapshot hash so a future inventory update cannot silently change the processing scope.

Six overview samples support the initial design: inventory numbers 478, 542, 726, 947, 948 and 949. They show photography apparatus outside the map, inner and outer frame lines, rotated grid crosses, corner title blocks, and split-sheet captures. A native-resolution section of 542 shows arrowheaded crosses and consecutive border labels `373000`, `373500` and `374000`. These are observations about the grid notation, not completed control-point pairs. The appendix maps also contain Dutch and Belgian coordinate tables; identify the applicable grid before reading values from either column.

## Implementation stages

| Stage | Work | Completion condition |
| --- | --- | --- |
| 1 | Define the selection, canonical records, schemas and request cache | All 999 selected scans have stable identities; D.01 cannot enter the job queue |
| 2 | Build overview acquisition, mask detection and grid/OCR proposals | Repeatable candidates and evidence crops can be generated offline from cache |
| 3 | Complete a 24-scan pilot with visual verification | Cover every selected series plus difficult examples; establish measurement uncertainty and acceptance limits |
| 4 | Implement RD adjustment, coordinate conversion and annotation export | Synthetic failures are caught and pilot annotations round-trip through the target tools |
| 5 | Process one 50-scan batch, then the remaining scans in resumable batches | Every released annotation has reviewed source evidence and a recorded quality class |
| 6 | Integrate generated Annotation Pages and coverage reporting | Deterministic offline build; published links resolve; all selected scans are accounted for |

The pilot must include both 1:5,000 and 1:2,000 maps, different rotations and dates, faint or obstructed crosses, title-block notches, and all three appendix captures. Use 478, 542 and 726 as initial ordinary-map examples. Pilot work establishes reusable settings within similar layouts; every subsequent sheet still receives its own geometry and visual check.

## Request images conservatively

Reuse the Image API metadata already saved in the source snapshot. Do not refetch 999 `info.json` documents or use the large full-resolution download links as the default image source.

1. Fetch one overview per selected scan, using an advertised size near 1,600–2,000 pixels on the longest side. Choose cached native pyramid levels when practical.
2. Run classification, coarse mask detection, grid orientation and candidate ranking on that overview.
3. Fetch small native-resolution regions only where needed: selected crosses, border labels and short boundary strips. Combine nearby regions when this reduces work. Prefer existing cached tiles if they already cover the region.
4. Cache responses by the exact service identifier and request parameters. Retain decoded dimensions, original-image region, request URL, checksum, response validators and retrieval time. Both CV and visual review must use the same cached evidence.
5. Start with one request in flight and no more than one new request per second to the archive host. Honour `Retry-After`, including HTTP dates, and use exponential backoff with jitter for 429/503 responses. Persist the queue and stop fetching after repeated failures rather than retrying the whole collection.

Set an initial automatic budget of one overview plus twelve detail requests per scan, with each detail response at most 1.8 megapixels and within the service's advertised limits. An exhausted budget moves that scan to a review queue; it does not justify guessing coordinates or downloading the full scan automatically. Record request counts, bytes and cache hits to tune the budget after the pilot. Offline validation makes no image requests. Follow the [IIIF Image API](https://iiif.io/api/image/3.0/) for region and size requests.

Convert every detected position back into original-image coordinates using the requested region and the actual decoded image dimensions. Retain the complete inverse transform for any local crop rotation or deskew. Pixel coordinates use top-left origin, x rightwards and y downwards; never store overview pixels as original-image pixels. Preserve the archive's image-service URL, including its query-string identifier.

## Detect and review masks

Use the editor's distinction between a printed frame and a physical sheet edge as the starting point. Its [detection engine](../../../map-series-editor/src/lib/detection/engine.ts) combines grayscale analysis, Canny edges, line detection, ridge support and local line refinement. Its [mask validation](../../../map-series-editor/src/lib/mask.ts) supports simple concave polygons.

The batch implementation should:

- Detect the inner mapped extent while excluding microfilm holders, rulers, blank photographic margins, border coordinate labels and adjacent-sheet labels.
- Propose a quadrilateral from long frame lines, then refine it from short native-resolution strips. Distinguish scanner skew from the rotation of the RD grid inside the frame.
- Adapt direction searches when a frame itself is rotated; the reference detector initially prefers approximately horizontal and vertical frame lines.
- Allow a concave notch for a title block attached to an edge. Preserve disconnected map insets as separate map records. An internal table is not a second map; retain it inside the enclosing mask when removing it would require an unsupported hole.
- Handle 947/948 as cropped map captures: a boundary may coincide with the edge of the available scan rather than a printed neatline. Record that distinction.
- Validate finite original-image coordinates, bounds, nonzero area, unique vertices and no self-intersections. Use a consistent clockwise vertex order in image coordinates without a duplicated closing vertex.

Produce an overview with the proposed mask and numbered vertices, plus native boundary crops for uncertain edges. Visually inspect the entire mask and any notches. Corrections become explicit saved vertices, not hidden detector parameters. Grid controls and mask vertices are independent; do not force controls onto frame corners.

Use the editor as a reference for behavior and file compatibility. Keep the batch implementation in this repository. If source code is reused directly, carry its GPL licence and attribution requirements with that reuse.

## Recover the projected grid

Treat the crosses as a rotated lattice, not a north-aligned rectangle. The map frame, north arrow and RD grid need not have the same orientation.

1. **Find candidate marks.** Use contrast normalization, adaptive thresholding and connected components, followed by rotated templates or line-junction detection. Include both cross and arrowheaded-cross templates. Reject text strokes, parcel marks, river-kilometre ticks and the large north arrow using shape and lattice consistency.
2. **Estimate the two grid directions.** Combine cross-arm orientations, arrowhead direction and repeated cross spacing. Cluster candidate centres into two lattice directions with robust fitting. Do not use a single arrow or the river axis to assign east and north.
3. **Read the border coordinates.** Fetch narrow crops around the relevant labels, rotate them locally for OCR, and retain the unmodified pixels as evidence. Preserve raw text before normalization, including abbreviations, separators, units, missing digits and alternatives.
4. **Anchor the lattice absolutely.** Follow the appropriate grid direction from each cross to its border intercept and corresponding label. Read labels from both coordinate families and, where possible, opposing borders. Verify interval and positive direction from successive labels. Do not assign the nearest text box to a cross or assume that the top border always labels one particular axis.
5. **Choose controls.** Select at least three distinct non-collinear crosses spread over the mapped area. Prefer four to six when legible, with good coverage along both dimensions. Use the intersection of the cross arms, not the arrow tip, as the pixel location. Refine the intersection from the native crop and retain a localization uncertainty.
6. **Verify by vision.** For every accepted control, inspect the cross centre, arrow direction, both coordinate assignments and the source border labels. Read the numbers from the crop independently before comparing with the OCR proposal. Confirm scale and axis interpretation using the full overview. Mark doubtful digits unresolved and request a better crop only when it can resolve them.

Grid spacing is evidence, not a global constant: establish it for each layout or sheet from visible labels. An obscured coordinate may be derived by counting verified lattice intervals from a legible anchor, but record that derivation and its dependencies. Several points using the same anchor do not supply independent protection against a wrong anchor.

Repeated editions may help locate candidate regions, but transfer neither masks nor control points without checking the current scan. A global coordinate offset, axis swap or wrong grid origin can fit an affine transform perfectly. Detect these through independently read absolute labels, arrow directions, geographic plausibility and comparison of map place names. Modern shorelines are not control points for historical river maps.

## Preserve RD values and convert reproducibly

Use **EPSG:28992**, RD New, with x/easting and y/northing in metres, as requested. Save the supplied [PROJJSON definition](https://epsg.io/28992.json) with a checksum. Keep original transcriptions and their units even when the normalized numeric pair is in metres. Do not silently interpret river chainage or Belgian coordinate-table columns as RD coordinates. Unexpected values require source inspection; do not silently add an origin offset or change CRS.

Use PROJ as the canonical batch converter, targeting longitude/latitude order explicitly, for example `OGC:CRS84`. Record the selected coordinate operation, PROJ/database versions, accuracy statement and any grid-file checksums. Disable implicit network grid downloads during builds and reject ballpark fallback. The supplied CRS definition describes RD; selecting its transformation to WGS84 is a separate step. [PROJ's operation selection documentation](https://proj.org/en/stable/apps/projinfo.html) describes these choices.

The current local PROJ installation offers non-ballpark RD-to-WGS84 operations with a stated accuracy of 1 metre. During the pilot, choose and pin the appropriate operation for the map coverage; use a verified grid-based alternative if the required accuracy warrants it. Test against authoritative reference coordinates, not only a round trip. A round trip can reproduce the same incorrect datum assumption. Proj4js can support editor review once its definition and any grids match the chosen operation; check its output against the canonical converter.

Store original projected coordinates as immutable observations. Store adjusted positions, derived coordinates, conversion outputs and residuals separately. Never reconstruct the original RD values by inverse-transforming exported longitude/latitude or from the editor's rounded display.

## Adjustment and quality checks

Fit the geometry in the RD plane before geographic conversion. Begin with a six-parameter affine model to accommodate scan rotation, separate axis scales and shear. Keep the observations in the space where their uncertainty is measured. For verified grid coordinates `(E, N)` and measured scan coordinates `(u, v)`, fit:

```text
u = a0 + a1 E + a2 N
v = b0 + b1 E + b2 N
```

Centre and scale the coordinates for numerical stability and solve with QR or SVD. Verify full rank and acceptable conditioning, then invert the fitted 2×2 linear part for image-to-RD mapping. Treat pixel localization as uncertain and verified printed grid coordinates as fixed for this model. If both coordinate sets have material uncertainty, use a mixed/errors-in-variables model rather than ordinary least squares. This choice follows the distinction illustrated in the Stuttgart [Adjustment Theory notes](https://www.gis.uni-stuttgart.de/lehre/campus-docs/LN_Ausgl.pdf), sections 5.3.4–5.3.5.

Three non-collinear pairs determine the affine parameters, with `2n − 6 = 0` residual degrees of freedom. Their zero fitted residual is not an accuracy check. Prefer four to six measured points and an independently transcribed check point where feasible. A result with only three controls can be visually verified, but must be labelled `minimal-control` and must not receive a statistical-pass claim.

For redundant observations, weight the fit using localization uncertainty estimated from repeat picks on the pilot. With a calibrated observation covariance, use the weighted residual statistic and its appropriate degrees of freedom for a global consistency test. Report standardized residuals, leverage, conditioning and uncertainty propagated across the mask; account for shared anchors and correlated evidence. Use leave-one-out or held-out predictions where the remaining geometry is sufficient. The [Testing Theory reference](https://books.open.tudelft.nl/home/catalog/book/178), especially chapter 4, motivates redundancy and error identification; a passed test cannot detect every systematic mistake.

Use robust estimation to propose suspicious candidates, then inspect their source crops. Retain rejected observations and reasons. Never change a transcribed coordinate merely to reduce residuals. A similarity model is a useful diagnostic for rotation and scale; it must not be imposed solely to create redundancy. Escalate systematic affine residuals to additional controls and a justified distortion model. Do not use thin-plate-spline interpolation's zero training residual as evidence of correctness.

Pilot starting targets are an RMS pixel residual at most 2 original-image pixels and independent check errors at most 5 pixels. These are proposed processing targets, not claimed ground accuracy. Calibrate and freeze limits before bulk processing, report errors in both pixels and RD metres, and distinguish fitting error, datum-conversion accuracy and the historical map's own accuracy. Check near-collinear or clustered controls and excessive extrapolation separately from residual size.

## Canonical records and export

Keep the authoritative observations in `data/georeferencing/nieuwe-stijl/maps/<map-id>.json`. A stable map ID combines the source record/image identity and a persistent component ID; it must not depend on processing order or mask vertices.

Each record should contain:

| Field group | Preserved information |
| --- | --- |
| Source | Inventory number, EAD/source hash, series, Canvas and Manifest IDs, image service, native dimensions, shared-sheet relationship |
| Mask | Original-image vertices, edge kinds, candidate/corrected history and visual review |
| Controls | Stable point ID, measured pixel pair, exact normalized RD pair, CRS and units, verbatim labels, direct/derived status, anchor dependencies |
| Evidence | Request URL and region, decoded size, inverse crop transform, checksum, OCR alternatives, centre uncertainty and visual decision |
| Conversion | Derived longitude/latitude, pinned operation and versions |
| Adjustment | Model, parameters, used/rejected/check points, covariance assumptions, residuals, degrees of freedom and quality class |
| Review | Reviewer or model identifier, time, corrections, decisions and unresolved reasons |

Generate standalone Annotation Pages per included series under `data/iiif-annotations/nieuwe-stijl/series-XX.json`, published under `iiif/annotations/nieuwe-stijl/`. Follow the existing editor-compatible pattern: one `georeferencing` Annotation per map, a `SpecificResource` targeting its `ImageService3`, native dimensions, parent Canvas/Manifest references and a polygon `SvgSelector`. Use the actual map mask and observed controls; never substitute synthetic display coordinates. The [IIIF Georeference Extension](https://iiif.io/api/extension/georef/) specifies the target, selector and control-point structure.

Set `resourceCoords` to original-image pixels and GeoJSON Point `coordinates` to WGS84 `[longitude, latitude]`. Preserve each RD pair in documented namespaced feature properties with a small published JSON-LD context, and keep the canonical record as the authoritative copy. Publish that record as linked provenance so loss of custom fields in another editor cannot destroy the transcriptions.

Generate the selector using the annotation format, not the editor's generic SVG-download helper: the Georeference Extension disallows SVG `viewBox` and element transforms. Validate the resulting Annotation Page with the installed Allmaps parser and a structural/schema check. Do not attach an ImageService-targeted page directly as a Canvas annotation; Canvas-attached variants must target that Canvas in its coordinate space. Standalone page links are sufficient for the initial release.

Start by testing `polynomial` order 1 for the exported transform. The authoritative affine solution is in RD, while viewers may fit converted controls in a different geographic or projected space. Compare the rendered warp over a dense set of image positions against the RD solution followed by PROJ, and add verified controls if needed. If derived controls are later needed for display, identify them explicitly and exclude them from statistical validation.

The reference editor currently exports thin-plate-spline transforms and does not guarantee preservation of arbitrary annotation extensions. Treat editor output as an edit proposal: reconcile masks and control positions by stable identity, reattach unchanged source observations from the canonical record, and revalidate. A changed geographic coordinate invalidates its previous source association and requires new source evidence; do not attach the old RD pair to a new location. Do not let a round trip silently replace the chosen model, discard RD coordinates or turn an independent check point into a fitted control.

## Repository work and acceptance

Proposed modules are a Python CV/measurement pipeline using OpenCV, NumPy and PROJ, plus a TypeScript exporter using the existing IIIF toolchain and the Allmaps annotation parser. Pin dependencies when implementing. Reuse the installed Tesseract for OCR after checking supported orientation handling. Keep photographic evidence in an ignored `.cache/georeferencing/` directory; commit compact crop manifests and checksums so evidence can be retrieved again. Keep any small diagnostic fixtures explicitly selected for tests separate from the bulk cache.

Add the following pieces in implementation order:

1. `data/georeferencing/nieuwe-stijl/selection.json`, schemas and a resumable status ledger.
2. `scripts/georeferencing/georeference/` acquisition, masks, grid/OCR, adjustment, projection and review-report modules; a pinned Python dependency file.
3. Canonical per-map records, pilot results and versioned detector/quality configuration.
4. An annotation exporter and checks for Allmaps import, mask preservation, projected-coordinate preservation and viewer geometry.
5. Build integration in [scripts/build.ts](../../scripts/build.ts) that copies regenerated annotation/provenance outputs; new links from the relevant Manifests and browse page. Builds must remain offline, and existing Canvas/image identifiers must remain stable.

Tests must cover original-pixel recovery after crop/resize/rotation, wrong axis order, thousandfold unit errors, a one-digit OCR error, uniform grid offsets, collinearity, poor point distribution, missing datum assets, mask notches, split captures, and repeatable interrupted downloads. Test rate limiting, response caching and `Retry-After` without contacting the archive. Add synthetic rotated/sheared grids with known coordinates and realistic noise to verify fitting and error detection; include a three-point case that cannot claim residual validation. Verify custom base URLs and preserve the existing first-edition data.

For each released map require a visually checked mask, at least three verified non-collinear controls, preserved RD observations and evidence, a reproducible conversion, an explicit quality class, and a successful annotation/renderer check. Review contact sheets must remain legible; inspect individual crops for every chosen coordinate rather than accepting an unreadable montage. Ambiguous records remain `needs-review` with reasons and are excluded from release pages until resolved. A coverage report must reconcile released, excluded and unresolved records with all 999 selected scans. An unresolved record is not evidence that the map is undigitized.

The final deliverables are the canonical observations, per-series Annotation Pages, compact provenance, a quality/coverage report and commands that regenerate them from saved inputs. Completion requires resolving every selected map or explicitly reporting the remaining exceptions; it does not require inventing coordinates to reach a target count.

## Reference implementation links

- [Editor mask and annotation workflow](../../../map-series-editor/docs/georeferencing-and-files.md)
- [Frame detection and refinement](../../../map-series-editor/src/lib/detection/engine.ts)
- [Image region requests and pixel-coordinate recovery](../../../map-series-editor/src/lib/iiif.ts)
- [Mask validity](../../../map-series-editor/src/lib/mask.ts)
- [Annotation export](../../../map-series-editor/src/lib/resource-export.ts)
- [Projection conversion and display rounding](../../../map-series-editor/src/lib/projections.ts)
- [Existing first-edition Annotation Page](../../data/iiif-annotations/first-edition/series-1.json)
