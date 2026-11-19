import assert from 'node:assert/strict';
import test from 'node:test';
import type { Manifest } from '@iiif/presentation-3';
import type { LinkedCollection } from './collection.ts';
import { createBrowseModel, renderBrowsePage, toolLinks } from './site.ts';

test('tool links pass the complete manifest URL to the supported import routes', () => {
  const manifest = 'https://example.org/nested/maps/manifest.json?value=a&other=b#canvas';
  const links = toolLinks(manifest);
  const allmaps = new URL(links.allmaps);
  assert.equal(allmaps.origin + allmaps.pathname, 'https://editor.allmaps.org/images');
  assert.equal(allmaps.searchParams.get('url'), manifest);
  const editor = new URL(links.editor);
  assert.equal(editor.origin + editor.pathname, 'https://manifest-editor.digirati.services/share');
  assert.equal(editor.searchParams.get('iiif-content'), manifest);
  assert.equal(editor.searchParams.get('action'), 'import');
  assert.equal(new URL(links.theseus).searchParams.get('iiif-content'), manifest);
});

test('the page follows new edition collections and safely renders their labels without browser JavaScript', () => {
  const base = 'https://example.org/custom/path/';
  const root: LinkedCollection = { id: `${base}collection.json`, type: 'Collection', label: { en: ['River maps'] }, items: [] };
  const documents = new Map<string, LinkedCollection | Manifest>([['collection.json', root]]);
  for (const edition of ['first', 'second']) {
    const path = `collections/${edition}.json`;
    const collection: LinkedCollection = {
      id: `${base}${path}`, type: 'Collection', label: { en: [edition] }, items: [],
    };
    root.items.push({ id: collection.id, type: 'Collection', label: collection.label });
    documents.set(path, collection);
    const manifest: Manifest = {
      id: `${base}manifests/${edition}.json`, type: 'Manifest', label: { none: [`Series — ${edition} & <script>unsafe</script>`] }, items: [],
    };
    collection.items.push({ id: manifest.id, type: 'Manifest', label: manifest.label });
    documents.set(`manifests/${edition}.json`, manifest);
  }
  const groups = createBrowseModel(documents);
  assert.deepEqual(groups.map(group => group.label), ['first', 'second']);
  assert.equal(groups.flatMap(group => group.manifests).length, 2);
  const page = renderBrowsePage(documents);
  assert.equal((page.match(/class="manifest-row"/g) ?? []).length, 2);
  assert.ok(page.includes('href="manifests/second.json"'));
  assert.ok(page.includes(encodeURIComponent(`${base}manifests/second.json`)));
  assert.ok(page.includes('second &amp;'));
  assert.doesNotMatch(page, /<script\b/);
  documents.delete('manifests/second.json');
  assert.throws(() => renderBrowsePage(documents), /missing document/);
});
