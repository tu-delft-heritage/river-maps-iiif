import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { parseAnnotation } from '@allmaps/annotation';
import { loadBatch, reviewPage, assertReviewed, batchFolder } from './georeference-batch-export.ts';

for(const [name,count] of [['batch-01',50],['batch-02',24],['batch-03',81]] as const) test(`${name} exports all ${count} maps with metadata, masks and original RD coordinates, excluding checks`,async()=>{
  const maps=await loadBatch(name);
  const page=reviewPage(maps,name),parsed=parseAnnotation(page);
  assert.equal(maps.length,count);assert.equal(new Set(parsed.map(m=>m.resource.id)).size,count);
  for(let i=0;i<maps.length;i++){
    const m=maps[i],a=page.items[i];
    assert.notEqual(m.source.series,'D.01');assert.equal(m.quality.releaseEligible,false);
    assert.deepEqual(a.metadata,m.source.metadata);
    assert.deepEqual(parsed[i].resourceMask,m.mask.resourceMask);
    const controls=m.points.filter(p=>p.role==='control');
    assert.deepEqual(parsed[i].gcps,controls.map(p=>({resource:p.resourceCoords,geo:p.geo})));
    assert.deepEqual(a.body.features.map(f=>(f.properties as Record<string,unknown>)['rm:originalProjected']),controls.map(p=>p.originalProjected));
    assert.equal(a.body.features.length,4);assert.equal(m.points.filter(p=>p.role==='check').length,1);
    assert.ok(a['@context'].every(c=>typeof c==='string'));
  }
});
test('editing a point, raw coordinate or mask invalidates geometry approval',async()=>{
  const map=(await loadBatch('batch-01'))[0];
  const approved=JSON.parse(await readFile(batchFolder('batch-01')+'/geometry-review.json','utf8')).maps[map.id];
  for(const mutate of [
    (m:typeof map)=>{m.points[0].resourceCoords[0]+=1;},
    (m:typeof map)=>{m.points[0].originalProjected={crs:'EPSG:28992',coordinates:[1,2]};},
    (m:typeof map)=>{m.mask.resourceMask[0][0]+=1;}
  ]){const changed=structuredClone(map);mutate(changed);assert.throws(()=>assertReviewed(changed,approved),/stale/);}
  assert.throws(()=>batchFolder('../maps'),/batch-NN/);
});
