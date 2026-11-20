import { readFile, writeFile, readdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { isDeepStrictEqual } from 'node:util';
import { parseAnnotation } from '@allmaps/annotation';
import { annotationForMap, viewerComparison, type CanonicalMap, type Point } from './georeference-export.ts';
import { defaultBaseUrl } from '../catalog.ts';
import { buildProgress } from './georeference-progress.ts';

const root=fileURLToPath(new URL('../../',import.meta.url));
const data=resolve(root,'data/georeferencing/nieuwe-stijl');
export function batchFolder(name:string) {
  if(!/^batch-\d{2}$/.test(name))throw new Error('Expected batch-NN');
  return resolve(data,'batches',name);
}
const read=async(path:string)=>JSON.parse(await readFile(path,'utf8'));
const save=async(path:string,value:unknown)=>writeFile(path,JSON.stringify(value,null,2)+'\n');
export function assertReviewed(map:CanonicalMap,approved:unknown) {
  const geometry={resourceMask:map.mask.resourceMask,points:map.points.map(p=>({
    id:p.id,role:p.role,resourceCoords:p.resourceCoords,rdNew:p.rdNew,geo:p.geo,originalProjected:p.originalProjected}))};
  if(!isDeepStrictEqual(geometry,approved)||map.mask.reviewStatus!=='ai-visually-reviewed')
    throw new Error(`Geometry review is missing or stale: ${map.id}`);
  if(map.source.series==='D.01'||map.quality.releaseEligible||map.quality.reasons.some(r=>!['rms-above-2px','check-above-5px','poor-control-coverage','ill-conditioned-controls'].includes(r)))
    throw new Error(`Not a reviewed batch candidate: ${map.id}`);
  if(map.points.filter(p=>p.role==='control').length!==4||map.points.filter(p=>p.role==='check').length!==1)
    throw new Error(`Expected four controls and a held-out check: ${map.id}`);
}
export async function loadBatch(name:string):Promise<CanonicalMap[]> {
  const folder=batchFolder(name),selection=await read(resolve(folder,'selection.json'));
  const snapshot=await readFile(resolve(root,'data/nationaal-archief/nieuwe-stijl.json'));
  const hash=createHash('sha256').update(snapshot).digest('hex');
  const catalog=await read(resolve(data,'selection.json'));
  const count=selection.selectedCount??50;
  if(!Number.isInteger(count)||count<1||count>(selection.mode==='whole-series'?catalog.records.length:50)||selection.batchId!==name||selection.sourceSha256!==hash||selection.eadSha256!==catalog.eadSha256||selection.records.length!==count)
    throw new Error('Batch/source snapshot mismatch');
  if(selection.mode==='whole-series') {
    if(!selection.series)throw new Error('Whole-series batch requires a series');
    const prior=new Set<string>(catalog.records.filter((r:{pilot:boolean})=>r.pilot).map((r:{id:string})=>r.id));
    for(const previous of (await readdir(resolve(data,'batches'))).filter(n=>/^batch-\d{2}$/.test(n)&&n<name)) {
      const selected=await read(resolve(batchFolder(previous),'selection.json'));
      for(const r of selected.records)prior.add(r.id);
    }
    const expected=catalog.records.filter((r:{id:string;series:string})=>r.series===selection.series&&!prior.has(r.id));
    if(!isDeepStrictEqual(selection.records,expected))throw new Error('Whole-series selection is incomplete or out of source order');
  }
  const known=new Map<string,unknown>(catalog.records.map((r:{id:string})=>[r.id,r]));
  const approved=(await read(resolve(folder,'geometry-review.json'))).maps;
  const maps:CanonicalMap[]=[];
  for(const record of selection.records){
    if(record.pilot||!isDeepStrictEqual(known.get(record.id),record)||(selection.series&&record.series!==selection.series))throw new Error('Pilot, out-of-scope or modified source record in batch');
    const map:CanonicalMap=await read(resolve(folder,'maps',record.id+'.json'));
    if(map.sourceSha256!==hash||map.batchId!==name||!isDeepStrictEqual(map.source,record))throw new Error('Stale canonical map');
    assertReviewed(map,approved[map.id]);maps.push(map);
  }
  if(new Set(maps.map(m=>m.id)).size!==count)throw new Error('Duplicate scans');
  return maps;
}
export function reviewPage(maps:CanonicalMap[],name:string) {
  const items=maps.map(map=>{
    const annotation=annotationForMap(map);
    // Retain the pilot format: the installed Allmaps parser requires context URL strings.
    // These IDs identify local review artifacts; this exporter does not publish them.
    return {...annotation,metadata:map.source.metadata,seeAlso:[{...annotation.seeAlso[0],
      id:defaultBaseUrl+`georeferencing/nieuwe-stijl/batches/${name}/maps/${map.id}.json`}]};
  });
  const page={type:'AnnotationPage',id:`urn:river-maps:nieuwe-stijl:${name}:review`,
    '@context':'http://www.w3.org/ns/anno.jsonld',
    label:{en:[`Nieuwe Stijl ${name}: ${maps.length} maps for review`]},items};
  const parsed=parseAnnotation(page);
  if(parsed.length!==maps.length)throw new Error('Allmaps dropped annotations');
  return page;
}
export async function exportBatch(name='batch-01') {
  const startedAt=new Date().toISOString(),clock=performance.now();
  const folder=batchFolder(name),maps=await loadBatch(name);
  const samples:Record<string,{resource:Point;geo:Point}[]>=await read(resolve(folder,'viewer-samples.json'));
  const results=maps.map(m=>viewerComparison(m,samples[m.id]));
  if(results.some(r=>!Number.isFinite(r.mercatorMaxGroundMetres)||r.mercatorMaxGroundMetres>5))
    throw new Error('Viewer transformation differs from RD affine by more than 5 metres');
  await save(resolve(folder,'review-annotations.json'),reviewPage(maps,name));
  await save(resolve(folder,'viewer-report.json'),{results,limitGroundMetres:5,
    limitation:'Numerical Allmaps renderer-geometry check, not a browser screenshot test or independent survey validation.'});
  const catalog=await read(resolve(data,'selection.json'));
  const pilotIds=new Set<string>(catalog.records.filter((r:{pilot:boolean})=>r.pilot).map((r:{id:string})=>r.id));
  const batches=[];const processed=new Set(pilotIds);
  for(const batch of (await readdir(resolve(data,'batches'))).filter(n=>/^batch-\d{2}$/.test(n)).sort()){
    const reportPath=resolve(batchFolder(batch),'report.json');
    let report;
    try{report=await read(reportPath);}catch(error){if((error as NodeJS.ErrnoException).code==='ENOENT')continue;throw error;}
    for(const row of report.results){if(processed.has(row.mapId))throw new Error('Duplicate batch coverage');processed.add(row.mapId);}
    batches.push({batchId:batch,processed:report.scans,humanReview:report.humanReview});
  }
  await save(resolve(data,'batches/coverage.json'),{digitizedMaps:catalog.records.length,pilotProcessed:pilotIds.size,
    processed:processed.size,remaining:catalog.records.length-processed.size,batches,
    meaning:'Processed means prepared for review; it does not imply released or accepted.'});
  console.log(`Exported ${maps.length} reviewed candidates to ${folder}/review-annotations.json`);
  const timingPath=resolve(folder,'processing.json');
  let timing;
  try {timing=await read(timingPath);} catch(error) {if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
  if(timing) {
    const completedAt=new Date().toISOString();
    timing.commands.push({command:'export',startedAt,completedAt,elapsedSeconds:(performance.now()-clock)/1000,success:true});
    // Preserve the original preparation interval when replaying an exported batch.
    if(!timing.completedAt) {
      timing.completedAt=completedAt;
      timing.elapsedSeconds=(Date.parse(completedAt)-Date.parse(timing.startedAt))/1000;
    }
    await save(timingPath,timing);
  }
  await buildProgress();
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await exportBatch(process.argv[2]??'batch-01');
