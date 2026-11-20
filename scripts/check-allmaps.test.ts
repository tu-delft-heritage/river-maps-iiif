import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile, mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { IIIF, type Canvas } from '@allmaps/iiif-parser';
import { defaultBaseUrl, editions } from './catalog.ts';
import { generateCollection, sourcePath } from './collection.ts';
import { archiveSnapshotPath, generateArchiveCollection } from './nationaal-archief.ts';
import { publishGeoreferencing } from './published-georeferencing.ts';
import { validateAllmapsDocuments, checkPublishedAllmaps } from './check-allmaps.ts';
import type { Manifest } from '@iiif/presentation-3';

const read = async (path: string) => JSON.parse(await readFile(new URL('../' + path, import.meta.url), 'utf8'));
const sources = new Map<string, unknown>();
for (const edition of editions) for (const series of edition.series) sources.set(sourcePath(edition, series), await read(sourcePath(edition, series)));
const presentations = generateCollection(editions, sources, defaultBaseUrl);
for (const [path, document] of generateArchiveCollection(await read(archiveSnapshotPath), defaultBaseUrl)) presentations.set(path, document);
const georeferencing = await publishGeoreferencing(presentations);
const documents = new Map<string, unknown>([
  ...presentations, ...[...georeferencing.files].filter(([path]) => path.startsWith('annotations/')),
]);
const manifestPath = 'manifests/nieuwe-stijl/series-02.json';

test('Allmaps accepts every final collection, manifest and annotation page without mutation or network access', t => {
  const fetch = t.mock.method(globalThis, 'fetch', () => {throw new Error('Parser validation must remain offline');});
  const original = JSON.stringify([...documents]);
  assert.deepEqual(validateAllmapsDocuments(documents), {
    collections: 3, manifests: 23, canvases: 1153, annotationPages: 16, maps: 999,
  });
  assert.equal(JSON.stringify([...documents]), original);
  assert.equal(fetch.mock.callCount(), 0);
});

test('the actual missing provider homepage label is rejected with the manifest path and parser diagnostics', () => {
  const manifest = structuredClone(presentations.get(manifestPath) as Manifest);
  const homepage = manifest.provider![0].homepage![0] as {id: string; label?: unknown};
  assert.equal(homepage.id, 'https://www.nationaalarchief.nl/');
  assert.deepEqual(homepage.label, {nl: ['Nationaal Archief']});
  delete homepage.label;
  assert.throws(() => validateAllmapsDocuments(new Map([[manifestPath, manifest]])), (error: unknown) => {
    assert.ok(error instanceof Error);
    assert.ok(error.message.includes(manifestPath));
    assert.match(error.message, /provider/);
    assert.match(error.message, /homepage/);
    assert.match(error.message, /label/);
    assert.ok(error.cause instanceof Error);
    return true;
  });
});

test('Allmaps retains the archival homepage links, navigation dates and geographic masks', () => {
  for (const document of presentations.values()) {
    if (document.type !== 'Manifest') continue;
    const parsed = IIIF.parse(document);
    assert.equal(parsed.type, 'manifest');
    if (parsed.type !== 'manifest') throw new Error('Expected a manifest');
    assert.equal(parsed.homepage?.[0].id, document.homepage?.[0].id);
    assert.equal(parsed.provider?.[0].homepage?.[0].id, document.provider?.[0].homepage?.[0].id);
    for (const [i, canvas] of document.items.entries()) {
      const converted: Canvas = parsed.canvases[i];
      assert.equal(converted.homepage?.[0].id, canvas.homepage?.[0].id);
      assert.equal(converted.navDate?.getTime(), canvas.navDate ? Date.parse(canvas.navDate) : undefined);
      assert.deepEqual(converted.navPlace, (canvas as {navPlace?: unknown}).navPlace);
    }
  }
});

test('malformed georeference annotations are rejected by the annotation package with the page path', () => {
  const path = 'annotations/nieuwe-stijl/series-17.json';
  const page = structuredClone(documents.get(path)) as {items: {body: {features: {geometry: {coordinates: unknown[]}}[]}}[]};
  page.items[0].body.features[0].geometry.coordinates[0] = 'not a longitude';
  assert.throws(() => validateAllmapsDocuments(new Map([[path, page]])), /Allmaps rejected annotations\/nieuwe-stijl\/series-17.json/);
});

test('the deployment check reads committed files without rebuilding or repairing invalid JSON', async () => {
  const output = await mkdtemp(join(tmpdir(), 'river-maps-parser-'));
  try {
    for (const folder of ['collections', 'manifests/nieuwe-stijl', 'annotations/nieuwe-stijl']) await mkdir(join(output, folder), {recursive: true});
    const root = {id: 'https://example.org/collection.json', type: 'Collection', label: {en: ['Maps']}, items: []};
    const manifest = 'manifests/nieuwe-stijl/series-17.json';
    const page = 'annotations/nieuwe-stijl/series-17.json';
    for (const [path, doc] of [['collection.json', root], [manifest, documents.get(manifest)], [page, documents.get(page)]] as const) {
      await writeFile(join(output, path), JSON.stringify(doc));
    }
    assert.deepEqual(await checkPublishedAllmaps(output), {collections: 1, manifests: 1, canvases: 3, annotationPages: 1, maps: 3});
    await writeFile(join(output, manifest), '{invalid');
    await assert.rejects(checkPublishedAllmaps(output), /Cannot read published IIIF JSON: manifests\/nieuwe-stijl\/series-17.json/);
    assert.equal(await readFile(join(output, manifest), 'utf8'), '{invalid');
  } finally {
    await rm(output, {recursive: true, force: true});
  }
});
