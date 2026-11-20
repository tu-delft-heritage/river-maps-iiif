import { GcpTransformer } from '@allmaps/transform';
import type { GeoreferencedMap } from '@allmaps/annotation';
import type { Canvas, MetadataItem } from '@iiif/presentation-3';

type Point = [number, number];
export const navPlaceContext = 'http://iiif.io/api/extension/navplace/context.json';
const months = new Map([
  ['januari', 1], ['jannuari', 1], ['jan', 1], ['februari', 2], ['maart', 3],
  ['april', 4], ['mei', 5], ['juni', 6], ['juli', 7], ['augustus', 8], ['augsutus', 8],
  ['september', 9], ['oktober', 10], ['november', 11], ['december', 12],
]);
export interface DateField { label: string; value: string }
function date(year: number, month = 1, day = 1): string | undefined {
  if (year < 1000 || year > 9999 || month < 1 || month > 12 || day < 1 || day > 31) return;
  const value = new Date(Date.UTC(year, month - 1, day));
  if (value.getUTCFullYear() !== year || value.getUTCMonth() !== month - 1 || value.getUTCDate() !== day) return;
  return value.toISOString().replace('.000Z', 'Z');
}
export function datesInField(field: DateField): string[] {
  const dates: string[] = [];
  const add = (y: string, m?: string, d?: string) => {
    const value = date(Number(y), m ? Number(m) : 1, d ? Number(d) : 1);
    if (value) dates.push(value);
  };
  if (field.label === 'Datering (ISO)') {
    // Reject malformed normalized values instead of guessing what a typo meant.
    for (const token of field.value.trim().split(/[\s/,;]+/)) {
      const m = /^(\d{4})(?:-?(\d{2})(?:-?(\d{2}))?)?$/.exec(token);
      if (m) add(m[1], m[2], m[3]);
    }
  } else {
    for (const m of field.value.toLowerCase().matchAll(/\b(?:(\d{1,2})\s+)?([a-z]+)\.?\s+(\d{4})\b/g)) {
      const month = months.get(m[2]);
      if (month) add(m[3], String(month), m[1]);
    }
    for (const m of field.value.matchAll(/(?<!\d)(\d{4})-(\d{2})(?:-(\d{2}))?(?!\d)/g)) add(m[1], m[2], m[3]);
    // Year-only dates and the endpoints of year ranges remain useful navigation dates.
    for (const m of field.value.matchAll(/(?<!\d)(\d{4})(?!\d)/g)) add(m[1]);
  }
  return [...new Set(dates)].sort();
}
export function navigationDate(fields: DateField[]): string | undefined {
  return fields.filter(f => ['Datering', 'Datering (ISO)', 'Date', 'Published'].includes(f.label))
    .flatMap(datesInField).sort().at(-1);
}
export function canvasNavigationDate(canvas: Canvas): string | undefined {
  // Use this sheet's own fields, never an inherited series publication range.
  const fields = (canvas.metadata ?? []).flatMap((item: MetadataItem) => {
    const labels = Object.values(item.label).flat().filter((s): s is string => typeof s === 'string');
    return labels.flatMap(label => Object.values(item.value).flat().filter((s): s is string => typeof s === 'string').map(value => ({label, value})));
  });
  return navigationDate(fields);
}

export const toMercator = ([lon, lat]: Point): Point => [
  6378137 * lon * Math.PI / 180, 6378137 * Math.log(Math.tan(Math.PI / 4 + lat * Math.PI / 360)),
];
export const fromMercator = ([x, y]: Point): Point => [
  x / 6378137 * 180 / Math.PI, (2 * Math.atan(Math.exp(y / 6378137)) - Math.PI / 2) * 180 / Math.PI,
];
export function signedArea(ring: Point[]): number {
  const [x, y] = ring[0];
  return ring.slice(1).reduce((sum, p, i) => sum + (ring[i][0] - x) * (p[1] - y) - (p[0] - x) * (ring[i][1] - y), 0) / 2;
}
export function maskFeature(map: GeoreferencedMap, id: string) {
  // Allmaps Viewer fits in Web Mercator. Transform there, then return RFC 7946 lon/lat.
  const transformer = GcpTransformer.fromGeoreferencedMap({
    ...map, gcps: map.gcps.map(gcp => ({...gcp, geo: toMercator(gcp.geo)})),
  });
  const ring = transformer.transformToGeo([map.resourceMask], {
    postToGeo: fromMercator, maxDepth: 8, minOffsetRatio: Infinity, minOffsetDistance: 1e-7,
  })[0] as Point[];
  if (!ring.length || ring.some(p => p.length !== 2 || !p.every(Number.isFinite) || Math.abs(p[0]) > 180 || Math.abs(p[1]) > 90)) {
    throw new Error(`Invalid geographic mask: ${map.id}`);
  }
  if (ring[0][0] !== ring.at(-1)![0] || ring[0][1] !== ring.at(-1)![1]) ring.push([...ring[0]]);
  if (ring.length < 4 || Math.abs(signedArea(ring)) < 1e-14) throw new Error(`Degenerate geographic mask: ${map.id}`);
  if (signedArea(ring) < 0) ring.reverse();
  return {id, type: 'Feature' as const, properties: {}, geometry: {type: 'Polygon' as const, coordinates: [ring]}};
}
