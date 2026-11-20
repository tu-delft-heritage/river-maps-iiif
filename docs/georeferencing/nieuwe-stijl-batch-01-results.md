# Nieuwe Stijl batch 01 — 50 maps for review

The next 50 digitized maps after the 24-scan pilot have been processed on
`codex/nieuwe-stijl-georeferencing-plan`. This batch covers repeated editions of
sheets 101–117 in series D.02. It excludes the pilot scans and all D.01 sheet indices.

Load [the combined AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-01/review-annotations.json)
in Allmaps Viewer using the same local-file workflow as the pilot. It contains all
50 candidates, including the maps with numerical review flags. The output is local;
its stable annotation/provenance IDs do not mean those URLs have been published.

## Results

- 50 maps, 200 control points, 50 held-out check points, and 50 individual masks.
- 21 pass the unchanged provisional screen; 29 retain numerical review flags.
- Fit RMS ranges from 0.48 to 3.66 native pixels. Largest held-out error: 5.60 pixels.
- Scans 823 and 847 exceed the five-pixel check limit (5.60 and 5.04 respectively).
- All 250 point centres, native frame/title details, and 50 final mask overlays were
  inspected with AI vision. Human review of this batch remains pending.
- The Allmaps polynomial1 Mercator implementation differs from the authoritative
  RD affine by at most 1.16 ground metres on the saved sample grids. This is a
  numerical compatibility check, not a browser screenshot test or survey accuracy.
- Evidence: 50 overviews, 200 initial corner crops and 15 adaptive detail crops;
  265 unique image requests, 45,108,672 bytes. Acquisition was serial, at least one
  second between requests, with caching and a 12-detail-per-map cap. Measurement
  and export use no network requests. No full-resolution whole scans were requested.

The canonical observations, source metadata, original printed coordinates, unit
conventions, coordinate derivations, evidence checksums, adjustment diagnostics and
review notes are saved in
[`batches/batch-01/`](../../data/georeferencing/nieuwe-stijl/batches/batch-01).
The combined annotation preserves native masks, control coordinates, original RD
values and archival metadata. Held-out points remain in canonical records and do
not enter the Allmaps fit.

23 sheets use RD Old (EPSG:28991), converted to RD New with the documented origin
shift; 27 use RD New directly. Original values are retained. Geographic conversion
uses the same pinned PROJ operation as the pilot. Assumed pixel uncertainty and
shared border anchors still limit the interpretation of residuals. User acceptance
of the pilot did not change any numerical limit or calibrate measurement uncertainty.

## Lessons applied

SIFT/RANSAC registration between editions supplied image-position proposals only.
Each edition's actual crosses and printed labels were checked independently. Some
registrations with apparently good inlier counts still landed on text or blank
areas; these proposals were replaced by direct observations. Arrowheads were not
used as cross centres. Occluded crosses and checks covered by moved title boxes
were replaced with visible grid intersections. The title-box notch moves from left
to right on scan 858, matching that edition. Faint inner frames were distinguished
from outer frames and title lines at native resolution.

Scan 483 has an apparently inconsistent bottom-left northing label; its northing
assignment was traced from the right-border labels instead and this is recorded in
its corrections. The small native adjustment residual and held-out result agree
with that reading. No inferred label replaces the original print in the evidence.

The pilot's `@allmaps/attach` experiment did not improve the absolute checks, so no
attach tie points enter these fits. The batch does not change published release
selection or the pilot's earlier results.

## Reproduction

With the repository's existing Python and Node dependencies installed:

```sh
# Restore exact saved evidence if the local cache is missing; requests are serial.
.venv/bin/python scripts/georeferencing/georeference_batch.py hydrate --batch batch-01
# Recompute from reviewed observations and export the combined local review file.
pnpm georeference:batch
pnpm georeference:validate
```

`measure` rejects missing reviews and stale source records; export rejects stale
geometry approvals and non-numerical unresolved flags. A later point or mask edit
requires inspecting its new artifacts and updating the explicit geometry-review
snapshot. There is no automatic approval command. Initial acquisition and proposal
commands (`select`, `acquire`, `propose`, `packs`) remain available for later batches;
proposals never constitute reviewed observations.

The batch coverage ledger now records 74 prepared maps out of 999, with 925 remaining.
Prepared does not imply human acceptance or release. No commit or deployment was made.

## Per-scan numerical screen

| Inventory | Fit RMS (px) | Held-out error (px) | Screen |
| --- | ---: | ---: | --- |
| 822 | 2.70 | 2.49 | rms-above-2px |
| 823 | 3.16 | 5.60 | rms-above-2px, check-above-5px |
| 479 | 1.98 | 1.24 | Pass |
| 826 | 0.92 | 0.79 | Pass |
| 825 | 0.85 | 0.56 | Pass |
| 824 | 0.91 | 3.27 | Pass |
| 480 | 0.50 | 2.42 | Pass |
| 827 | 3.66 | 1.37 | rms-above-2px |
| 828 | 2.68 | 1.82 | rms-above-2px |
| 830 | 2.38 | 1.21 | rms-above-2px |
| 829 | 3.10 | 3.20 | rms-above-2px |
| 832 | 3.25 | 3.03 | rms-above-2px |
| 833 | 2.99 | 2.28 | rms-above-2px |
| 831 | 2.78 | 2.16 | rms-above-2px |
| 497 | 2.20 | 3.87 | rms-above-2px |
| 834 | 3.03 | 1.92 | rms-above-2px |
| 836 | 2.49 | 1.18 | rms-above-2px |
| 835 | 2.26 | 4.06 | rms-above-2px |
| 838 | 2.18 | 1.39 | rms-above-2px |
| 837 | 1.65 | 1.23 | Pass |
| 839 | 1.71 | 1.11 | Pass |
| 840 | 1.77 | 1.56 | Pass |
| 841 | 2.42 | 2.78 | rms-above-2px |
| 842 | 2.00 | 1.44 | Pass |
| 844 | 2.32 | 1.28 | rms-above-2px |
| 843 | 1.61 | 0.93 | Pass |
| 845 | 2.20 | 1.68 | rms-above-2px |
| 847 | 3.51 | 5.04 | rms-above-2px, check-above-5px |
| 846 | 2.84 | 2.41 | rms-above-2px |
| 481 | 2.38 | 2.44 | rms-above-2px |
| 848 | 3.42 | 1.81 | rms-above-2px |
| 849 | 2.82 | 1.05 | rms-above-2px |
| 482 | 2.55 | 1.30 | rms-above-2px |
| 851 | 2.74 | 2.74 | rms-above-2px |
| 850 | 2.23 | 3.19 | rms-above-2px |
| 483 | 1.66 | 2.85 | Pass |
| 853 | 1.11 | 0.50 | Pass |
| 852 | 1.40 | 1.47 | Pass |
| 484 | 0.48 | 0.51 | Pass |
| 855 | 1.05 | 0.33 | Pass |
| 854 | 1.94 | 1.24 | Pass |
| 485 | 1.62 | 1.01 | Pass |
| 857 | 2.10 | 1.49 | rms-above-2px |
| 856 | 1.25 | 0.41 | Pass |
| 486 | 1.81 | 0.47 | Pass |
| 859 | 2.55 | 2.35 | rms-above-2px |
| 858 | 1.75 | 1.28 | Pass |
| 487 | 2.38 | 1.73 | rms-above-2px |
| 861 | 1.74 | 1.84 | Pass |
| 860 | 2.18 | 1.37 | rms-above-2px |
