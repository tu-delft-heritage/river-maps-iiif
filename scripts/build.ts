import { copyFile, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { defaultBaseUrl, editions } from './catalog.ts';
import { generateCollection, sourcePath } from './collection.ts';
import { renderBrowsePage } from './site.ts';

const root = fileURLToPath(new URL('../', import.meta.url));
const output = resolve(root, 'iiif');
const sources = new Map<string, unknown>();
for (const edition of editions) {
  for (const series of edition.series) {
    const path = sourcePath(edition, series);
    try {
      sources.set(path, JSON.parse(await readFile(resolve(root, path), 'utf8')));
    } catch (cause) {
      throw new Error(`Cannot read ${path}. Run pnpm sync to download the source manifests.`, { cause });
    }
  }
}
// Generate and validate in memory before replacing any existing output. No network is used.
const documents = generateCollection(editions, sources, process.env.IIIF_BASE_URL ?? defaultBaseUrl);
const page = renderBrowsePage(documents);
await rm(output, { recursive: true, force: true });
for (const [path, document] of documents) {
  const destination = resolve(output, path);
  await mkdir(dirname(destination), { recursive: true });
  await writeFile(destination, `${JSON.stringify(document, null, 2)}\n`);
}
await writeFile(resolve(output, '.nojekyll'), '');
await writeFile(resolve(output, 'index.html'), page);
await mkdir(resolve(output, 'assets'), { recursive: true });
await copyFile(resolve(root, 'site/style.css'), resolve(output, 'assets/site.css'));
console.log(`Built ${documents.size} IIIF documents and the browse page in iiif/.`);
