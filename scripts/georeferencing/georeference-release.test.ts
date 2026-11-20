import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';
import { parseAnnotation } from '@allmaps/annotation';
import { progressModel, geometryFingerprint } from './georeference-progress.ts';
const {model, canonical} = await progressModel();

test('release preserves all 999 current approved geometries, observations, original CRSs and metadata', async () => {
  assert.equal(model.accepted, 999);
  const seen = new Set<string>();
  for (const series of model.series) {
    const page = JSON.parse(await readFile(new URL(`../../data/iiif-annotations/nieuwe-stijl/series-${series.id.slice(2)}.json`, import.meta.url), 'utf8'));
    assert.equal(page.items.length, series.total);
    for (const a of page.items) {
      const parsed = parseAnnotation(a)[0];
      const id = parsed.id!.split('/').at(-1)!;
      const map = canonical.get(id)!;
      assert.ok(map, id); assert.ok(!seen.has(id)); seen.add(id);
      assert.deepEqual(parsed.resourceMask, map.mask.resourceMask);
      const controls = map.points.filter(p => p.role === 'control');
      assert.deepEqual(parsed.gcps, controls.map(p => ({resource: p.resourceCoords, geo: p.geo})));
      assert.equal(a['rm:provenance'].geometrySha256, geometryFingerprint(map));
      assert.equal(a['rm:provenance'].humanReview.accepted, true);
      assert.deepEqual(a['rm:quality'].reasons, map.quality.reasons);
      assert.equal(a.metadata.length, map.source.metadata.length);
      controls.forEach((p, i) => {
        assert.deepEqual(a.body.features[i].properties['rm:originalProjected'], p.originalProjected);
        assert.deepEqual(a.body.features[i].properties['rm:rdNew'], p.rdNew);
        assert.deepEqual(a.body.features[i].properties['rm:coordinateDerivation'], p.coordinateDerivation);
      });
      assert.equal(a['rm:heldOutChecks'].length, map.points.filter(p => p.role !== 'control').length);
    }
  }
  assert.equal(seen.size, 999);
});
