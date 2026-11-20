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
  annotationUrl?: string;
  mapCount?: number;
}
export interface BrowseGroup {
  id: string;
  path: string;
  label: string;
  manifests: BrowseManifest[];
}

// URLSearchParams preserves URLs containing their own query strings or fragments.
export function toolLinks(resourceId: string, resourceType: 'Manifest' | 'Collection' = 'Manifest') {
  const allmaps = new URL('https://editor.allmaps.org/images');
  allmaps.searchParams.set('url', resourceId);
  allmaps.searchParams.set('lang', 'en');
  const editor = new URL('https://manifest-editor.digirati.services/share');
  editor.searchParams.set('iiif-content', resourceId);
  editor.searchParams.set('action', 'import');
  if (resourceType === 'Collection') editor.searchParams.set('resource-type', 'Collection');
  const theseus = new URL('https://theseusviewer.org/');
  theseus.searchParams.set('iiif-content', resourceId);
  return { allmaps: allmaps.href, editor: editor.href, theseus: theseus.href };
}

export function createBrowseModel(documents: Documents, counts: ReadonlyMap<string, number> = new Map()): BrowseGroup[] {
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
        group.manifests.push({
          id: manifest.id,
          path: entry.path,
          label: getValue(manifest.label),
          mapCount: counts.get(manifest.id),
          annotationUrl: manifest.seeAlso?.find(s => 'profile' in s && s.profile === 'http://iiif.io/api/extension/georef/1/context.json')?.id,
        });
      }
    }
    if (group.manifests.length) groups.push(group);
  }
  visit(root, []);
  return groups;
}

function ResourceLinks({ resource, type, jsonLabel }: {
  resource: BrowseManifest;
  type: 'Manifest' | 'Collection';
  jsonLabel: string;
}) {
  const links = toolLinks(resource.id, type);
  return html`<nav class="resource-links" aria-label=${`Open ${resource.label}`}>
      <a href=${links.allmaps}>Allmaps Editor</a>
      <a href=${links.editor}>IIIF Manifest Editor</a>
      <a href=${links.theseus}>Theseus Viewer</a>
      <a href=${resource.path}>${jsonLabel}</a>
    </nav>`;
}

export function allmapsViewerLink(annotationUrl: string): string {
  const url = new URL('https://viewer.allmaps.org/');
  url.searchParams.set('url', annotationUrl);
  return url.href;
}

function ManifestRow({ manifest }: { manifest: BrowseManifest }) {
  return html`<li class="manifest-row">
    <h3>${manifest.label}</h3>
    <${ResourceLinks} resource=${manifest} type="Manifest" jsonLabel="Manifest JSON" />
    ${manifest.annotationUrl && html`<nav class="resource-links" aria-label="Georeferenced maps"><a href=${allmapsViewerLink(manifest.annotationUrl)}>Open ${manifest.mapCount ?? ""} maps in Allmaps</a><a href=${manifest.annotationUrl}>Annotation JSON</a></nav>`}
  </li>`;
}

export function renderBrowsePage(documents: Documents, counts: ReadonlyMap<string, number> = new Map()): string {
  const groups = createBrowseModel(documents, counts);
  const root = documents.get('collection.json')!;
  const collection = { id: root.id, path: 'collection.json', label: getValue(root.label) };
  return '<!doctype html>\n' + render(html`<html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>River maps</title>
      <meta name="description" content="Historical river maps from Utrecht University Library and Nationaal Archief, with links to IIIF viewers and editors." />
      <link rel="stylesheet" href="assets/site.css" />
    </head>
    <body>
      <main>
        <header class="page-heading">
          <h1>River maps</h1>
          <p>Explore 999 reviewed Nieuwe Stijl maps in Allmaps, grouped by series.</p>
          <${ResourceLinks} resource=${collection} type="Collection" jsonLabel="Collection JSON" />
        </header>
        ${groups.map((group, index) => html`<section class="edition" aria-labelledby=${`edition-${index}`}>
          <header class="edition-heading">
            <h2 id=${`edition-${index}`}>${group.label}</h2>
            <${ResourceLinks} resource=${group} type="Collection" jsonLabel="Edition JSON" />
          </header>
          <ul class="manifest-list">${group.manifests.map(manifest => html`<${ManifestRow} key=${manifest.id} manifest=${manifest} />`)}</ul>
        </section>`)}
      </main>
    </body>
  </html>`) + '\n';
}
