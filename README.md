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
## IIIF collection

The IIIF Presentation 3 collection is generated with Node.js 24, TypeScript,
[pnpm](https://pnpm.io/), and [@iiif/helpers](https://github.com/IIIF-Commons/iiif-helpers).

The entry point is [`iiif/collection.json`](iiif/collection.json). Once deployed,
its public URL is:

<https://tu-delft-heritage.github.io/river-maps-iiif/collection.json>

```text
River maps (collection.json)
└── First edition (collections/first-edition.json)
    ├── Series 1 (manifests/first-edition/series-1.json)
    ├── Series 2 (manifests/first-edition/series-2.json)
    ├── Series 3 (manifests/first-edition/series-3.json)
    ├── Series 4 (manifests/first-edition/series-4.json)
    ├── Series 5 (manifests/first-edition/series-5.json)
    └── Series 6 (manifests/first-edition/series-6.json)
```

Future editions become sibling collections; existing URLs remain stable. There
are no empty placeholder editions.

### Local development

```sh
pnpm install --frozen-lockfile
pnpm validate
```

- `pnpm sync` downloads and checks the library manifests listed in
  [`scripts/catalog.ts`](scripts/catalog.ts). It replaces the local source JSON
  only after every download succeeds. Refreshing requires internet access.
- `pnpm build` generates `iiif/` entirely from local source files, without network
  access. The directory is generated output and is replaced on each build.
- `pnpm check` checks the TypeScript types.
- `pnpm test` checks record identities, collection links, additional editions,
  custom base URLs, parsing with the IIIF Vault, and preservation of source data.
- `pnpm validate` runs the type check, tests, and build.

Commit the source manifests in `data/iiif-manifests/`, the generated `iiif/`
files, and `pnpm-lock.yaml`. Downloads are separate from builds so publishing
works even when the library's server is unavailable.

The source JSON is preserved as downloaded, with formatting applied. Published
manifests receive local IDs, readable series labels, an edition `partOf` link,
and a `seeAlso` link to the original manifest. The original library label is
retained in metadata. All embedded canvas and annotation IDs, image URLs,
image services, descriptive metadata, and attribution remain intact. Images
continue to be served by Utrecht University Library; they are not downloaded.

The checks catch missing/wrong records and broken collection links; they are not
a comprehensive IIIF schema validator.

### Adding an edition or series

1. Add an edition or series to `scripts/catalog.ts`, with a stable slug, label,
   and the source Presentation 3 manifest URL. Slugs become public URL paths.
2. Run `pnpm sync` and inspect the downloaded records and titles.
3. Run `pnpm validate` and commit the catalog, source JSON, and generated JSON.

For another host, repository path, or local server, set the public base URL:

```sh
IIIF_BASE_URL=https://example.org/river-maps/ pnpm build
```

This changes collection/manifest IDs and collection links, while retaining
library canvas IDs and image service URLs. Run `pnpm build` without the variable
to restore the default GitHub Pages URLs before committing generated files.

### GitHub Pages

[The workflow](.github/workflows/pages.yml) checks pull requests and deploys pushes
to `main`. It can also be run manually from `main`. It installs the locked pnpm
dependencies, runs the checks, builds from the committed source manifests, and
uploads only `iiif/` using the official GitHub Pages actions. The build uses the
base URL returned by `actions/configure-pages`, including a configured custom
domain. Pull requests and manual runs on other branches do not deploy.

In the repository's **Settings → Pages → Build and deployment**, set **Source**
to **GitHub Actions** before the first deployment. Then merge or push these files
to `main`. No personal access token is required; deployment uses the workflow's
`GITHUB_TOKEN` and its `github-pages` environment.

References: [IIIF Presentation 3 collections](https://iiif.io/api/presentation/3.0/#51-collection)
and [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
