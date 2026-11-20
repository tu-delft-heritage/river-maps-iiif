# Nieuwe Stijl batch 02 — D.02 visually accepted

The [combined AnnotationPage](../../data/georeferencing/nieuwe-stijl/batches/batch-02/review-annotations.json) contains the remaining 24 digitized maps in D.02, sheets 117–125. Load this local JSON in Allmaps Viewer using the same workflow as the previous batches. All 24 are included, including numerical review flags. Sheet indices and previously prepared scans are excluded.

The user accepted these remaining 24 maps on 2026-11-19. D.02 now has all 76 maps visually accepted. The [dashboard](../../dashboard/index.html) reports current project totals separately and provides batch and series downloads, direct Allmaps Viewer links and map filters. Work remains on `codex/nieuwe-stijl-georeferencing-plan`, without a new commit or deployment.

## Results and evidence

- 24 individual masks, 96 control points and 24 held-out check points.
- 7 pass the unchanged numerical screen; 17 exceed the two-pixel RMS threshold. Scan 871 also exceeds the five-pixel check threshold (5.57 pixels).
- Fit RMS ranges from 1.20 to 3.62 native pixels. The largest sampled difference between the Allmaps Mercator polynomial1 transform and the authoritative RD affine is 0.90 ground metres.
- 9 scans use RD Old (EPSG:28991); 15 use RD New (EPSG:28992). Original projected coordinates, printed metre/kilometre units, border transcription, source metadata and evidence checksums remain in canonical records. Exported controls retain the original projected coordinates. Check points are excluded from the fit and remain in canonical records.
- All 120 final point patches and 24 mask overlays were inspected with AI vision, together with native border/frame/title details. Geometry approval and subsequent human acceptance are bound to exact coordinates.
- Acquisition used 24 overviews and 96 native corner sections: 120 cached images, 20,980,949 bytes. There were 121 network attempts including one retry, serially throttled at least one second apart. Measurement and export were offline. No whole native-resolution scans were requested.

Automatic registration supplied candidate image positions only. Later editions frequently moved title boxes, changed the coordinate typography or invalidated cross proposals. These were checked against each scan and corrected from native evidence. Scan 875 has a bottom table away from the corner; its mask uses a notch around it. Later scan 495 moves the title to the bottom left. No overlap tie points enter the absolute adjustment.

Residuals test internal consistency, not historical survey accuracy. Pixel uncertainty is assumed, and controls and checks share border anchors. Numerical flags and release eligibility are unchanged by visual acceptance. The Allmaps comparison is a numerical compatibility check, not a browser or independent survey validation.

## Reproduction

```sh
# Restore the exact saved evidence only if needed (serial requests, cached).
.venv/bin/python scripts/georeferencing/georeference_batch.py hydrate --batch batch-02
# Recompute locally and refresh the review annotation and dashboard.
.venv/bin/python scripts/georeferencing/georeference_batch.py measure --batch batch-02 --offline
node scripts/georeferencing/georeference-batch-export.ts batch-02
pnpm georeference:validate
```

This batch used the legacy limited selection. New batches default to one complete remaining series; the optional 1–50 limit remains for reproducing earlier selections. Saved selections remain immutable. Reviewed observations, geometry snapshots, evidence ledgers, adjustment and viewer reports are under [`batches/batch-02/`](../../data/georeferencing/nieuwe-stijl/batches/batch-02).

## Dashboard

Open `dashboard/index.html` directly in a browser. It is a local snapshot regenerated on export, with no remote fonts, libraries or map-image requests. Filter by series, inventory, review state or numerical flags. Download all prepared maps or one batch at a time.

`human-reviews.json` records the user's acceptance of the pilot and batches 01–02, with geometry fingerprints. A later change to a mask, control or original coordinate invalidates that acceptance. AI geometry review is checked independently before an annotation is counted as prepared. Updating the dashboard does not release annotations or mark new maps accepted.
