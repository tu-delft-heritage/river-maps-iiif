import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {shapeDiagnostics} from './georeference-shape.ts';
import {progressModel} from './georeference-progress.ts';

test('screen distinguishes raster y reversal from a reflected map, independent of residuals',()=>{
  assert.deepEqual(shapeDiagnostics([[0,2],[2,0]]).flags,[]);
  assert.deepEqual(shapeDiagnostics([[2,0],[0,-2]]).flags,[]);
  assert.deepEqual(shapeDiagnostics([[2,0],[0,2]]).flags,['mirrored-grid']);
  assert.ok(shapeDiagnostics([[2.2,0],[0,-2]]).flags.includes('directional-stretch-over-2pct'));
  assert.ok(shapeDiagnostics([[2,.3],[0,-2]]).flags.includes('grid-skew-over-1deg'));
  assert.throws(()=>shapeDiagnostics([[1,1],[1,1]]),/Singular/);
});

test('screen catches every original reflected/skewed case including both additional copies',async()=>{
  const root=new URL('../../data/georeferencing/nieuwe-stijl/rechecks/2026-11-20/',import.meta.url);
  const {cases}=JSON.parse(await readFile(new URL('cases.json',root),'utf8'));
  const flagged=[];
  for(const c of cases){
    const before=JSON.parse(await readFile(new URL(c.beforeCanonical,root),'utf8'));
    const shape=shapeDiagnostics(before.adjustment.linear);
    if(shape.flags.length)flagged.push(c.inventoryNumber);
  }
  assert.deepEqual(flagged.sort(),['1123','1148','1149','1151','1381','625','751'].sort());
  // 1284 had a uniform offset: shape screening alone cannot detect translation.
});

test('all corrected scans remain in the eight-map review set with no large shape anomalies',async()=>{
  const {model}=await progressModel();
  assert.equal(model.shapeScreen.tested,999);
  assert.equal(model.shapeScreen.flagged,0);
  const group=model.rechecks.find(g=>g.id==='2026-11-20')!;
  assert.deepEqual(model.maps.filter(m=>group.mapIds.includes(m.id)).map(m=>m.inventory).sort(),
    ['1123','1148','1149','1151','1284','1381','625','751'].sort());
  assert.equal(group.pending,0);
  assert.equal(group.accepted,8);
});
