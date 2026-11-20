import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { parseAnnotation } from '@allmaps/annotation';
import { annotationForMap, extensionContext, contextPath } from './georeference-export.ts';
import { progressModel, geometryFingerprint } from './georeference-progress.ts';
import { defaultBaseUrl } from '../catalog.ts';

const root = fileURLToPath(new URL('../../', import.meta.url));
const destination = resolve(root, 'data/iiif-annotations/nieuwe-stijl');
const {model, canonical} = await progressModel(root);
if (model.total !== 999 || model.accepted !== 999 || canonical.size !== 999 || model.series.length !== 16) {
  throw new Error('Release requires all 999 exact geometries to have current human approval');
}
const escape = (s: string) => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
const context = structuredClone(extensionContext);
for (const key of ['provenance', 'heldOutChecks']) {
  Object.assign(context['@context'], {[`rm:${key}`]: {'@id': defaultBaseUrl + contextPath + '#' + key, '@type': '@json'}});
}
const source = await readFile(resolve(root, 'data/nationaal-archief/nieuwe-stijl.json'));
const sourceSha256 = createHash('sha256').update(source).digest('hex');
const files = new Map<string, unknown>();
const series = model.series.map(s => {
  const maps = [...canonical.values()].filter(m => m.source.series === s.id)
    .sort((a, b) => Number(a.source.inventoryNumber) - Number(b.source.inventoryNumber));
  const filename = `series-${s.id.slice(2)}.json`;
  const page = {
    '@context': ['http://www.w3.org/ns/anno.jsonld', 'http://iiif.io/api/presentation/3/context.json'],
    id: defaultBaseUrl + 'annotations/nieuwe-stijl/' + filename, type: 'AnnotationPage',
    label: {nl: [`${s.id} — ${s.title}`]},
    items: maps.map(map => {
      const annotation = annotationForMap(map);
      const review = model.maps.find(m => m.id === map.id)!;
      return {...annotation,
        metadata: (map.source.metadata as {label: string; value: string}[]).map(f => ({label: {nl: [f.label]}, value: {nl: [escape(f.value)]}})),
        rights: 'http://creativecommons.org/publicdomain/mark/1.0/',
        'rm:quality': {status: map.quality.status, reasons: map.quality.reasons, numericScreenPassed: map.quality.releaseEligible},
        'rm:provenance': {inventoryNumber: map.source.inventoryNumber, series: map.source.series,
          sourceSha256, geometrySha256: geometryFingerprint(map), humanReview: {accepted: true, recordedOn: review.recordedOn}},
        'rm:heldOutChecks': map.points.filter(p => p.role !== 'control').map(p => ({
          id: p.id, role: p.role, resourceCoords: p.resourceCoords, geo: p.geo, rdNew: p.rdNew,
          originalProjected: p.originalProjected, evidenceId: p.evidenceId, coordinateDerivation: p.coordinateDerivation,
        })),
        seeAlso: [{id: defaultBaseUrl + 'georeferencing/nieuwe-stijl/release.json', type: 'Dataset', format: 'application/json',
          label: {en: ['Release provenance and coordinate conventions']}}],
      };
    }),
  };
  const parsed = parseAnnotation(page);
  if (parsed.length !== maps.length) throw new Error('Annotation count changed during parsing');
  files.set(filename, page);
  return {series: s.id, filename, mapCount: maps.length,
    sha256: createHash('sha256').update(JSON.stringify(page, null, 2) + '\n').digest('hex')};
});
files.set('context.json', context);
files.set('release.json', {
  schemaVersion: 1, edition: 'Nieuwe Stijl', mapCount: 999, seriesCount: 16, excludedIndexScans: 10,
  sourceSha256, series,
  selection: 'Every digitized map in D.02–D.17 with current human approval of its exact mask and measured points. D.01 sheet indices and legends excluded.',
  quality: 'Visual acceptance does not erase numerical flags or establish survey accuracy. Held-out points are preserved as evidence and excluded from the fitted transformation.',
  coordinates: 'Control-point geometry is WGS84 longitude/latitude. rm:originalProjected preserves printed coordinates and their CRS, including RD Old EPSG:28991 where applicable. rm:rdNew preserves converted RD New EPSG:28992 metres.',
  transformation: 'The approved annotations use polynomial order 1. Canvas navPlace masks use @allmaps/transform 1.0.0-beta.53 fitted in EPSG:3857, matching Allmaps Viewer, and return closed counterclockwise WGS84 longitude/latitude polygons.',
  dates: 'navDate uses the latest valid date from the sheet’s own Datering and Datering (ISO) metadata. Missing month/day is represented by January/1st at 00:00:00Z for navigation only. Original text and precision remain in metadata. Undated sheets and missing sheet dates are omitted; series date ranges are not inherited.',
  projection: JSON.parse(await readFile(resolve(root, 'data/georeferencing/nieuwe-stijl/projection.json'), 'utf8')),
  researchBranch: 'codex/nieuwe-stijl-georeferencing-plan',
});
// Compute and validate every document before replacing the previous pilot snapshot.
await rm(destination, {recursive: true, force: true});
for (const [name, document] of files) {
  const file = resolve(destination, name); await mkdir(dirname(file), {recursive: true});
  await writeFile(file, JSON.stringify(document, null, 2) + '\n');
}
console.log(`Released ${canonical.size} human-approved maps in ${series.length} series.`);
