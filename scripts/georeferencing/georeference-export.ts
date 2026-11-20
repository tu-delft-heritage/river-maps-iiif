import { readFile, readdir, mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { generateAnnotation, parseAnnotation, type GeoreferencedMap } from '@allmaps/annotation';
import { GcpTransformer } from '@allmaps/transform';
import { defaultBaseUrl } from '../catalog.ts';
import { normalizeBaseUrl } from '../collection.ts';
export type Point=[number,number];
export interface CanonicalMap {
  schemaVersion:number;id:string;sourceSha256:string;nativeSize:Point;
  source:{inventoryNumber:string;series:string;title:string;manifestPath:string;canvasId:string;
    imageService:{id:string;type:'ImageService3';width:number;height:number};metadata:unknown[]};
  mask:{resourceMask:Point[];reviewStatus:string};
  points:{id:string;role:string;resourceCoords:Point;rdNew:Point;geo:Point;originalProjected:unknown;
    evidenceId:string;coordinateDerivation:unknown}[];
  adjustment:{linear:[Point,Point];intercept:Point;rmsPixels:number};
  quality:{status:string;reasons:string[];releaseEligible:boolean};
  [key:string]:unknown;
}
const root=fileURLToPath(new URL('../../',import.meta.url));
const data=resolve(root,'data/georeferencing/nieuwe-stijl');
const publicData='georeferencing/nieuwe-stijl/';
export const contextPath='contexts/river-maps-georeferencing.json';
const vocabulary=defaultBaseUrl+contextPath+'#';
export const extensionContext={'@context':{
  rm:vocabulary,
  ...Object.fromEntries(['originalProjected','rdNew','coordinateDerivation','quality'].map(key=>[
    `rm:${key}`,{'@id':vocabulary+key,'@type':'@json'}])),
  'rm:pointId':vocabulary+'pointId','rm:evidenceId':vocabulary+'evidenceId'
}};
export async function loadCanonicalMaps():Promise<CanonicalMap[]> {
  const names=(await readdir(resolve(data,'maps'))).filter(n=>n.endsWith('.json')).sort();
  const maps:CanonicalMap[]=await Promise.all(names.map(async n=>JSON.parse(await readFile(resolve(data,'maps',n),'utf8'))));
  const approved=JSON.parse(await readFile(resolve(data,'geometry-review.json'),'utf8')).maps;
  for(const map of maps){
    const geometry={resourceMask:map.mask.resourceMask,points:map.points.map(p=>({
      id:p.id,role:p.role,resourceCoords:p.resourceCoords,rdNew:p.rdNew,geo:p.geo,originalProjected:p.originalProjected}))};
    if(map.quality.releaseEligible&&JSON.stringify(geometry)!==JSON.stringify(approved[map.id]))throw new Error(`Geometry review is stale: ${map.id}`);
  }
  return maps;
}
export function mapForExport(map:CanonicalMap,base=defaultBaseUrl):GeoreferencedMap {
  base=normalizeBaseUrl(base);
  const canvas=base+map.source.manifestPath+'#'+map.source.canvasId.split('#')[1];
  return {type:'GeoreferencedMap',id:base+'annotations/nieuwe-stijl/maps/'+map.id,
    resource:{...map.source.imageService,partOf:[{id:canvas,type:'Canvas',partOf:[{
      id:base+map.source.manifestPath,type:'Manifest'}]}]},
    resourceMask:map.mask.resourceMask,transformation:{type:'polynomial',options:{order:1}},
    gcps:map.points.filter(p=>p.role==='control').map(p=>({resource:p.resourceCoords,geo:p.geo}))};
}
export function annotationForMap(map:CanonicalMap,base=defaultBaseUrl) {
  base=normalizeBaseUrl(base);
  const annotation=generateAnnotation(mapForExport(map,base));
  if(annotation.type!=='Annotation')throw new Error('Expected one map annotation');
  const points=map.points.filter(p=>p.role==='control');
  annotation.body.features.forEach((feature,i)=>Object.assign(feature.properties,{
    'rm:pointId':points[i].id,'rm:originalProjected':points[i].originalProjected,
    'rm:rdNew':points[i].rdNew,'rm:evidenceId':points[i].evidenceId,
    'rm:coordinateDerivation':points[i].coordinateDerivation
  }));
  const result={...annotation,'@context':['http://iiif.io/api/extension/georef/1/context.json','http://iiif.io/api/presentation/3/context.json',base+contextPath],
    label:{nl:[`${map.source.inventoryNumber}: ${map.source.title}`]},
    'rm:quality':map.quality,
    seeAlso:[{id:base+publicData+'maps/'+map.id+'.json',type:'Dataset',format:'application/json',
              label:{en:['Canonical RD observations, evidence and quality report']}}]};
  const parsed=parseAnnotation(result)[0];
  if(JSON.stringify(parsed.resourceMask)!==JSON.stringify(map.mask.resourceMask) ||
     JSON.stringify(parsed.gcps)!==JSON.stringify(mapForExport(map,base).gcps))throw new Error('Allmaps round-trip changed geometry');
  if(/viewBox|transform=/.test(result.target.selector.value))throw new Error('Invalid selector');
  return result;
}
export function generatePages(maps:CanonicalMap[],base=defaultBaseUrl,includeDrafts=false) {
  base=normalizeBaseUrl(base);
  const groups=new Map<string,CanonicalMap[]>();
  for(const map of maps){
    if(map.source.series==='D.01')throw new Error('Sheet indices cannot be georeferenced');
    if(!includeDrafts&&!map.quality.releaseEligible)continue;
    const path=`annotations/nieuwe-stijl/series-${map.source.series.slice(2)}.json`;
    groups.set(path,[...(groups.get(path)??[]),map]);
  }
  return new Map([...groups].map(([path,values])=>{
    const page={id:base+path,type:'AnnotationPage' as const,'@context':'http://www.w3.org/ns/anno.jsonld',
      label:{en:[includeDrafts?'Pilot candidates — includes maps needing review':'Pilot georeferencing — provisional quality screen passed']},
      items:values.sort((a,b)=>Number(a.source.inventoryNumber)-Number(b.source.inventoryNumber)).map(m=>annotationForMap(m,base))};
    parseAnnotation(page);return [path,page];
  }));
}
export async function georeferenceDocuments(base:string) {
  base=normalizeBaseUrl(base);
  const maps=await loadCanonicalMaps();
  const snapshot=await readFile(resolve(root,'data/nationaal-archief/nieuwe-stijl.json'));
  const {createHash}=await import('node:crypto');
  const hash=createHash('sha256').update(snapshot).digest('hex');
  if(maps.length!==24||maps.some(m=>m.sourceSha256!==hash))throw new Error('Pilot/source snapshot mismatch');
  const pages=generatePages(maps,base);
  const files=new Map<string,unknown>(pages);
  files.set(contextPath,extensionContext);
  for(const name of ['projection.json','config.json','pilot-report.json','coverage.json','evidence.json','attach-report.json','viewer-report.json','projection-checks.json','geometry-review.json']){
    files.set(publicData+name,JSON.parse(await readFile(resolve(data,name),'utf8')));
  }
  // Publish provenance for every pilot result, including the unreleased candidates.
  for(const map of maps) {
    const rebased=structuredClone(map);
    rebased.source.canvasId=base+map.source.manifestPath+'#'+map.source.canvasId.split('#')[1];
    files.set(publicData+'maps/'+map.id+'.json',rebased);
  }
  return {files,pages,maps};
}
export const mercator=([lon,lat]:Point):Point=>[6378137*lon*Math.PI/180,6378137*Math.log(Math.tan(Math.PI/4+lat*Math.PI/360))];
export function viewerComparison(map:CanonicalMap,samples:{resource:Point;geo:Point}[]) {
  const controls=map.points.filter(p=>p.role==='control');
  const transformer=new GcpTransformer(controls.map(p=>({resource:p.resourceCoords,geo:mercator(p.geo)})),'polynomial1');
  const degrees=new GcpTransformer(controls.map(p=>({resource:p.resourceCoords,geo:p.geo})),'polynomial1');
  function errors(geographic:boolean){return samples.map(s=>{
    const expected=mercator(s.geo);
    const actual=geographic?mercator(degrees.transformToGeo(s.resource)):transformer.transformToGeo(s.resource);
    return Math.hypot(actual[0]-expected[0],actual[1]-expected[1])*Math.cos(s.geo[1]*Math.PI/180);
  });}
  const m=errors(false),d=errors(true);
  return {inventoryNumber:map.source.inventoryNumber,sampleCount:samples.length,
    mercatorMaxGroundMetres:Math.max(...m),mercatorRmsGroundMetres:Math.sqrt(m.reduce((s,x)=>s+x*x,0)/m.length),
    lonLatMaxGroundMetres:Math.max(...d),
    method:'Allmaps polynomial1, EPSG:3857 and unprojected lon/lat fits versus inverse authoritative RD affine followed by pinned PROJ. Mercator distances multiplied by local cos(latitude).'};
}
export async function exportPilot() {
  const maps=await loadCanonicalMaps();
  for(const drafts of [false,true]){
    const pages=generatePages(maps,defaultBaseUrl,drafts);
    const folder=resolve(root,drafts?'data/georeferencing/nieuwe-stijl/draft-annotations':'data/georeferencing/nieuwe-stijl/pilot-screen-annotations');
    const {rm}=await import('node:fs/promises');await rm(folder,{recursive:true,force:true});await mkdir(folder,{recursive:true});
    for(const [path,page] of pages)await writeFile(resolve(folder,path.split('/').at(-1)!),JSON.stringify(page,null,2)+'\n');
  }
  const samples=JSON.parse(await readFile(resolve(data,'viewer-samples.json'),'utf8'));
  const results=maps.map(m=>viewerComparison(m,samples[m.id]));
  await writeFile(resolve(data,'viewer-report.json'),JSON.stringify({results,
    limitation:'Numerical renderer-geometry check; not a screenshot/UI test or a guarantee that another viewer uses this projection/model.'},null,2)+'\n');
  console.log(`Exported ${maps.length} candidate annotations; ${maps.filter(m=>m.quality.releaseEligible).length} pass the provisional release screen.`);
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await exportPilot();
