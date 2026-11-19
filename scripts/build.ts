import { copyFile, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { defaultBaseUrl, editions } from './catalog.ts';
import { generateCollection, sourcePath } from './collection.ts';
import { renderBrowsePage } from './site.ts';
import {
  archiveEadPath, archiveSnapshotPath, generateArchiveCollection, publishedEadPath,
  type ArchiveSnapshot,
} from './nationaal-archief.ts';

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
const archive: ArchiveSnapshot = JSON.parse(await readFile(resolve(root, archiveSnapshotPath), 'utf8'));
const ead = await readFile(resolve(root, archiveEadPath));
if (createHash('sha256').update(ead).digest('hex') !== archive.eadSha256) {
  throw new Error('Nationaal Archief EAD and metadata snapshot differ. Run pnpm sync:na again.');
}
const archiveDocuments = generateArchiveCollection(archive, process.env.IIIF_BASE_URL ?? defaultBaseUrl);
const main = documents.get('collection.json')!;
if (main.type !== 'Collection') throw new Error('Expected root collection');
for (const [path, document] of archiveDocuments) {
  if (documents.has(path)) throw new Error(`Duplicate IIIF document: ${path}`);
  documents.set(path, document);
  if (document.type === 'Collection') {
    main.items!.push({ id: document.id, type: 'Collection', label: document.label });
  }
}
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
await mkdir(dirname(resolve(output, publishedEadPath)), { recursive: true });
await writeFile(resolve(output, publishedEadPath), ead);
console.log(`Built ${documents.size} IIIF documents and the browse page in iiif/.`);
