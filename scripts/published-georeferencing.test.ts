import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile, mkdtemp, mkdir, symlink, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseAnnotation } from '@allmaps/annotation';
import { defaultBaseUrl, editions } from './catalog.ts';
import { generateCollection, sourcePath } from './collection.ts';
import { generateArchiveCollection, archiveSnapshotPath } from './nationaal-archief.ts';
import { publishGeoreferencing } from './published-georeferencing.ts';
import { navPlaceContext, signedArea } from './navigation.ts';
import type { Manifest } from '@iiif/presentation-3';

const json = async (path: string) => JSON.parse(await readFile(new URL('../' + path, import.meta.url), 'utf8'));
async function documents(base = defaultBaseUrl) {
  const sources = new Map<string, unknown>();
  for (const e of editions) for (const s of e.series) sources.set(sourcePath(e, s), await json(sourcePath(e, s)));
  const docs = generateCollection(editions, sources, base);
  for (const [path, value] of generateArchiveCollection(await json(archiveSnapshotPath), base)) docs.set(path, value);
  return docs;
}

test('published snapshot contains every reviewed series, and supplies polygons and sheet dates', async () => {
  const docs = await documents();
  const {files, counts} = await publishGeoreferencing(docs);
  const maps = [...files].filter(([p]) => p.startsWith('annotations/nieuwe-stijl/')).flatMap(([, p]) => parseAnnotation(p));
  assert.equal(maps.length, 999);
  assert.equal(new Set(maps.map(m => m.id)).size, 999);
  assert.equal(counts.size, 16);
  const manifests = [...docs.values()].filter((d): d is Manifest => d.type === 'Manifest');
  const canvases = manifests.flatMap(m => m.items);
  assert.equal(canvases.filter(c => c.navDate).length, 998);
  for (const manifest of manifests) {
    const geo = manifest.items.filter(c => 'navPlace' in c);
    if (!geo.length) continue;
    assert.equal(manifest['@context']![0], navPlaceContext);
    for (const canvas of geo) {
      const nav = (canvas as any).navPlace;
      assert.equal(nav.type, 'FeatureCollection');
      assert.equal(nav.features.length, 1);
      const ring = nav.features[0].geometry.coordinates[0];
      assert.equal(nav.features[0].geometry.type, 'Polygon');
      assert.deepEqual(ring[0], ring.at(-1));
      assert.ok(signedArea(ring) > 0);
      assert.ok(ring.every(([x, y]: number[]) => Number.isFinite(x) && Number.isFinite(y) && x > 3 && x < 8 && y > 50 && y < 54));
    }
  }
  assert.equal(canvases.filter(c => 'navPlace' in c).length, 999);
  assert.ok(![...files.keys()].some(path => path.startsWith('annotations/first-edition/')));
  for (const [path, document] of docs) {
    if (!path.startsWith('manifests/first-edition/') || document.type !== 'Manifest') continue;
    assert.ok(!counts.has(document.id));
    assert.ok(document.items.every(canvas => !('navPlace' in canvas)));
    assert.ok(!document.seeAlso?.some(link => link.id?.includes('/annotations/first-edition/')));
  }
  const indices = docs.get('manifests/nieuwe-stijl/series-01.json') as Manifest;
  assert.ok(indices.items.every(c => !('navPlace' in c)));
  assert.ok(!files.has('annotations/nieuwe-stijl/series-01.json'));
  const undated = docs.get('manifests/nieuwe-stijl/series-17.json') as Manifest;
  assert.ok(undated.items.every(c => !('navDate' in c)));
  const report = files.get('georeferencing/navigation-report.json') as {dateIssues: unknown[]};
  assert.equal(report.dateIssues.length, 8);
});

test('publication supports another base URL without rewriting archive image URLs or leaving broken research links', async () => {
  const base = 'https://example.org/release/';
  const docs = await documents(base);
  const {files} = await publishGeoreferencing(docs, base);
  for (const [path, page] of files) {
    if (!path.startsWith('annotations/')) continue;
    const p = page as any;
    assert.equal(p.id, base + path);
    for (const a of p.items) {
      const map = parseAnnotation(a)[0];
      assert.ok(map.resource.id.startsWith('https://service.archief.nl/'));
      for (const link of a.seeAlso ?? []) if (link.id.startsWith(base)) assert.ok(files.has(link.id.slice(base.length)));
      assert.doesNotMatch(JSON.stringify(a), /georeferencing\/nieuwe-stijl\/maps\/|urn:river-maps:review/);
    }
  }
});

test('a missing annotated canvas prevents publication', async () => {
  const docs = await documents();
  (docs.get('manifests/nieuwe-stijl/series-02.json') as Manifest).items = [];
  await assert.rejects(publishGeoreferencing(docs), /no matching canvas/);
});


test('unreviewed annotation files in other editions cannot enter the publication', async () => {
  const repo = await mkdtemp(join(tmpdir(), 'river-maps-publication-test-'));
  try {
    await mkdir(join(repo, 'data/iiif-annotations/first-edition'), {recursive: true});
    for (const path of ['data/iiif-annotations/nieuwe-stijl', 'data/nationaal-archief']) {
      await symlink(fileURLToPath(new URL('../' + path, import.meta.url)), join(repo, path), 'dir');
    }
    await writeFile(join(repo, 'data/iiif-annotations/first-edition/series-1.json'), 'unreviewed, invalid annotation data');
    const {files, counts} = await publishGeoreferencing(await documents(), defaultBaseUrl, repo);
    assert.equal(counts.size, 16);
    assert.ok(!files.has('annotations/first-edition/series-1.json'));
  } finally {
    await rm(repo, {recursive: true, force: true});
  }
});
