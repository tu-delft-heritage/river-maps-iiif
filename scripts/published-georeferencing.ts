import { readFile, readdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { parseAnnotation } from '@allmaps/annotation';
import type { Manifest } from '@iiif/presentation-3';
import { defaultBaseUrl } from './catalog.ts';
import { normalizeBaseUrl, type LinkedCollection } from './collection.ts';
import { canvasNavigationDate, datesInField, maskFeature, navPlaceContext } from './navigation.ts';

const root = fileURLToPath(new URL('../', import.meta.url));
export const georeferenceProfile = 'http://iiif.io/api/extension/georef/1/context.json';
interface Release {
  sourceSha256: string; mapCount: number; seriesCount: number;
  series: {series: string; filename: string; mapCount: number; sha256: string}[];
}
function rebase(value: unknown, base: string): any {
  if (typeof value === 'string') return value.startsWith(defaultBaseUrl) ? base + value.slice(defaultBaseUrl.length) : value;
  if (Array.isArray(value)) return value.map(v => rebase(v, base));
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, rebase(v, base)]));
  return value;
}

/** Publish only the reviewed Nieuwe Stijl snapshot; never discover unrelated annotation files. */
export async function publishGeoreferencing(documents: Map<string, LinkedCollection | Manifest>, baseUrl = defaultBaseUrl, repo = root) {
  const base = normalizeBaseUrl(baseUrl);
  const source = resolve(repo, 'data/iiif-annotations');
  const files = new Map<string, unknown>();
  const counts = new Map<string, number>();
  const release: Release = JSON.parse(await readFile(resolve(source, 'nieuwe-stijl/release.json'), 'utf8'));
  const snapshot = await readFile(resolve(repo, 'data/nationaal-archief/nieuwe-stijl.json'));
  if (createHash('sha256').update(snapshot).digest('hex') !== release.sourceSha256) throw new Error('Publication snapshot refers to different archival metadata');
  const expected = new Map(release.series.map(s => [s.filename, s]));
  const seen = new Set<string>();
  const annotatedCanvases = new Set<string>();
  const dateIssues: unknown[] = [];
  let dated = 0, undated = 0, nieuweStijlMaps = 0;
  for (const document of documents.values()) {
    if (document.type !== 'Manifest') continue;
    for (const canvas of document.items) {
      const navDate = canvasNavigationDate(canvas);
      if (navDate) {canvas.navDate = navDate; dated++;} else {delete canvas.navDate; undated++;}
      const dateFields = (canvas.metadata ?? []).filter(f => f.label.nl?.[0] === 'Datering' || f.label.nl?.[0] === 'Datering (ISO)')
        .map(f => ({label: f.label.nl![0], value: f.value.nl![0]}));
      const text = dateFields.filter(f => f.label === 'Datering').flatMap(datesInField).sort().at(-1);
      const iso = dateFields.filter(f => f.label === 'Datering (ISO)').flatMap(datesInField).sort().at(-1);
      if (dateFields.some(f => f.label === 'Datering (ISO)') && (!iso || (text && iso !== text))) {
        dateIssues.push({canvas: canvas.id, navDate, sourceFields: dateFields,
          note: !iso ? 'Malformed normalized date ignored; readable date used where available.' : 'Date fields disagree; latest usable date selected as requested.'});
      }
    }
  }
  const edition = 'nieuwe-stijl';
  for (const name of (await readdir(resolve(source, edition))).filter(n => /^series-\d+\.json$/.test(n)).sort()) {
    const bytes = await readFile(resolve(source, edition, name));
    const original = JSON.parse(bytes.toString());
    const entry = expected.get(name);
    if (!entry || name === 'series-01.json' || createHash('sha256').update(bytes).digest('hex') !== entry.sha256) throw new Error(`Unverified release page: ${name}`);
    if (original.items.length !== entry.mapCount) throw new Error(`Wrong map count: ${name}`);
    seen.add(name); nieuweStijlMaps += entry.mapCount;
    const path = `annotations/${edition}/${name}`;
    const page = {...rebase(original, base), id: base + path};
    const manifestPath = `manifests/${edition}/${name}`;
    const manifest = documents.get(manifestPath);
    if (!manifest || manifest.type !== 'Manifest') throw new Error(`No manifest for ${path}`);
    const maps = parseAnnotation(page);
    for (const map of maps) {
      const reference = map.resource.partOf?.find(r => r.type === 'Canvas');
      const canvas = manifest.items.find(c => c.id === reference?.id);
      if (!canvas) throw new Error(`Annotation has no matching canvas: ${map.id}`);
      const body = canvas.items?.[0]?.items?.[0]?.body as {service?: {id: string}[]};
      if (!body?.service?.some(s => s.id === map.resource.id)) throw new Error(`Canvas image does not match annotation: ${map.id}`);
      if (annotatedCanvases.has(canvas.id)) throw new Error(`Duplicate map for canvas: ${canvas.id}`);
      annotatedCanvases.add(canvas.id);
      Object.assign(canvas, {navPlace: {id: canvas.id + '-navplace', type: 'FeatureCollection',
        features: [maskFeature(map, canvas.id + '-mask')]}});
      // Canvas-level discovery complements the per-series link on the manifest.
      const canvasReference = {id: page.id, type: 'Dataset' as const, format: 'application/ld+json',
        profile: georeferenceProfile, label: {en: ['Georeference annotations for this series']}};
      canvas.seeAlso = [...(canvas.seeAlso ?? []), canvasReference];
    }
    const contexts = Array.isArray(manifest['@context']) ? manifest['@context'] : [manifest['@context']!];
    manifest['@context'] = [navPlaceContext, ...contexts.filter(c => c !== navPlaceContext)];
    const manifestReference = {id: page.id, type: 'Dataset' as const, format: 'application/ld+json',
      profile: georeferenceProfile, label: {en: [`Georeference annotations — ${maps.length} maps`]}};
    manifest.seeAlso = [...(manifest.seeAlso ?? []), manifestReference];
    files.set(path, page); counts.set(manifest.id, maps.length);
  }
  if (nieuweStijlMaps !== 999 || release.mapCount !== 999 || release.seriesCount !== 16 || seen.size !== expected.size || seen.size !== 16) throw new Error('Incomplete Nieuwe Stijl publication');
  files.set('contexts/river-maps-georeferencing.json', rebase(JSON.parse(await readFile(resolve(source, 'nieuwe-stijl/context.json'), 'utf8')), base));
  files.set('georeferencing/nieuwe-stijl/release.json', rebase(release, base));
  files.set('georeferencing/navigation-report.json', {datedCanvases: dated, undatedCanvases: undated,
    georeferencedCanvases: annotatedCanvases.size, dateIssues,
    datePolicy: 'Latest usable date in the sheet’s own metadata; no inherited series dates. Unknown month/day uses the start of the known period at midnight UTC for navigation, not a claim of exact dating.',
    maskPolicy: 'Allmaps transformation fitted in Web Mercator, transformed back to WGS84 longitude/latitude. Adaptive boundary refinement, closed counterclockwise exterior ring. Source masks and control points unchanged.'});
  return {files, counts};
}
