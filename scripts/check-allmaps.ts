import { readFile, readdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { IIIF } from '@allmaps/iiif-parser';
import { parseAnnotation } from '@allmaps/annotation';

/** Check the exact publication documents, without fetching images or changing data. */
export function validateAllmapsDocuments(documents: ReadonlyMap<string, unknown>) {
  const counts = {collections: 0, manifests: 0, canvases: 0, annotationPages: 0, maps: 0};
  for (const [path, document] of documents) {
    try {
      const source = document as {id?: unknown; type?: unknown; items?: {id?: unknown}[]};
      if (path.startsWith('annotations/')) {
        if (source?.type !== 'AnnotationPage') throw new Error('Expected an AnnotationPage');
        const maps = parseAnnotation(document);
        if (maps.length !== source.items?.length) throw new Error('Parser did not retain every map annotation');
        counts.annotationPages++; counts.maps += maps.length;
      } else {
        const expected = path === 'collection.json' || path.startsWith('collections/') ? 'collection'
          : path.startsWith('manifests/') ? 'manifest' : undefined;
        if (!expected) throw new Error('Unexpected IIIF document path');
        const parsed = IIIF.parse(document);
        if (parsed.type !== expected || parsed.uri !== source.id) throw new Error('Parser changed the resource type or identity');
        const items = parsed.type === 'collection' ? parsed.items : parsed.type === 'manifest' ? parsed.canvases : [];
        if (!Array.isArray(source.items) || items.length !== source.items.length
          || items.some((item, i) => item.uri !== source.items![i].id)) {
          throw new Error('Parser did not retain every collection item or canvas in order');
        }
        if (parsed.type === 'collection') counts.collections++;
        if (parsed.type === 'manifest') {counts.manifests++; counts.canvases += parsed.canvases.length;}
      }
    } catch (cause) {
      throw new Error(`Allmaps rejected ${path}: ${cause instanceof Error ? cause.message : String(cause)}`, {cause});
    }
  }
  return counts;
}

/** Validate committed output independently of generation, including before deployment. */
export async function checkPublishedAllmaps(output = fileURLToPath(new URL('../iiif/', import.meta.url))) {
  const documents = new Map<string, unknown>();
  async function read(path: string) {
    try {documents.set(path, JSON.parse(await readFile(resolve(output, path), 'utf8')));}
    catch (cause) {throw new Error(`Cannot read published IIIF JSON: ${path}`, {cause});}
  }
  async function walk(folder: string) {
    for (const entry of (await readdir(resolve(output, folder), {withFileTypes: true})).sort((a, b) => a.name.localeCompare(b.name))) {
      const path = `${folder}/${entry.name}`;
      if (entry.isDirectory()) await walk(path);
      else if (entry.name.endsWith('.json')) await read(path);
    }
  }
  await read('collection.json');
  for (const folder of ['collections', 'manifests', 'annotations']) await walk(folder);
  return validateAllmapsDocuments(documents);
}

export function allmapsCheckSummary(counts: ReturnType<typeof validateAllmapsDocuments>): string {
  return `Allmaps accepted ${counts.collections} collections, ${counts.manifests} manifests (${counts.canvases} canvases), and ${counts.annotationPages} annotation pages (${counts.maps} maps).`;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  console.log(allmapsCheckSummary(await checkPublishedAllmaps(process.argv[2])));
}
