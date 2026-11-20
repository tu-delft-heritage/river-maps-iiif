# Georeferencing River Maps

## Scans from Utrecht University Library

### First edition

#### Series 1
_Boven Rijn, de Waal, de Merwede, de Oude en een gedeelte van de Nieuwe Maas, van Lobith tot Brielle_

- https://objects.library.uu.nl/reader/20.500.14918-462061
- https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462061

#### Series 2
_Boven en Neder-Rijn, de Lek en de Nieuwe Maas, van Lobith tot Brielle_

- https://objects.library.uu.nl/reader/20.500.14918-462106
- https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462106

#### Series 3
_IJssel van Westervoort tot Kampen_

- https://objects.library.uu.nl/reader/20.500.14918-462062
- https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462062

#### Series 4
_Boven Maas van Visé tot Woudrichem_

- https://objects.library.uu.nl/reader/20.500.14918-462072
- https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462072

#### Series 5
_Oude en Nieuwe Merwede en de killen in het Bergsche Veld_

- https://objects.library.uu.nl/reader/20.500.14918-462108
- https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462108

#### Series 6
_Hollandsche IJssel van Gouda tot IJsselmonde_

- https://objects.library.uu.nl/reader/20.500.14918-462063
- https://objects.library.uu.nl/manifest/iiif/v3/20.500.14918-462063

## Tools to use

- [IIIF Manifest Editor](https://manifest-editor.digirati.services/)
- [Allmaps Editor](https://editor.allmaps.org/?lang=en)
- [Map Series Editor](https://github.com/allmaps/map-series-editor)

## Scans from Nationaal Archief

The **Nieuwe Stijl** edition uses digitized records in section D of
[inventory 2.16.5150](https://www.nationaalarchief.nl/onderzoeken/archief/2.16.5150).
Its microfilms were digitized in mid-2025. The saved inventory version is
30 July 2026; metadata was retrieved on 19 November 2026.

[`iiif/collections/nieuwe-stijl.json`](iiif/collections/nieuwe-stijl.json) contains
**17 Presentation 3 Manifests and 1,009 image Canvases**. One Manifest corresponds
to each group D.01–D.17, in inventory order: 15 river groups, the index/legend
sheets, and the Netherlands–Belgium border-agreement appendices. Subgroups under
D.01 and D.05 are retained as IIIF Ranges. Only records with digital-object links
and resolved scans are included; descriptions without scans produce no Canvas.
Earlier, undigitized editions in this inventory are not added.

The collection's public URL after deployment is:

<https://tu-delft-heritage.github.io/river-maps-iiif/collections/nieuwe-stijl.json>

Canvas metadata retains Dutch titles, inventory numbers, handles and UUIDs,
dates (including normalized dates), scales, photography notes, duplicate-copy
notes, related material, processing notes, and inherited series descriptions.
Each Canvas links to its archival description, METS record, Image API metadata,
and full-resolution JPEG. Original Image API 3 services, capabilities, resolution
limits, and physical-scale information are preserved. The METS records classify
all 1,009 scans as public domain; the generated resources use the Public Domain
Mark and credit Nationaal Archief. Source images remain hosted by the archive.

The exact EAD XML, full METS XML responses, and Image API responses are saved in
[`data/nationaal-archief/`](data/nationaal-archief). The complete EAD is retained
as source evidence, including descriptions that are excluded from the IIIF
collection. A copy is published under `iiif/sources/nationaal-archief/` and linked
with `seeAlso`; the build checks its SHA-256 against the metadata snapshot.
Catalog sync does not download map images. The georeferencing pilot caches small photographic overviews and details locally; those images are ignored by Git.

To refresh this source (Python 3, standard library only):

```sh
pnpm sync:na
pnpm validate
```

`sync:na` downloads the current EAD and resolves every linked METS record and
image's `info.json`. It caches completed requests in `.cache/nationaal-archief/`,
limits request rates, and retries temporary failures. It leaves committed source
files untouched if any download or parse fails. Run `pnpm sync:na --refresh` to
also refresh cached METS and image metadata. `--ead /path/to/inventory.xml` accepts
a specific local EAD snapshot. Builds and tests use only the committed files and
do not require network access. The importer lives in
[`scripts/sync-nationaal-archief.py`](scripts/sync-nationaal-archief.py); IIIF
generation lives in [`scripts/nationaal-archief.ts`](scripts/nationaal-archief.ts).

## Published georeferencing and navigation

All **999 Nieuwe Stijl maps in D.02–D.17** have been visually reviewed, including
the corrected placements. Each series has an AnnotationPage under
[`iiif/annotations/nieuwe-stijl/`](iiif/annotations/nieuwe-stijl), linked from the
[index](iiif/index.html), its Manifest and its Canvases. The index opens the hosted
annotations directly in Allmaps Viewer. D.01 contains ten index/legend scans and
has no georeference annotations. Only the reviewed Nieuwe Stijl release is
published; First Edition manifests and scans have no georeference annotations.

The release preserves original projected observations (including RD Old where
printed), converted RD New coordinates, WGS84 control points, archival metadata,
held-out checks, human approval fingerprints and numerical flags. See the
[release provenance](iiif/georeferencing/nieuwe-stijl/release.json).

Each georeferenced Canvas has a `navPlace` GeoJSON FeatureCollection containing
a Polygon of its transformed mask. `@allmaps/transform` fits the annotation's
transformation in Web Mercator, as Allmaps Viewer does, then converts the refined
boundary to WGS84 longitude/latitude. Rings are closed and counterclockwise;
these are map extents, not rectangular image bounds. Manifests include the
[IIIF navPlace context](https://iiif.io/api/extension/navplace/).

Canvas `navDate` uses the latest valid date in that sheet's own `Datering` and
`Datering (ISO)` metadata, including later additions. Malformed ISO values are
ignored when the written date provides usable evidence. Conflicting valid dates
use the latest one; the original fields are retained and the discrepancies are
listed in the [navigation audit](iiif/georeferencing/navigation-report.json).
For month/year precision, missing components use the start of that period at
midnight UTC as a navigation convention, not an assertion of exact dating.
Undated sheets and sheets without their own date metadata are omitted. Broad
series publication ranges and digitization dates are not assigned to sheets.
There are 998 dated Nieuwe Stijl Canvases and 11 without a usable date; the 144
Utrecht Canvases have no sheet-level dates. There are 999 geographic masks, all for reviewed Nieuwe Stijl maps.

The reviewed publication inputs live in `data/iiif-annotations/`; `pnpm build`
validates the Nieuwe Stijl checksums and generates their published copies plus
navigation properties. This build needs no image cache, CV pipeline or Python
georeferencing environment. Source metadata changes require a matching reviewed
publication snapshot. Pages continues to publish committed `iiif/` files.

The processing scripts, canonical measurements, approval history, diagnostics,
local dashboard, and illustrated essay are retained on branch
`codex/nieuwe-stijl-georeferencing-plan`.

## IIIF collection

The IIIF Presentation 3 collection is generated with Node.js 24, TypeScript,
[pnpm](https://pnpm.io/), and [@iiif/helpers](https://github.com/IIIF-Commons/iiif-helpers).

The entry point is [`iiif/collection.json`](iiif/collection.json). Once deployed,
its public URL is:

<https://tu-delft-heritage.github.io/river-maps-iiif/collection.json>

```text
River maps (collection.json)
├── First edition (collections/first-edition.json)
│   ├── Series 1 (manifests/first-edition/series-1.json)
│   ├── Series 2 (manifests/first-edition/series-2.json)
│   ├── Series 3 (manifests/first-edition/series-3.json)
│   ├── Series 4 (manifests/first-edition/series-4.json)
│   ├── Series 5 (manifests/first-edition/series-5.json)
│   └── Series 6 (manifests/first-edition/series-6.json)
└── Nieuwe Stijl (collections/nieuwe-stijl.json)
    ├── D.01 Index sheets and legends (manifests/nieuwe-stijl/series-01.json)
    ├── D.02–D.16 River groups (manifests/nieuwe-stijl/series-02.json … series-16.json)
    └── D.17 Border-agreement appendices (manifests/nieuwe-stijl/series-17.json)
```

Future editions become sibling collections; existing URLs remain stable. There
are no empty placeholder editions.

### Local development

Requires Node.js 24+, pnpm, and Python 3 (for Nationaal Archief sync and source checks).

```sh
pnpm install --frozen-lockfile
pnpm validate
```

- `pnpm sync` downloads and checks the library manifests listed in
  [`scripts/catalog.ts`](scripts/catalog.ts). It replaces the local source JSON
  only after every download succeeds. Refreshing requires internet access.
- `pnpm sync:na` refreshes Nationaal Archief metadata as described above.
- `pnpm build` generates `iiif/` entirely from local source files, without network
  access, including the manifest browse page. The directory is generated output
  and is replaced on each build.
- `pnpm check` checks the TypeScript types.
- `pnpm test` checks record identities, collection links, additional editions,
  custom base URLs, parsing with the IIIF Vault, preservation of source data,
  complete EAD-to-scan coverage, and exclusion of undigitized descriptions.
- `pnpm validate` runs the type check, tests, and build.

Commit the source manifests in `data/iiif-manifests/`, the archive snapshots in
`data/nationaal-archief/`, the generated `iiif/`
files (including `index.html` and `assets/`), and `pnpm-lock.yaml`. GitHub Pages
publishes the committed `iiif/` directory as-is; it does not run these scripts.
Run `pnpm validate` locally after changing sources, the catalog, or the website,
then commit the regenerated output. Only run `pnpm sync` when adding or refreshing
library records; use `pnpm sync:na` for archive records.

The Utrecht source JSON is preserved as downloaded, with formatting applied. Published
manifests receive local IDs, readable series labels, an edition `partOf` link,
and a `seeAlso` link to the original manifest. The original library label is
retained in metadata. All embedded canvas and annotation IDs, image URLs,
image services, descriptive metadata, and attribution remain intact. Images
continue to be served by Utrecht University Library; they are not downloaded.

The checks catch missing/wrong records and broken collection links; they are not
a comprehensive IIIF schema validator.

### Website

The homepage is a plain list of manifests grouped by edition, with direct JSON
links and links to Allmaps Editor, IIIF Manifest Editor, and Theseus Viewer.
The main collection and each edition have the same tool links; collection links
open as collections in IIIF Manifest Editor.
It follows the generated collection tree on every build, so
new editions and series appear automatically without editing the page.

The lightweight framework is [Preact](https://preactjs.com/), rendered at build
time with `preact-render-to-string` and HTM templates. The deployed page is static
HTML and CSS, with no browser JavaScript, external fonts, or runtime CDN
dependencies. Components and link generation live in `scripts/site.ts`; styles
live in `site/style.css`. The existing Pages workflow deploys the page and its
stylesheet alongside the IIIF JSON.

Tool links use the published collection and manifest IDs (including a custom `IIIF_BASE_URL`),
while JSON and stylesheet links are relative to the homepage. The Manifest Editor
link imports a copy into that editor; it does not change the JSON in this repo.

Link formats are based on [Allmaps' workshop guide](https://pages.allmaps.org/workshops/2026-open-science-week.html),
[Manifest Editor's import handler](https://github.com/digirati-co-uk/iiif-manifest-editor/blob/main/apps/web/src/components/share/SharePage.tsx),
and [its Theseus integration](https://github.com/digirati-co-uk/iiif-manifest-editor/blob/main/apps/docs/content/developer/previews.mdx).

### Adding an edition or series

For sources that already provide IIIF manifests:

1. Add an edition or series to `scripts/catalog.ts`, with a stable slug, label,
   and the source Presentation 3 manifest URL. Slugs become public URL paths.
2. Run `pnpm sync` and inspect the downloaded records and titles.
3. Run `pnpm validate` and commit the catalog, source JSON, and generated JSON.

Nationaal Archief's Nieuwe Stijl groups are discovered directly from section D
of the EAD instead of being entered in `scripts/catalog.ts`. A refresh updates
the series, descriptions and scans together. Existing Canvas IDs use archival
and scan UUIDs, so changes to source order do not change their identity.

For another host, repository path, or local server, set the public base URL:

```sh
IIIF_BASE_URL=https://example.org/river-maps/ pnpm build
```

This changes collection/manifest IDs and collection links, while retaining
library canvas IDs and all remote image service URLs. New Nationaal Archief
Canvas, annotation and Range IDs use fragments of their Manifest URL and follow
the configured host. Run `pnpm build` without the variable
to restore the default GitHub Pages URLs before committing generated files.

### GitHub Pages

[The workflow](.github/workflows/pages.yml) publishes the committed `iiif/`
directory using checkout, configure-pages, upload-pages-artifact, and deploy-pages.
It does not install Node.js or pnpm, download library data, run tests, or rebuild
the collection or website. Generation and validation are local development steps.

Pushes to `watertijdreis` deploy only when `iiif/**` or the workflow itself changes.
Documentation-only and source-only commits do not trigger deployment. Pull
requests do not deploy.

Manual runs deploy the selected branch's committed `iiif/` directory. Choose
**Actions → Deploy IIIF to GitHub Pages → Run workflow**, select the branch
(for example, `watertijdreis`), and run it. The `github-pages` environment must
allow that branch; `main` and `watertijdreis` are currently allowed. Manual runs
publish to the same public site, and deployments are serialized across branches.

When changing the public domain or repository path, regenerate locally with
`IIIF_BASE_URL` set to the final Pages URL and commit the output before deploying.
The workflow publishes the IDs and tool links exactly as committed.

In the repository's **Settings → Pages → Build and deployment**, set **Source**
to **GitHub Actions** before the first deployment. This repository already uses
that setting. Commit and push the workflow and all generated `iiif/` files before
running it. No personal access token is required; deployment uses the workflow's
`GITHUB_TOKEN` and its `github-pages` environment.

References: [IIIF Presentation 3 collections](https://iiif.io/api/presentation/3.0/#51-collection)
and [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

On this research branch, start with [the workspace guide](docs/georeferencing/research-workspace.md) and [the illustrated essay](docs/georeferencing/nieuwe-stijl-georeferencing-essay.md).
