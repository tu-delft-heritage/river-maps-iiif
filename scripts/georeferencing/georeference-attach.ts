import { readFile, writeFile } from 'node:fs/promises';
import { AttachedTransformation, type Attachment } from '@allmaps/attach';
import { Polynomial1 } from '@allmaps/transform';
import type { CanonicalMap, Point } from './georeference-export.ts';
const root = new URL('../../data/georeferencing/nieuwe-stijl/', import.meta.url);
const input = JSON.parse(await readFile(new URL('tie-candidates.json', root), 'utf8')) as {
  ties: { id: string; role: string; mapIds: string[]; resourceCoords: Point[]; visualReview: string }[];
};
if (input.ties.some(t => t.visualReview !== 'accepted')) throw new Error('Tie evidence still needs visual review');
const ids = input.ties[0].mapIds;
const maps: CanonicalMap[] = await Promise.all(ids.map(async id => JSON.parse(await readFile(new URL(`maps/${id}.json`, root), 'utf8'))));
const normalize = ([x,y]: Point): Point => [(x-4000)/1000, (y-2500)/1000];
const independent = new Map(maps.map(map => [map.id, new Polynomial1(
  map.points.filter(p=>p.role==='control').map(p=>normalize(p.resourceCoords)),
  map.points.filter(p=>p.role==='control').map(p=>p.rdNew))]));
const attachments: Attachment[] = input.ties.filter(t=>t.role==='fit').map(t=>[
  { id:t.id, transformationId:ids[0], source:normalize(t.resourceCoords[0]) },
  { id:t.id, transformationId:ids[1], source:normalize(t.resourceCoords[1]) }
]);
const options = { clone:true, averageOut:false, evaluateAttachmentScps:true,
  evaluateSingleScps:false, evaluateGcps:false, removeExistingGcps:false, useMapTransformationTypes:false };
const attached = new AttachedTransformation(independent, attachments, options);
attached.solve();
const distance = (a: Point,b: Point) => Math.hypot(a[0]-b[0],a[1]-b[1]);
const baseline = (map: CanonicalMap, p: Point): Point => {
  const [[a,b],[c,d]]=map.adjustment.linear; const [x,y]=p.map((v,i)=>v-map.adjustment.intercept[i]);
  const det=a*d-b*c;return [(d*x-b*y)/det,(-c*x+a*y)/det];
};
const evaluate = (p: Point,id: string): Point => attached.evaluateFunction(normalize(p),id);
const ties = input.ties.map(t=>({id:t.id,role:t.role,
  beforeMetres:distance(baseline(maps[0],t.resourceCoords[0]),baseline(maps[1],t.resourceCoords[1])),
  independentPackageMetres:distance(independent.get(ids[0])!.evaluateFunction(normalize(t.resourceCoords[0])),independent.get(ids[1])!.evaluateFunction(normalize(t.resourceCoords[1]))),
  afterMetres:distance(evaluate(t.resourceCoords[0],ids[0]),evaluate(t.resourceCoords[1],ids[1]))
}));
const rms=(values:number[])=>Math.sqrt(values.reduce((s,v)=>s+v*v,0)/values.length);
const errors=maps.map(map=>({inventoryNumber:map.source.inventoryNumber,
  controls:map.points.filter(p=>p.role==='control').map(p=>({id:p.id,
    beforeMetres:distance(baseline(map,p.resourceCoords),p.rdNew),
    afterMetres:distance(evaluate(p.resourceCoords,map.id),p.rdNew),
    displacementMetres:distance(baseline(map,p.resourceCoords),evaluate(p.resourceCoords,map.id))})),
  checks:map.points.filter(p=>p.role==='check').map(p=>({id:p.id,
    beforeMetres:distance(baseline(map,p.resourceCoords),p.rdNew),
    afterMetres:distance(evaluate(p.resourceCoords,map.id),p.rdNew)}))
}));
const held=ties.filter(t=>t.role==='check');
const report={ package:'@allmaps/attach@1.0.0-beta.51', options,
  solver:'Joint first-order polynomial image-to-RD fit; equal weights in RD metres. Native resource pixels centred/scaled for conditioning.',
  baseline:'Independent weighted affine RD-to-image fits, inverted; also report package inverse-fit baseline.',
  trainingTieCount:3,heldOutTieCount:3,heldOutTieRmsBeforeMetres:rms(held.map(t=>t.beforeMetres)),
  heldOutTieRmsAfterMetres:rms(held.map(t=>t.afterMetres)),ties,gridErrors:errors,
  conclusion:'Experimental only. Relative overlap consistency is not absolute accuracy; preserve original RD observations and baseline annotations. No automatic promotion.',
  limitations:['Three tie equations plus eight absolute controls, all equal-weight; no calibrated joint covariance.',
    'Both images depict the same sheet. Repeated features are correlated, not independent surveyed points.',
    'No averaging of destinations to conceal attachment disagreement; evaluate the solved transforms directly.',
    'Only this same-sheet pair was evaluated. Transfer to different dates/sheets is untested.']};
await writeFile(new URL('attach-report.json',root),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({heldOutBefore:report.heldOutTieRmsBeforeMetres,heldOutAfter:report.heldOutTieRmsAfterMetres,gridErrors:errors},null,2));
