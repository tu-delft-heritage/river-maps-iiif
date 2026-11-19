import { getValue } from '@iiif/helpers/i18n';
import type { Manifest } from '@iiif/presentation-3';
import { html } from 'htm/preact';
import { render } from 'preact-render-to-string';
import type { LinkedCollection } from './collection.ts';

type Documents = ReadonlyMap<string, LinkedCollection | Manifest>;
export interface BrowseManifest {
  id: string;
  path: string;
  label: string;
  published: string;
  canvases: number;
}
export interface BrowseGroup {
  id: string;
  path: string;
  label: string;
  manifests: BrowseManifest[];
}

// URLSearchParams preserves URLs containing their own query strings or fragments.
export function toolLinks(manifestId: string) {
  const allmaps = new URL('https://editor.allmaps.org/images');
  allmaps.searchParams.set('url', manifestId);
  allmaps.searchParams.set('lang', 'en');
  const editor = new URL('https://manifest-editor.digirati.services/share');
  editor.searchParams.set('iiif-content', manifestId);
  editor.searchParams.set('action', 'import');
  const theseus = new URL('https://theseusviewer.org/');
  theseus.searchParams.set('iiif-content', manifestId);
  return { allmaps: allmaps.href, editor: editor.href, theseus: theseus.href };
}

export function createBrowseModel(documents: Documents): BrowseGroup[] {
  const root = documents.get('collection.json');
  if (!root || root.type !== 'Collection') throw new Error('Missing root collection for the browse page.');
  const byId = new Map([...documents].map(([path, document]) => [document.id, { path, document }]));
  const groups: BrowseGroup[] = [];
  const visited = new Set<string>();
  function visit(collection: LinkedCollection, parentLabels: string[]) {
    if (visited.has(collection.id)) return;
    visited.add(collection.id);
    const labels = collection === root ? parentLabels : [...parentLabels, getValue(collection.label)];
    const group: BrowseGroup = {
      id: collection.id,
      path: byId.get(collection.id)!.path,
      label: labels.join(' / ') || getValue(collection.label),
      manifests: [],
    };
    for (const reference of collection.items) {
      const entry = byId.get(reference.id);
      if (!entry) throw new Error(`Browse page references a missing document: ${reference.id}`);
      if (entry.document.type === 'Collection') {
        visit(entry.document, labels);
      } else {
        const manifest = entry.document;
        const published = manifest.metadata?.find(item => getValue(item.label).toLowerCase() === 'published');
        group.manifests.push({
          id: manifest.id,
          path: entry.path,
          label: getValue(manifest.label),
          published: published ? getValue(published.value) : '',
          canvases: manifest.items.length,
        });
      }
    }
    if (group.manifests.length) groups.push(group);
  }
  visit(root, []);
  return groups;
}

function RiverMark() {
  return html`<svg viewBox="0 0 36 36" fill="none" aria-hidden="true">
    <path d="M9 3C27 8 2 16 20 22S15 31 23 34M18 2C36 7 11 15 29 21S24 30 32 33M0 4C18 9-7 17 11 23S6 32 14 35" stroke="currentColor" stroke-width="2" />
  </svg>`;
}

function ManifestRow({ manifest }: { manifest: BrowseManifest }) {
  const links = toolLinks(manifest.id);
  const split = manifest.label.indexOf(' — ');
  const series = split >= 0 ? manifest.label.slice(0, split) : 'Manifest';
  const title = split >= 0 ? manifest.label.slice(split + 3) : manifest.label;
  return html`<li class="manifest-row">
    <div class="manifest-description">
      <div class="manifest-meta"><span class="series">${series}</span>
        ${manifest.published && html`<span>${manifest.published}</span>`}
        <span>${manifest.canvases} scanned pages</span>
      </div>
      <h3>${title}</h3>
    </div>
    <nav class="manifest-tools" aria-label=${`Open ${manifest.label}`}>
      <a class="tool tool-view" href=${links.theseus}>Theseus Viewer</a>
      <a class="tool" href=${links.allmaps}>Allmaps Editor</a>
      <a class="tool" href=${links.editor}>IIIF Manifest Editor</a>
      <a class="json-link" href=${manifest.path}>Manifest JSON</a>
    </nav>
  </li>`;
}

export function renderBrowsePage(documents: Documents): string {
  const groups = createBrowseModel(documents);
  const manifests = new Map(groups.flatMap(group => group.manifests.map(manifest => [manifest.id, manifest] as const)));
  const canvasCount = [...manifests.values()].reduce((sum, manifest) => sum + manifest.canvases, 0);
  const root = documents.get('collection.json')!;
  const collectionViewer = toolLinks(root.id).theseus;
  return '<!doctype html>\n' + render(html`<html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>River maps · IIIF collection</title>
      <meta name="description" content="Explore historical river maps from Utrecht University Library. Open each series in Theseus Viewer, Allmaps Editor, or IIIF Manifest Editor." />
      <link rel="stylesheet" href="assets/site.css" />
    </head>
    <body>
      <a class="skip-link" href="#manifests">Skip to manifests</a>
      <header class="masthead"><div class="wrap masthead-inner">
        <a class="brand" href="./"><${RiverMark} /><span>River maps<span class="brand-subtitle">IIIF collection</span></span></a>
        <a class="header-link" href="https://github.com/tu-delft-heritage/river-maps-iiif">View on GitHub</a>
      </div></header>
      <main class="wrap">
        <section class="intro" aria-labelledby="page-title">
          <div><p class="eyebrow">Utrecht University Library · Digitised collections</p>
            <h1 id="page-title">Follow the rivers.<br /><em>Explore the maps.</em></h1>
            <p class="lede">Historic maps of the Dutch rivers, organised by edition and series.
              View the scans, georeference a map, or work with its IIIF manifest.</p>
            <div class="collection-actions"><a class="button" href=${collectionViewer}>Explore the collection</a>
              <a class="text-link" href="collection.json">Collection JSON</a></div>
          </div>
          <dl class="collection-stats" aria-label="Collection overview">
            <div><dt>Editions</dt><dd>${groups.length}</dd></div>
            <div><dt>Manifests</dt><dd>${manifests.size}</dd></div>
            <div><dt>Scanned pages</dt><dd>${canvasCount}</dd></div>
          </dl>
        </section>
        <div class="catalog-heading" id="manifests"><h2>Browse the manifests</h2><span>Choose a series to get started</span></div>
        ${groups.map((group, index) => html`<section class="edition" aria-labelledby=${`edition-${index}`}>
          <header class="edition-heading"><div><h2 id=${`edition-${index}`}>${group.label}</h2>
            <span>${group.manifests.length} ${group.manifests.length === 1 ? 'manifest' : 'manifests'}</span></div>
            <a href=${group.path}>Edition JSON</a></header>
          <ul class="manifest-list">${group.manifests.map(manifest => html`<${ManifestRow} key=${manifest.id} manifest=${manifest} />`)}</ul>
        </section>`)}
        <aside class="tool-guide" aria-labelledby="tools-heading">
          <h2 id="tools-heading">A tool for every next step</h2>
          <div class="guide-grid"><div><h3>Theseus Viewer</h3><p>Browse the scanned pages and zoom in on the details.</p></div>
            <div><h3>Allmaps Editor</h3><p>Place historic maps in the world by georeferencing them.</p></div>
            <div><h3>IIIF Manifest Editor</h3><p>Import a copy to edit its metadata, structure, and annotations.</p></div></div>
        </aside>
      </main>
      <footer class="wrap"><span>Scans from <a href="https://www.uu.nl/en/university-library">Utrecht University Library</a></span>
        <a href="collection.json">IIIF Presentation 3</a></footer>
    </body>
  </html>`) + '\n';
}
