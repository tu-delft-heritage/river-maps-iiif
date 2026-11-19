import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { Vault } from '@iiif/helpers/vault';
import type { Manifest } from '@iiif/presentation-3';
import { defaultBaseUrl, editions } from './catalog.ts';
import { generateCollection, normalizeBaseUrl, sourcePath } from './collection.ts';

const sources = new Map<string, Manifest>();
for (const edition of editions) {
  for (const series of edition.series) {
    const path = sourcePath(edition, series);
    sources.set(path, JSON.parse(await readFile(new URL(`../${path}`, import.meta.url), 'utf8')));
  }
}

test('the real catalog has six distinct library records with the correct river titles', () => {
  const series = editions[0]!.series;
  assert.ok(series.length >= 6);
  const expected = [
    ['462061', 'Boven Rijn'], ['462106', 'Neder-Rijn'], ['462062', 'Westervoort'],
    ['462072', 'Visé'], ['462108', 'Bergsche Veld'], ['462063', 'Gouda'],
  ];
  for (const [index, [id, title]] of expected.entries()) {
    const entry = series[index]!;
    const source = sources.get(sourcePath(editions[0]!, entry))!;
    assert.ok(source.id.endsWith(id!));
    assert.ok(JSON.stringify(source.metadata).includes(title!));
  }
  assert.equal(series.slice(0, 6).reduce((count, entry) => count + sources.get(sourcePath(editions[0]!, entry))!.items.length, 0), 144);
});

test('all collection and parent links resolve locally, including a second edition and custom base path', async () => {
  const first = editions[0]!;
  const second = { ...first, slug: 'second-edition', label: 'Second edition' };
  const bothSources = new Map(sources);
  for (const series of second.series) {
    bothSources.set(sourcePath(second, series), sources.get(sourcePath(first, series))!);
  }
  const base = 'https://example.org/maps/nested/';
  const documents = generateCollection([first, second], bothSources, base.slice(0, -1));
  const byId = new Map([...documents.values()].map(document => [document.id, document]));
  const root = documents.get('collection.json')!;
  assert.equal(root.items?.length, 2);
  assert.equal(documents.size, 1 + 2 * (1 + first.series.length));
  const vault = new Vault({ customFetcher: async (url) => { throw new Error(`Unexpected fetch: ${url}`); } });
  for (const [path, document] of documents) {
    assert.equal(document.id, `${base}${path}`);
    if (document.type === 'Collection') {
      for (const reference of document.items ?? []) {
        const child = byId.get(reference.id);
        assert.ok(child, `Missing document for ${reference.id}`);
        assert.equal(child.type, reference.type);
        assert.deepEqual(child.label, reference.label);
      }
    }
    for (const parent of document.partOf ?? []) {
      assert.ok(parent.id);
      if (parent.id.startsWith(base)) assert.ok(byId.has(parent.id));
    }
    const loaded = await vault.load<{ id: string; type: string }>(document.id, document);
    assert.equal(loaded?.id, document.id);
    assert.equal(loaded?.type, document.type);
  }
});

test('publishing preserves canvases, annotations, image services, metadata and attribution without mutating sources', () => {
  const before = structuredClone(sources);
  const documents = generateCollection(editions, sources, defaultBaseUrl);
  for (const edition of editions) {
    for (const series of edition.series) {
      const source = sources.get(sourcePath(edition, series))!;
      const published = documents.get(`manifests/${edition.slug}/${series.slug}.json`)! as Manifest;
      // Only these five properties are intentionally changed or extended.
      const { id: _sourceId, label: sourceLabel, metadata: sourceMetadata, partOf: _sourceParents, seeAlso: _sourceLinks, ...original } = source;
      const { id: _id, label: _label, metadata, partOf: _parents, seeAlso, ...preserved } = published;
      assert.deepEqual(preserved, original);
      assert.deepEqual(metadata?.slice(0, -1), sourceMetadata ?? []);
      assert.deepEqual(metadata?.at(-1)?.value, sourceLabel);
      assert.equal(seeAlso?.at(-1)?.id, series.source);
    }
  }
  assert.deepEqual(sources, before);
  assert.deepEqual(generateCollection(editions, sources, defaultBaseUrl), documents);
});

test('invalid inputs fail instead of publishing missing or mislabeled manifests', () => {
  assert.throws(() => generateCollection(editions, new Map(), defaultBaseUrl), /Not a manifest/);
  const wrongSources = new Map(sources);
  wrongSources.set(sourcePath(editions[0]!, editions[0]!.series[1]!), sources.values().next().value!);
  assert.throws(() => generateCollection(editions, wrongSources, defaultBaseUrl), /Expected a Presentation 3 manifest/);
  const duplicate = structuredClone(editions);
  duplicate[0]!.series[1]!.source = duplicate[0]!.series[0]!.source;
  assert.throws(() => generateCollection(duplicate, sources, defaultBaseUrl), /duplicate\/invalid source/);
  const traversal = structuredClone(editions);
  traversal[0]!.slug = '../outside';
  assert.throws(() => generateCollection(traversal, sources, defaultBaseUrl), /Invalid or duplicate edition slug/);
  for (const url of ['file:///tmp/', 'https://example.org/?query=1', 'https://example.org/#fragment']) {
    assert.throws(() => normalizeBaseUrl(url), /IIIF_BASE_URL/);
  }
});
