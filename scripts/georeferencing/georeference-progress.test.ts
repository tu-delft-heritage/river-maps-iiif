import test from 'node:test';
import assert from 'node:assert/strict';
import { parseAnnotation } from '@allmaps/annotation';
import { reviewPage } from './georeference-batch-export.ts';
import { progressModel, geometryFingerprint, visualAcceptance, renderProgress, usableViewerUrl } from './georeference-progress.ts';

test('dashboard accounts for every digitized map and separates acceptance from QA',async()=>{
  const {model,canonical}=await progressModel();
  assert.equal(model.total,999);
  assert.equal(model.accepted,999);
  assert.equal(model.pending,0);
  assert.equal(model.prepared,model.accepted+model.pending);
  assert.equal(model.remaining,999-model.prepared);
  const d02=model.series.find(s=>s.id==='D.02')!;
  assert.deepEqual([d02.total,d02.prepared,d02.accepted,d02.pending,d02.remaining],[76,76,76,0,0]);
  const d03=model.series.find(s=>s.id==='D.03')!;
  assert.deepEqual([d03.total,d03.prepared,d03.accepted,d03.pending,d03.remaining],[83,83,83,0,0]);
  const b03=model.batches.find(b=>b.id==='batch-03')!;
  assert.ok(b03.processing && b03.processing.commandSeconds>0);
  assert.ok(!('tokenUsage' in b03.processing));
  assert.ok(!('visionTokenUsage' in b03.processing));
  assert.equal(model.batches.find(b=>b.id==='batch-02')!.processing,null);
  assert.ok(!model.maps.some(m=>m.series==='D.01'));
  assert.ok(model.maps.some(m=>m.status==='accepted'&&m.flags.length>0));
  assert.equal(new Set(model.maps.map(m=>m.id)).size,model.total);
  assert.equal(canonical.size,model.prepared);
  for(const id of model.series.map(s=>s.id)) {
    const series=model.series.find(s=>s.id===id)!;
    assert.equal(series.accepted,series.total,id);
  }
  const batchIds = new Set(model.maps.filter(m => m.batchId === 'batch-02').map(m => m.id));
  const batch = reviewPage([...canonical.values()].filter(m => batchIds.has(m.id)), 'batch-02');
  assert.equal(parseAnnotation(batch).length, 24);
  const series = reviewPage([...canonical.values()].filter(m => m.source.series === 'D.03'), 'D.03');
  assert.equal(parseAnnotation(series).length, 83);
  const html=renderProgress(model);
  assert.ok(!/Vision tokens|Model tokens/.test(html));
  assert.ok(html.includes('Not recorded'));
  assert.ok(html.includes('Elapsed incl. review'));
});

test('oversized aggregate URLs retain downloads while series links remain usable',()=>{
  assert.ok(usableViewerUrl({type:'AnnotationPage',items:[]}));
  assert.equal(usableViewerUrl({data:'x'.repeat(2_000_000)}),undefined);
});

test('visual acceptance expires when any reviewed geometry changes',async()=>{
  const {canonical}=await progressModel();const map=[...canonical.values()][0];
  const events=[{batchId:'pilot',recordedOn:'2026-11-19',basis:'User review',maps:[{id:map.id,geometrySha256:geometryFingerprint(map)}]}];
  assert.equal(visualAcceptance(map,events).accepted,true);
  for(const change of [
    (m:typeof map)=>{m.mask.resourceMask[0][0]+=1;},
    (m:typeof map)=>{m.points[0].resourceCoords[0]+=1;},
    (m:typeof map)=>{m.points[0].originalProjected={crs:'EPSG:28992',coordinates:[1,2]};}
  ]) {const edited=structuredClone(map);change(edited);assert.equal(visualAcceptance(edited,events).accepted,false);assert.equal(visualAcceptance(edited,events).stale,true);}
  assert.equal(visualAcceptance(map,[]).accepted,false);
});

test('embedded source metadata cannot break out of the dashboard data script',async()=>{
  const {model}=await progressModel();model.maps[0].title='</script><script>alert(1)</script>';
  const html=renderProgress(model);
  assert.ok(!html.includes('</script><script>alert(1)'));
  assert.ok(html.includes('\\u003c/script>'));
});
