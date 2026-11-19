import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import test from 'node:test';
import { Vault } from '@iiif/helpers/vault';
import type { Canvas, Manifest, Range } from '@iiif/presentation-3';
import { defaultBaseUrl } from './catalog.ts';
import {
  archiveEadPath, archiveSnapshotPath, components, generateArchiveCollection,
  validateArchiveSnapshot, type ArchiveSnapshot,
} from './nationaal-archief.ts';

const snapshot: ArchiveSnapshot = JSON.parse(await readFile(new URL(`../${archiveSnapshotPath}`, import.meta.url), 'utf8'));
const ead = await readFile(new URL(`../${archiveEadPath}`, import.meta.url));
const documents = generateArchiveCollection(snapshot, defaultBaseUrl);
const manifests = [...documents.values()].filter((d): d is Manifest => d.type === 'Manifest');
const escape = (value: string) => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');

test('the saved inventory produces 17 series and exactly 1,009 digitized canvases', () => {
  assert.equal(createHash('sha256').update(ead).digest('hex'), snapshot.eadSha256);
  assert.equal(manifests.length, 17);
  assert.deepEqual(manifests.map(m => m.items.length), [10, 76, 83, 145, 73, 38, 55, 109, 44, 44, 80, 16, 12, 23, 69, 129, 3]);
  const canvases = manifests.flatMap(m => m.items);
  assert.equal(canvases.length, 1009);
  assert.equal(new Set(canvases.map(c => c.id)).size, 1009);
  const records = [...components(snapshot.edition)].filter(n => n.metsUrl);
  assert.equal(records.length, 1009);
  assert.equal(Object.keys(snapshot.objects).length, 1009);
  assert.equal([...components(snapshot.edition)].filter(n => !n.metsUrl && !n.children.length).length, 0);
});

test('every source record retains descriptive fields, image identity, dimensions, capabilities and rights', () => {
  const canvases = manifests.flatMap(m => m.items);
  for (const record of components(snapshot.edition)) {
    if (!record.metsUrl) continue;
    const object = snapshot.objects[record.uuid]!;
    for (const image of object.images) {
      const canvas = canvases.find(c => c.id.endsWith(`#canvas-${record.uuid}-${image.id}`))!;
      assert.ok(canvas, `Missing ${record.inventoryNumber}`);
      assert.equal(canvas.width, image.info.width);
      assert.equal(canvas.height, image.info.height);
      for (const field of record.metadata) {
        assert.ok(canvas.metadata?.some(m => m.label.nl?.[0] === field.label && m.value.nl?.[0] === escape(field.value)),
          `Lost metadata: ${record.inventoryNumber} / ${field.label}`);
      }
      const page = canvas.items![0]!;
      const annotation = page.items![0]!;
      assert.equal(annotation.motivation, 'painting');
      assert.equal(annotation.target, canvas.id);
      assert.ok(annotation.body && !Array.isArray(annotation.body));
      const body = annotation.body as { id: string; width: number; height: number; service: unknown[] };
      assert.equal(body.id, image.image.url);
      assert.deepEqual(body.service, [image.info]);
      assert.equal(body.width, canvas.width);
      assert.equal(body.height, canvas.height);
      assert.ok(canvas.seeAlso?.some(source => source.id === record.metsUrl));
      assert.equal(canvas.homepage?.[0]?.id, record.homepage);
      assert.equal(canvas.rendering?.[0]?.id, image.image.url);
      if (object.rights.length && object.rights.every(r => r.category === 'PUBLIC DOMAIN')) {
        assert.equal(canvas.rights, 'http://creativecommons.org/publicdomain/mark/1.0/');
      }
    }
  }
});

test('ranges preserve source subgroup hierarchy and inventory order without dangling or duplicate canvas links', () => {
  function canvasIds(range: Range): string[] {
    return (range.items ?? []).flatMap(item => {
      assert.notEqual(typeof item, 'string');
      if (typeof item === 'string') return [item];
      return item.type === 'Range' ? canvasIds(item as Range) : [(item as Canvas).id];
    });
  }
  for (const manifest of manifests) {
    assert.equal(manifest.structures?.length, 1);
    assert.deepEqual(canvasIds(manifest.structures![0]!), manifest.items.map(c => c.id));
  }
  assert.equal(manifests[0]!.structures![0]!.items!.filter(i => typeof i !== 'string' && i.type === 'Range').length, 3);
  assert.equal(manifests[4]!.structures![0]!.items!.filter(i => typeof i !== 'string' && i.type === 'Range').length, 2);
});

test('new documents load through IIIF Vault with no network access and resolve their collection links', async () => {
  const vault = new Vault({ customFetcher: async (url) => { throw new Error(`Unexpected fetch: ${url}`); } });
  const byId = new Map([...documents.values()].map(d => [d.id, d]));
  for (const document of documents.values()) {
    const loaded = await vault.load<{ id: string; type: string }>(document.id, document);
    assert.equal(loaded?.type, document.type);
    if (document.type === 'Collection') {
      for (const ref of document.items) assert.ok(byId.has(ref.id));
    } else {
      for (const parent of document.partOf ?? []) assert.ok(parent.id && byId.has(parent.id));
    }
  }
});

test('custom hosts rebase new IDs and cached EAD links while keeping archive image URLs and inputs unchanged', () => {
  const before = structuredClone(snapshot);
  const custom = generateArchiveCollection(snapshot, 'https://example.org/maps');
  for (const [path, doc] of custom) {
    assert.equal(doc.id, `https://example.org/maps/${path}`);
    assert.ok(doc.seeAlso?.some(source => source.id === 'https://example.org/maps/sources/nationaal-archief/2.16.5150.xml'));
    if (doc.type === 'Manifest') {
      assert.ok(doc.items.every(c => c.id.startsWith(`${doc.id}#canvas-`)));
      assert.ok(doc.items.every(c => c.rendering?.[0]?.id?.startsWith('https://service.archief.nl/')));
    }
  }
  assert.deepEqual(snapshot, before);
  const reordered = structuredClone(snapshot);
  reordered.edition.children[1]!.children.reverse();
  const regenerated = generateArchiveCollection(reordered, defaultBaseUrl);
  const original = documents.get('manifests/nieuwe-stijl/series-02.json') as Manifest;
  const changed = regenerated.get('manifests/nieuwe-stijl/series-02.json') as Manifest;
  assert.deepEqual(changed.items.map(c => c.id).sort(), original.items.map(c => c.id).sort());
});

test('incomplete, undigitized and malformed source objects fail before publishing', () => {
  const missing = structuredClone(snapshot);
  delete missing.objects[Object.keys(missing.objects)[0]!];
  assert.throws(() => validateArchiveSnapshot(missing), /Missing digital object/);
  const badSize = structuredClone(snapshot);
  Object.values(badSize.objects)[0]!.images[0]!.info.width = 0;
  assert.throws(() => validateArchiveSnapshot(badSize), /Invalid or duplicate digital image/);
  const undigitized = structuredClone(snapshot);
  undigitized.edition.children[1]!.children.push({
    uuid: 'undigitized', title: 'No scan', level: 'file', code: '', inventoryNumber: '', metadata: [], children: [],
  });
  assert.throws(() => validateArchiveSnapshot(undigitized), /Undigitized record/);
});
