import { getValue } from '@iiif/helpers/i18n';
import type { Collection, Manifest } from '@iiif/presentation-3';
import type { Edition, Series } from './catalog.ts';

// The published collection links to separate documents, rather than embedding full resources.
export type ResourceReference = Pick<Manifest, 'id' | 'label'> & { type: 'Collection' | 'Manifest' };
export type LinkedCollection = Omit<Collection, 'items'> & { items: ResourceReference[] };

export const context = 'http://iiif.io/api/presentation/3/context.json';
export const sourcePath = (edition: Edition, series: Series) =>
  `data/iiif-manifests/${edition.slug}/${series.slug}.json`;

export function normalizeBaseUrl(value: string): string {
  const url = new URL(value);
  if (!['http:', 'https:'].includes(url.protocol) || url.search || url.hash || url.username || url.password) {
    throw new Error('IIIF_BASE_URL must be an HTTP(S) URL without credentials, a query, or a fragment.');
  }
  url.pathname = `${url.pathname.replace(/\/+$/, '')}/`;
  return url.href;
}

export function validateCatalog(editions: Edition[]): void {
  if (!editions.length) throw new Error('The catalog must contain at least one edition.');
  const editionSlugs = new Set<string>();
  for (const edition of editions) {
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(edition.slug) || editionSlugs.has(edition.slug)) {
      throw new Error(`Invalid or duplicate edition slug: ${edition.slug}`);
    }
    editionSlugs.add(edition.slug);
    if (!edition.label.trim() || !edition.series.length) throw new Error(`Empty edition: ${edition.slug}`);
    const seriesSlugs = new Set<string>();
    const sources = new Set<string>();
    for (const series of edition.series) {
      if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(series.slug) || seriesSlugs.has(series.slug)) {
        throw new Error(`Invalid or duplicate series slug: ${edition.slug}/${series.slug}`);
      }
      if (!series.label.trim() || !/^https?:\/\//.test(series.source) || sources.has(series.source)) {
        throw new Error(`Invalid label or duplicate/invalid source: ${edition.slug}/${series.slug}`);
      }
      new URL(series.source);
      seriesSlugs.add(series.slug);
      sources.add(series.source);
    }
  }
}

// These checks catch failed downloads and wrong records; they are not a full IIIF schema validator.
export function assertSourceManifest(value: unknown, source: string): asserts value is Manifest {
  if (!value || typeof value !== 'object') throw new Error(`Not a manifest: ${source}`);
  const manifest = value as Manifest;
  const contexts = Array.isArray(manifest['@context']) ? manifest['@context'] : [manifest['@context']];
  if (manifest.type !== 'Manifest' || manifest.id !== source || !contexts.includes(context)) {
    throw new Error(`Expected a Presentation 3 manifest with id ${source}`);
  }
  if (!manifest.label || !getValue(manifest.label).trim() || !manifest.items?.length) {
    throw new Error(`Manifest has no label or canvases: ${source}`);
  }
  const ids = new Set<string>();
  for (const canvas of manifest.items) {
    if (canvas.type !== 'Canvas' || !canvas.id || ids.has(canvas.id) || !canvas.items?.length) {
      throw new Error(`Invalid, empty, or duplicate canvas in ${source}`);
    }
    ids.add(canvas.id);
  }
}

export function generateCollection(
  editions: Edition[],
  sources: ReadonlyMap<string, unknown>,
  baseUrl: string,
): Map<string, LinkedCollection | Manifest> {
  validateCatalog(editions);
  const base = normalizeBaseUrl(baseUrl);
  const url = (path: string) => new URL(path, base).href;
  const documents = new Map<string, LinkedCollection | Manifest>();
  const root: LinkedCollection = {
    '@context': context,
    id: url('collection.json'),
    type: 'Collection',
    label: { en: ['River maps'], nl: ['Rivierkaarten'] },
    summary: { en: ['Historical river maps, grouped by edition, with scans from Utrecht University Library.'] },
    items: [],
  };
  documents.set('collection.json', root);

  for (const edition of editions) {
    const editionPath = `collections/${edition.slug}.json`;
    const collection: LinkedCollection = {
      '@context': context,
      id: url(editionPath),
      type: 'Collection',
      label: { en: [edition.label] },
      partOf: [{ id: root.id, type: 'Collection' }],
      items: [],
    };
    root.items!.push({ id: collection.id, type: 'Collection', label: collection.label });
    documents.set(editionPath, collection);

    for (const series of edition.series) {
      const source = sources.get(sourcePath(edition, series));
      assertSourceManifest(source, series.source);
      const manifestPath = `manifests/${edition.slug}/${series.slug}.json`;
      // Keep embedded canvas/annotation IDs and image services stable for georeferencing.
      const manifest: Manifest = {
        ...structuredClone(source),
        id: url(manifestPath),
        label: { none: [series.label] },
        metadata: [
          ...(source.metadata ?? []),
          { label: { en: ['Original library label'] }, value: source.label },
        ],
        partOf: [
          { id: collection.id, type: 'Collection' },
          ...(source.partOf ?? []),
        ],
        seeAlso: [
          ...(source.seeAlso ?? []),
          {
            id: series.source,
            type: 'Dataset',
            format: 'application/ld+json',
          },
        ],
      };
      collection.items!.push({ id: manifest.id, type: 'Manifest', label: manifest.label });
      documents.set(manifestPath, manifest);
    }
  }
  return documents;
}
