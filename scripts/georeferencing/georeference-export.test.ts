import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { parseAnnotation } from '@allmaps/annotation';
import { loadCanonicalMaps, generatePages, annotationForMap, viewerComparison } from './georeference-export.ts';
const maps=await loadCanonicalMaps();
test('all pilot maps have draft annotations, release pages enforce quality',()=>{
  const drafts=generatePages(maps,undefined,true),release=generatePages(maps);
  assert.equal(drafts.size,16);
  assert.equal([...drafts.values()].reduce((s,p)=>s+p.items.length,0),24);
  assert.equal([...release.values()].reduce((s,p)=>s+p.items.length,0),7);
  for(const page of release.values())for(const a of page.items)assert.equal(a['rm:quality'].status,'pilot-pass');
  assert.throws(()=>generatePages([{...maps[0],source:{...maps[0].source,series:'D.01'}}]),/indices/);
});
test('Allmaps import retains native geometry and excludes held-out controls',()=>{
  for(const map of maps){
    const a=annotationForMap(map);const parsed=parseAnnotation(a)[0];
    assert.equal(parsed.gcps.length,4);
    assert.deepEqual(parsed.resourceMask,map.mask.resourceMask);
    assert.equal(parsed.resource.id,map.source.imageService.id);
    assert.equal(parsed.resource.type,'ImageService3');
    assert.doesNotMatch(a.target.selector.value,/viewBox|transform=/);
    const p=map.points.filter(p=>p.role==='control');
    a.body.features.forEach((feature,i)=>{
      const extended=feature.properties as Record<string,unknown>;
      assert.deepEqual(extended['rm:originalProjected'],p[i].originalProjected);
      assert.deepEqual(extended['rm:rdNew'],p[i].rdNew);
      assert.deepEqual(feature.geometry.coordinates,p[i].geo);
    });
  }
});
test('custom base URLs rebase annotation, provenance, parent and context links, not image services',()=>{
  const base='https://example.org/maps/';
  for(const map of maps){
    const a=annotationForMap(map,base);
    assert.ok(a.id!.startsWith(base));assert.ok(a.seeAlso[0].id.startsWith(base));
    assert.ok(a.target.source.partOf![0].id.startsWith(base));
    assert.ok(a.target.source.partOf![0].partOf![0].id.startsWith(base));
    assert.ok('id' in a.target.source);
    assert.equal(a.target.source.id,map.source.imageService.id);
    assert.equal(a['@context'].at(-1),base+'contexts/river-maps-georeferencing.json');
  }
});
test('renderer geometry agrees with RD affine within 1 metre for released pilot maps',async()=>{
  const samples=JSON.parse(await readFile(new URL('../../data/georeferencing/nieuwe-stijl/viewer-samples.json',import.meta.url),'utf8'));
  for(const map of maps.filter(m=>m.quality.releaseEligible)){
    const result=viewerComparison(map,samples[map.id]);
    assert.ok(result.sampleCount>150);
    assert.ok(result.mercatorMaxGroundMetres<1);
    assert.ok(result.lonLatMaxGroundMetres<1);
  }
});
test('exports are deterministic and do not mutate canonical observations',()=>{
  const original=JSON.stringify(maps);
  assert.equal(JSON.stringify([...generatePages(maps)]),JSON.stringify([...generatePages(maps)]));
  assert.equal(JSON.stringify(maps),original);
});
