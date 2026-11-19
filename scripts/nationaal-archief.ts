import type { Canvas, ImageService3, Manifest, MetadataItem, Range, ResourceProvider } from '@iiif/presentation-3';
import { context, normalizeBaseUrl, type LinkedCollection } from './collection.ts';

export const archiveSnapshotPath = 'data/nationaal-archief/nieuwe-stijl.json';
export const archiveEadPath = 'data/nationaal-archief/2.16.5150.xml';
export const publishedEadPath = 'sources/nationaal-archief/2.16.5150.xml';
export const archiveEditionSlug = 'nieuwe-stijl';

interface Field { label: string; value: string }
export interface ArchiveComponent {
  uuid: string;
  level: string;
  code: string;
  inventoryNumber: string;
  title: string;
  metadata: Field[];
  homepage?: string;
  metsUrl?: string;
  children: ArchiveComponent[];
}
interface FileReference { url: string; format: string; size: string }
export interface ArchiveImage {
  id: string;
  order: number;
  label: string;
  image: FileReference;
  thumbnail?: FileReference;
  infoUrl: string;
  info: ImageService3 & { width: number; height: number };
}
export interface ArchiveObject {
  metsUrl: string;
  metsXml: string;
  rights: { category: string; metadata: Field[] }[];
  images: ArchiveImage[];
}
export interface ArchiveSnapshot {
  schemaVersion: number;
  source: string;
  retrievedAt: string;
  eadSha256: string;
  eadVersion: string;
  archive: { title: string; homepage: string; metadata: Field[] };
  edition: ArchiveComponent;
  objects: Record<string, ArchiveObject>;
}

const escape = (value: string) => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
const fields = (values: Field[]): MetadataItem[] => values.map(({ label, value }) => ({
  label: { nl: [label] }, value: { nl: [escape(value)] },
}));
const provider: ResourceProvider[] = [{
  id: 'https://www.nationaalarchief.nl/', type: 'Agent', label: { nl: ['Nationaal Archief'] },
  homepage: [{ id: 'https://www.nationaalarchief.nl/', type: 'Text', format: 'text/html' }],
}];
const webPage = (id: string) => ({ id, type: 'Text' as const, format: 'text/html', label: { nl: ['Archiefbeschrijving'] } });
const dataset = (id: string, label: string, format = 'application/xml') => ({
  id, type: 'Dataset' as const, format, label: { nl: [label] },
});
const download = (id: string) => ({ id, type: 'Image' as const, format: 'image/jpeg', label: { en: ['Download full-resolution scan (JPEG)'] } });
const attribution = (number?: string) => ({
  label: { en: ['Attribution'], nl: ['Bronvermelding'] },
  value: { nl: [`Nationaal Archief, Den Haag, Meetkundige Dienst: Rivierkaarten, toegang 2.16.5150${number ? `, inventarisnummer ${number}` : ''}.`] },
});
export function* components(node: ArchiveComponent): Generator<ArchiveComponent> {
  yield node;
  for (const child of node.children) yield* components(child);
}

/** Reject incomplete snapshots, so a failed refresh cannot quietly remove maps. */
export function validateArchiveSnapshot(snapshot: ArchiveSnapshot): void {
  if (snapshot.schemaVersion !== 1 || snapshot.edition?.code !== 'D' || !snapshot.edition.children.length) {
    throw new Error('Invalid Nationaal Archief snapshot');
  }
  const seen = new Set<string>();
  const seenImages = new Set<string>();
  for (const node of components(snapshot.edition)) {
    if (!node.uuid || !node.title || seen.has(node.uuid)) throw new Error('Missing or duplicate EAD component');
    seen.add(node.uuid);
    if (!node.metsUrl) {
      if (!node.children.length) throw new Error(`Undigitized record in snapshot: ${node.uuid}`);
      continue;
    }
    const object = snapshot.objects[node.uuid];
    if (!object || object.metsUrl !== node.metsUrl || !object.images.length) {
      throw new Error(`Missing digital object: ${node.uuid}`);
    }
    for (const image of object.images) {
      const info = image.info;
      if (seenImages.has(image.id) || !image.id || !image.image.url || image.image.format !== 'image/jpeg'
        || !info.id || info.type !== 'ImageService3' || !['level0', 'level1', 'level2'].includes(info.profile)
        || !Number.isInteger(info.width) || info.width <= 0 || !Number.isInteger(info.height) || info.height <= 0
        || image.infoUrl !== `${info.id}/info.json`) {
        throw new Error(`Invalid or duplicate digital image: ${node.uuid}/${image.id}`);
      }
      seenImages.add(image.id);
    }
  }
  const linked = [...components(snapshot.edition)].filter(node => node.metsUrl);
  if (linked.length !== Object.keys(snapshot.objects).length) throw new Error('Orphan digital objects in snapshot');
}

export function generateArchiveCollection(snapshot: ArchiveSnapshot, baseUrl: string): Map<string, LinkedCollection | Manifest> {
  validateArchiveSnapshot(snapshot);
  const base = normalizeBaseUrl(baseUrl);
  const url = (path: string) => new URL(path, base).href;
  const documents = new Map<string, LinkedCollection | Manifest>();
  const collectionPath = `collections/${archiveEditionSlug}.json`;
  const commonSources = [dataset(snapshot.source, 'EAD-inventaris (actuele versie)'),
    dataset(url(publishedEadPath), `EAD-bronbestand — ${snapshot.eadVersion}`)];
  const commonMetadata = fields([
    { label: 'Archief', value: snapshot.archive.title },
    { label: 'Toegang', value: '2.16.5150' },
    { label: 'Inventarisversie', value: snapshot.eadVersion },
  ]);
  const collection: LinkedCollection = {
    '@context': context, id: url(collectionPath), type: 'Collection',
    label: { nl: ["Rivierkaart 'Nieuwe Stijl'"], en: ["Nieuwe Stijl — Nationaal Archief"] },
    summary: { nl: [snapshot.edition.title], en: ['Digitized river maps, grouped by the series in section D of inventory 2.16.5150.'] },
    metadata: [...commonMetadata, ...fields(snapshot.archive.metadata), ...fields(snapshot.edition.metadata)],
    provider, requiredStatement: attribution(), homepage: [webPage(snapshot.archive.homepage)],
    seeAlso: commonSources, partOf: [{ id: url('collection.json'), type: 'Collection' }], items: [],
  };
  documents.set(collectionPath, collection);

  for (const series of snapshot.edition.children) {
    if (!/^D\.\d{2}$/.test(series.code)) throw new Error(`Unexpected series: ${series.code}`);
    const slug = `series-${series.code.slice(2)}`;
    const path = `manifests/${archiveEditionSlug}/${slug}.json`;
    const id = url(path);
    // Fragment identifiers are dereferenceable and based on archival/image UUIDs,
    // not array positions. Refreshing/reordering source records keeps IDs stable.
    const canvasesByRecord = new Map<string, Canvas[]>();
    const nodes = [...components(series)];
    const records = nodes.filter(node => node.metsUrl);
    const allRights: string[] = [];
    for (const record of records) {
      const object = snapshot.objects[record.uuid]!;
      const rights = object.rights.map(right => right.category);
      allRights.push(...rights);
      const recordCanvases = object.images.map((image): Canvas => {
        const canvasId = `${id}#canvas-${record.uuid}-${image.id}`;
        const dimensions = { width: image.info.width, height: image.info.height };
        const date = record.metadata.find(field => field.label === 'Datering')?.value;
        const title = `${record.inventoryNumber}: ${record.title}${date ? ` — ${date}` : ''}`;
        const parentGroups = nodes.filter(node => node !== record && [...components(node)].some(child => child === record));
        const metadata = [
          ...commonMetadata, ...fields(record.metadata),
          ...fields(parentGroups.flatMap(group => group.metadata.map(field => ({
            label: `${group.code} — ${field.label}`, value: field.value,
          })))),
          ...fields([{ label: 'Scanbestand', value: image.label },
            ...object.rights.flatMap(right => [{ label: 'Rechtencategorie (METS)', value: right.category }, ...right.metadata])]),
        ];
        return {
          id: canvasId, type: 'Canvas', label: { nl: [object.images.length > 1 ? `${title} (${image.order})` : title] },
          ...dimensions, metadata, requiredStatement: attribution(record.inventoryNumber),
          ...(rights.length && rights.every(right => right === 'PUBLIC DOMAIN') ? { rights: 'http://creativecommons.org/publicdomain/mark/1.0/' } : {}),
          ...(record.homepage ? { homepage: [webPage(record.homepage)] } : {}),
          seeAlso: [dataset(record.metsUrl!, 'METS-scangegevens'), dataset(image.infoUrl, 'IIIF Image API metadata', 'application/ld+json')],
          rendering: [download(image.image.url)],
          ...(image.thumbnail ? { thumbnail: [{ id: image.thumbnail.url, type: 'Image', format: image.thumbnail.format }] } : {}),
          items: [{
            id: `${canvasId}-page`, type: 'AnnotationPage', items: [{
              id: `${canvasId}-painting`, type: 'Annotation', motivation: 'painting', target: canvasId,
              body: {
                id: image.image.url, type: 'Image', format: 'image/jpeg', ...dimensions,
                // Preserve image-service capabilities, dimensions, limits and physical scale.
                service: [structuredClone(image.info)],
              },
            }],
          }],
        };
      });
      canvasesByRecord.set(record.uuid, recordCanvases);
    }
    function range(node: ArchiveComponent): Range {
      return {
        id: `${id}#range-${node.uuid}`, type: 'Range',
        label: { nl: [node.code ? `${node.code} — ${node.title}` : node.title] },
        metadata: fields(node.metadata),
        items: node.children.map(child => child.metsUrl
          ? (canvasesByRecord.get(child.uuid) ?? []).map(canvas => ({ id: canvas.id, type: 'Canvas' as const }))
          : [range(child)]).flat(),
      };
    }
    const canvases = records.flatMap(record => canvasesByRecord.get(record.uuid)!);
    if (!canvases.length) throw new Error(`No digitized images in ${series.code}`);
    const manifest: Manifest = {
      '@context': context, id, type: 'Manifest', label: { nl: [`${series.code} — ${series.title}`] },
      metadata: [...commonMetadata, ...fields(snapshot.edition.metadata), ...fields(series.metadata)],
      provider, requiredStatement: attribution(),
      ...(allRights.length && allRights.every(right => right === 'PUBLIC DOMAIN') ? { rights: 'http://creativecommons.org/publicdomain/mark/1.0/' } : {}),
      homepage: [webPage(snapshot.archive.homepage)],
      seeAlso: commonSources, partOf: [{ id: collection.id, type: 'Collection' }],
      behavior: ['individuals'], thumbnail: canvases[0]!.thumbnail,
      items: canvases, structures: [range(series)],
    };
    documents.set(path, manifest);
    collection.items.push({ id, type: 'Manifest', label: manifest.label });
  }
  return documents;
}
