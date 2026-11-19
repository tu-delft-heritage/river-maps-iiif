import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { getValue } from '@iiif/helpers/i18n';
import { editions } from './catalog.ts';
import { assertSourceManifest, sourcePath, validateCatalog } from './collection.ts';

const root = fileURLToPath(new URL('../', import.meta.url));
validateCatalog(editions);
const downloads = new Map<string, string>();
for (const edition of editions) {
  for (const series of edition.series) {
    const response = await fetch(series.source, {
      headers: { Accept: 'application/ld+json, application/json' },
      signal: AbortSignal.timeout(30_000),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status} downloading ${series.source}`);
    const manifest: unknown = await response.json();
    assertSourceManifest(manifest, series.source);
    downloads.set(sourcePath(edition, series), `${JSON.stringify(manifest, null, 2)}\n`);
    console.log(`${edition.slug}/${series.slug}: ${getValue(manifest.label)} (${manifest.items.length} canvases)`);
  }
}
// A failed download leaves all existing source files untouched.
for (const [path, contents] of downloads) {
  const destination = resolve(root, path);
  await mkdir(dirname(destination), { recursive: true });
  await writeFile(destination, contents);
}
console.log(`Saved ${downloads.size} source manifests. Run pnpm build to regenerate iiif/.`);
