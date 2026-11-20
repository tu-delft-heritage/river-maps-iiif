# Placement corrections after the 20 November review

The user has approved all eight corrected placements and their corresponding series, D.07, D.08, D.11 and D.15. Together with the earlier series approvals, **all 999 digitized maps are now visually accepted; none remain pending**. Acceptance is recorded against each map’s exact saved geometry.

The [combined eight-map AnnotationPage](../../dashboard/annotations/recheck-2026-11-20.json) contains the six reported scans and two additional D.08 copies discovered by screening the whole collection. Open the [dashboard’s follow-up review group](../../dashboard/index.html#review-2026-11-20) for its direct Allmaps Viewer link. All eight corrected placements have been accepted in human review. Nothing was committed.

## What changed

The errors were in the coordinate assignments. The source photographs and all eight native masks are unchanged. Original border strings and signed projected coordinates are preserved, with a correction history recording the previous and corrected assignments. The earlier coordinates are retained in complete [before records](../../data/georeferencing/nieuwe-stijl/rechecks/2026-11-20/before).

| Inventory | Series | Cause and correction | Principal scale ratio, before → after | Held-out check, before → after (px) |
| --- | --- | --- | ---: | ---: |
| 1123 | D.07 | Eastings and northings were transposed; swapped all five coordinate pairs. | 1.0003 → 1.0003; reflection removed | 1.37 → 1.37 |
| 1148 | D.08 | Top-right easting 98,600 → 98,800 m; bottom-left 97,800 → 97,600 m. | 1.2828 → 1.0004 | 0.70 → 0.68 |
| 1149 | D.08 | Same two 200 m easting errors; rechecked this copy’s own labels. | 1.2832 → 1.0003 | 1.69 → 1.73 |
| 625 | D.08 | Additional suspect: same two easting errors on another copy of sheet 505/610. | 1.2838 → 1.0020 | 2.59 → 2.57 |
| 1151 | D.08 | Additional suspect: same two easting errors on another copy of sheet 505/610. | 1.2830 → 1.0003 | 0.50 → 0.44 |
| 1284 | D.11 | All five northings were 400 m too high; corrected from this scan’s own border labels. | 1.0003 → 1.0003 | 1.53 → 1.53 |
| 751 | D.15 | Bottom-right easting 97,800 → 98,000 m; bottom-left 96,000 → 96,200 m. | 1.2632 → 1.0008 | 45.74 → 0.67 |
| 1381 | D.15 | Bottom-right easting −66,800 → −66,600 m; bottom-left −68,200 → −68,000 m. | 1.2292 → 1.0006 | 30.93 → 1.44 |

The four D.08 copies shared a consistent but sheared coordinate assignment. Their small residuals did not reveal the problem: the affine fit could reproduce the same mistake across controls and check. Inventory 1123 similarly had a neat but reflected fit. On 1284 the wrong northings moved the entire map without changing its shape or residuals. Its top border explicitly reads −39,200, −39,000 and −38,800; the old assignments were two 200 m steps too high.

Inventories 751 and 1381 were previously described as having unexplained residuals, with paper/scan distortion offered only as a possibility. That hypothesis is superseded by the verified grid-step corrections. Their held-out errors fall from 45.74 and 30.93 pixels to 0.67 and 1.44 pixels. Their remaining RMS errors exceed the existing 2-pixel screen, so those numerical flags remain visible.

1123 also exposed a provenance ambiguity: the same printed number can label either axis on one sheet. Its point-to-border dependencies now specify the visually checked axis and border location explicitly, rather than assigning an axis solely by numeric proximity.

## Collection-wide shape screen

Every one of the **999 saved RD-to-image transforms** was screened for:

- **Reflection:** a positive determinant, accounting for north-positive RD coordinates and downward-positive image pixels.
- **Unequal stretching:** a ratio above **1.02** between the largest and smallest directional scale factors (the singular values of the affine matrix).
- **Skew:** projected grid axes deviating more than **1°** from a right angle.

These are review triggers, separate from the unchanged 2-pixel RMS and 5-pixel held-out thresholds. Before correction, seven maps triggered the shape screen: five reported maps and **625 and 1151**. The eighth, 1284, was selected from the user’s report of a displacement. The remaining 992 maps’ largest directional scale ratio was about 1.00345.

After correction, **no maps trigger the shape screen**. This does not rule out a shared coordinate-origin error, a rotation, or a uniform scaling error. Those can preserve shape and require border or geographic evidence. The eight corrected maps remain together as a record of the completed review; their shape flags are clear.

The [before audit](../../data/georeferencing/nieuwe-stijl/rechecks/2026-11-20/shape-audit-before.json) and [current audit](../../dashboard/shape-audit.json) cover all 999 maps, with geometry fingerprints. The [case records](../../data/georeferencing/nieuwe-stijl/rechecks/2026-11-20/cases.json) preserve detailed reasons and before/after diagnostics. Rebuilding the dashboard reruns shape screening and includes any new shape suspects in the follow-up group.

## Verification

All source corner labels needed for these corrections were re-inspected from cached native sections. The final 40 control/check patches were visually checked; all masks match their earlier reviewed outlines. Fitting, held-out checks, coordinate conversions, Allmaps parsing and renderer comparisons were rerun for the affected batches. No new IIIF requests were needed. Human acceptance remains separate from these checks.
