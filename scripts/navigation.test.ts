import assert from 'node:assert/strict';
import test from 'node:test';
import type { GeoreferencedMap } from '@allmaps/annotation';
import { canvasNavigationDate, datesInField, fromMercator, maskFeature, navigationDate, signedArea } from './navigation.ts';
import type { Canvas } from '@iiif/presentation-3';

test('dates use the latest explicit date, preserve known precision, and omit undated records', () => {
  const d = (value: string, iso?: string) => navigationDate([{label: 'Datering', value}, ...(iso ? [{label: 'Datering (ISO)', value: iso}] : [])]);
  assert.equal(d('bijgewerkt tot november 1978, met toevoegingen tot 31 maart 1982'), '1982-03-31T00:00:00Z');
  assert.equal(d('bijgewerkt tot juni 1964, enkele elementen gedateerd 30 januari 1980', '19800130'), '1980-01-30T00:00:00Z');
  assert.equal(d('1974-1976', '1974/1976'), '1976-01-01T00:00:00Z');
  assert.equal(d('bijgewerkt tot december 1958, situatie van 1960', '1960'), '1960-01-01T00:00:00Z');
  assert.equal(d('jannuari 1997'), '1997-01-01T00:00:00Z');
  assert.equal(d('augsutus 1986'), '1986-08-01T00:00:00Z');
  assert.equal(d('bijgewerkt tot juni 1979', '19749-06'), '1979-06-01T00:00:00Z');
  assert.equal(d('bijgewerkt tot februari 1968', '11968-02'), '1968-02-01T00:00:00Z');
  assert.equal(d('bijgewerkt tot september 1979', '09-1979'), '1979-09-01T00:00:00Z');
  assert.equal(d('bijgewerkt tot april 1989', '1998-04'), '1998-04-01T00:00:00Z');
  assert.equal(d('ongedateerd'), undefined);
  assert.equal(navigationDate([]), undefined);
  assert.deepEqual(datesInField({label: 'Datering (ISO)', value: '1981-02-29'}), []);
  assert.equal(d('1980-02-29'), '1980-02-29T00:00:00Z');
});

test('sheet dates do not inherit series ranges or scan and photography dates', () => {
  const canvas = {id: 'https://example.org/canvas', type: 'Canvas', metadata: [
    {label: {nl: ['D.02 — Datering']}, value: {nl: ['1958-1998']}},
    {label: {nl: ['Inhoud']}, value: {nl: ['Luchtfotografie: april 1964']}},
    {label: {nl: ['Datering']}, value: {nl: ['ongedateerd']}},
  ]} as Canvas;
  assert.equal(canvasNavigationDate(canvas), undefined);
});

test('navPlace follows the masked area using the Viewer projection, closed CCW lon/lat coordinates', () => {
  const project = ([x, y]: [number, number]): [number, number] => fromMercator([500000 + 2 * x + y, 6800000 + x - 2 * y]);
  const resourceMask: [number, number][] = [[20, 20], [100, 20], [100, 100], [20, 100]];
  const map: GeoreferencedMap = {type: 'GeoreferencedMap', id: 'https://example.org/map',
    resource: {id: 'https://example.org/image', type: 'ImageService3', width: 1000, height: 1000},
    transformation: {type: 'polynomial', options: {order: 1}}, resourceMask,
    gcps: ([[0, 0], [1000, 0], [0, 1000], [1000, 1000]] as [number, number][]).map(resource => ({resource, geo: project(resource)}))};
  const original = JSON.stringify(map);
  const feature = maskFeature(map, 'https://example.org/canvas#mask');
  const ring = feature.geometry.coordinates[0];
  assert.equal(feature.geometry.type, 'Polygon');
  assert.deepEqual(ring[0], ring.at(-1));
  assert.ok(signedArea(ring) > 0);
  for (const corner of resourceMask.map(project)) assert.ok(ring.some(p => Math.hypot(p[0] - corner[0], p[1] - corner[1]) < 1e-9));
  assert.ok(ring.every(([lon, lat]) => lon > 4 && lon < 5 && lat > 51 && lat < 53));
  assert.equal(JSON.stringify(map), original);
});
