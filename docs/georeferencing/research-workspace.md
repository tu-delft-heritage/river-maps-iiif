# Georeferencing research workspace

Read [**4,995 small anchors**](nieuwe-stijl-georeferencing-essay.md), an illustrated account of how code and visual inspection positioned these maps, including unusual cases and a mosaic of every measured cross.

Open the [local progress dashboard](../../dashboard/index.html) for series totals, searchable maps, numerical flags, combined annotation downloads and direct Allmaps Viewer links. Viewer links embed the same annotations in `#data=`, so they work from disk without publishing the files. The dashboard itself makes no image-server requests. Rebuild with `pnpm georeference:dashboard`; batch exports refresh it too. The publication build is independent of the dashboard.

**All 999 digitized maps are visually accepted.** Every map series D.02–D.17 is fully reviewed, including the eight corrected placements. No maps await review; the ten sheet indices remain excluded.

The [20 November follow-up](nieuwe-stijl-review-2026-11-20.md) corrects six reported placements and two additional D.08 copies found by screening all 999 transforms. Open the [dashboard review group](../../dashboard/index.html#review-2026-11-20) for a combined **eight-map AnnotationPage** and direct Allmaps Viewer link. The dashboard now checks reflection, skew and unequal directional scaling on every rebuild. These corrections and their corresponding series are now approved.

D.16 is visually approved: [127 new maps and diagnostics](nieuwe-stijl-batch-16-results.md), with all 129 series maps available together from the dashboard.

D.15 is visually approved: [all 68 maps and diagnostics](nieuwe-stijl-batch-15-results.md), available together from the dashboard.

D.14 is visually approved: [all 22 maps and diagnostics](nieuwe-stijl-batch-14-results.md), available together from the dashboard.

D.13 is visually approved: [all 11 maps and diagnostics](nieuwe-stijl-batch-13-results.md), available together from the dashboard.

D.12 is visually approved: [all 15 maps and diagnostics](nieuwe-stijl-batch-12-results.md), available together from the dashboard.

D.11 is visually approved: [all 79 maps and diagnostics](nieuwe-stijl-batch-11-results.md), available together from the dashboard.

D.10 is visually approved: [all 43 maps and diagnostics](nieuwe-stijl-batch-10-results.md), available together from the dashboard.

D.09 is visually approved: [all 43 maps and diagnostics](nieuwe-stijl-batch-09-results.md), available together from the dashboard.

D.08 is visually approved: [all 107 maps and diagnostics](nieuwe-stijl-batch-08-results.md), available together from the dashboard.

D.07 is visually approved: [all 54 maps and diagnostics](nieuwe-stijl-batch-07-results.md), available together from the dashboard.

D.06 is visually approved: [all 37 maps and diagnostics](nieuwe-stijl-batch-06-results.md), available together from the dashboard.

D.05 is visually approved: [71 new maps and diagnostics](nieuwe-stijl-batch-05-results.md), with all 73 series maps available together from the dashboard.

D.04 is visually approved: [143 new maps and diagnostics](nieuwe-stijl-batch-04-results.md), with all 145 series maps available together from the dashboard.

The [50-scan batch report](nieuwe-stijl-batch-01-results.md) links its [combined review annotation](../../data/georeferencing/nieuwe-stijl/batches/batch-01/review-annotations.json). Run `pnpm georeference:batch` to reproduce batch 01 offline; see the batch 02 report for its commands. Process one complete remaining series per batch using `select --batch batch-NN --series D.NN`. Omit `--limit`; the optional legacy limit remains available for reproducing older selections. The dashboard reports measured elapsed and command time from Batch 03 onward. Earlier processing times are not reconstructed.

The [24-scan pilot report](nieuwe-stijl-pilot-results.md) records **7 provisional passes and 17 scans needing further review**. Each scan has a native-pixel mask, four fitted grid crosses, one held-out cross, and preserved projected observations. Both RD Old and RD New occur in the sources. Sheet indices are excluded from georeferencing.

[Setup and reproduction](nieuwe-stijl-georeferencing.md) covers the pinned Python/CV/PROJ environment, offline replay and tests. Canonical data lives under `data/georeferencing/nieuwe-stijl/`. The publication snapshot contains all 999 human-approved maps; the seven pilot passes are retained only as a historical numerical screen. The `@allmaps/attach` overlap experiment remains separate from the grid-only baseline.


## Rebuilding and releasing

- `pnpm georeference:dashboard` rebuilds the ignored `dashboard/` and its combined review pages from the canonical records.
- `pnpm georeference:release` checks current human approval fingerprints, writes the 16 publication snapshots, then rebuilds `iiif/`.
- `pnpm georeference:validate` runs the research and publication checks. The georeferencing Python environment is required for research tests only.
- The pilot command writes its historical seven-pass screen to `data/georeferencing/nieuwe-stijl/pilot-screen-annotations/`; it cannot overwrite the full approved publication snapshot.

Publication inputs and committed `iiif/` outputs intentionally coexist: the first reproduce the build without the research pipeline, the second are deployed by Pages. Image caches, generated dashboard pages, draft annotations and batch review aggregates stay local and ignored. Canonical observations, human approvals, correction history, acquisition recipes, numerical regression samples, and curated essay figures remain versioned on this branch.

The public branch is `watertijdreis`. Research files remain here; the small publishing helpers in `scripts/` are shared with the public branch so that a normal build preserves the released annotations, dates and geographic masks.
