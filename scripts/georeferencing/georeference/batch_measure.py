"""Offline batch measurement; shares the pilot's localization, projection and QA limits."""
from datetime import datetime,timezone
import cv2
import numpy as np
from .catalog import DATA,CACHE,read,save
from .batch import batch_dir,validate_selection
from .pilot import CONFIG,evidence_for,mask_for,render_review,coordinate_dependencies,geometry_snapshot,reviewed_label_value
from .acquire import original_point
from .geometry import adjust,to_pixel,to_rd,area,predict_uncertainty
from .measure import refine_cross
from .projection import normalize_rd,convert,definition
from .labels import parse_grid_label


def measure_batch(name):
    folder=batch_dir(name);selection=read(folder/'selection.json');reviews=read(folder/'reviews.json')
    records=validate_selection(selection)
    missing=[r['inventoryNumber'] for r in records if r['inventoryNumber'] not in reviews['maps']]
    if missing:raise ValueError('Missing reviewed observations: '+', '.join(missing))
    approved=read(folder/'geometry-review.json')['maps'] if (folder/'geometry-review.json').exists() else {}
    rows=[];all_evidence={};samples={}
    save(folder/'config.json',CONFIG);save(folder/'projection.json',definition())
    for record in records:
        n=record['inventoryNumber']
        review=reviews['maps'][n];ev=evidence_for(n);raw=[p[3:5] for p in review['points']]
        rd=[normalize_rd(p,review['crs']) for p in raw]
        seeds=[original_point(p[1:3],ev[p[0]]) for p in review['points']]
        control=[i for i,p in enumerate(review['points']) if len(p)==5 or p[5]!='check'];check=[i for i in range(len(raw)) if i not in control]
        if len(control)<4 or not check:raise ValueError(n+': four controls and a check required')
        initial=adjust([rd[i] for i in control],[seeds[i] for i in control]);directions=np.asarray(initial['linear']).T;points=[]
        for i,p in enumerate(review['points']):
            e=ev[p[0]];im=cv2.imread(str(CACHE/'images'/(e['id']+'.jpg')))
            local,localization=refine_cross(im,p[1:3],directions);resource=original_point(local,e)
            points.append({'id':'p'+str(i+1),'role':'control' if i in control else 'check','resourceCoords':resource,
                'reviewedSeedResourceCoords':seeds[i],
                'originalProjected':{'crs':review['crs'],'coordinates':raw[i],'unit':'metre','printedUnit':review.get('printedUnit','metre')},
                'rdNew':rd[i],'geo':convert(rd[i]),'evidenceId':e['id'],
                'resourceFromEvidence':[[e['region'][2]/e['decodedSize'][0],0,e['region'][0]],[0,e['region'][3]/e['decodedSize'][1],e['region'][1]]],
                'coordinateDerivation':{'method':'border-label and verified grid-interval tracing','axes':coordinate_dependencies(review,raw[i],ev),
                    'anchorIds':[n+'-'+c for c in review['labels']]+[n+'-external-'+a['axis'] for a in review.get('externalBorderAnchors',[])],
                    'sharedAnchorWarning':'Controls and checks share border anchors; checks test geometry, not independent protection against a uniform grid-origin error.'},
                'sigmaPixels':2.0,'uncertaintyStatus':'assumed','localization':localization,
                'visualReview':'Source cross and coordinate assignment inspected by Codex vision; final geometry approval is separately recorded.'})
        fit=adjust([rd[i] for i in control],[points[i]['resourceCoords'] for i in control]);fit['heldOutChecks']=[]
        for i in check:
            residual=np.asarray(points[i]['resourceCoords'])-to_pixel(fit,rd[i])
            fit['heldOutChecks'].append({'pointId':points[i]['id'],'residualPixels':residual.tolist(),'errorPixels':float(np.linalg.norm(residual)),
                'errorMetres':float(np.linalg.norm(residual@np.linalg.inv(fit['linear']).T)),'usedInFit':False})
        mask=mask_for(record,review,ev)
        hull=cv2.convexHull(np.array([points[i]['resourceCoords'] for i in control],np.float32));fit['controlHullFraction']=abs(float(cv2.contourArea(hull)))/area(mask['resourceMask'])
        fit['maskVertexPredictedSigmaPixels']=[predict_uncertainty(fit,p) for p in to_rd(fit,mask['resourceMask'])]
        reasons=[]
        if fit['rmsPixels']>CONFIG['rmsPixelsLimit']:reasons.append('rms-above-2px')
        if any(p['errorPixels']>CONFIG['checkPixelsLimit'] for p in fit['heldOutChecks']):reasons.append('check-above-5px')
        if fit['controlHullFraction']<CONFIG['minControlHullFraction']:reasons.append('poor-control-coverage')
        if fit['condition']>CONFIG['maxDesignCondition']:reasons.append('ill-conditioned-controls')
        if approved.get(record['id'])!=geometry_snapshot(mask,points):reasons.append('geometry-review-required');mask['reviewStatus']='needs-review'
        for p in points:
            if cv2.pointPolygonTest(np.asarray(mask['resourceMask'],np.float32),tuple(p['resourceCoords']),False)<0:reasons.append('point-outside-mask')
        status='needs-review' if reasons else 'batch-pass'
        anchors=[{'id':n+'-'+c,'evidenceId':ev[c]['id'],'verbatimLabels':labels,'parsedMetres':[reviewed_label_value(label,review) for label in labels],
            'interpretations':{label:review['labelInterpretations'][label] for label in labels if label in review.get('labelInterpretations',{})},
            'unit':review.get('printedUnit','metre'),'readingMethod':'vision, native-resolution evidence','coordinateSystem':review['crs']} for c,labels in review['labels'].items()]
        for a in review.get('externalBorderAnchors',[]):
            e=a['evidence'];ev['external-'+a['sourceInventoryNumber']+'-'+a['axis']]=e
            anchors.append({'id':n+'-external-'+a['axis'],'evidenceId':e['id'],'verbatimLabels':[a['verbatim']],'parsedMetres':[a['valueMetres']],'unit':a['printedUnit'],'readingMethod':a['method'],'sourceInventoryNumber':a['sourceInventoryNumber'],'coordinateSystem':review['crs']})
        canonical={'schemaVersion':1,'id':record['id'],'batchId':name,'source':record,'sourceSha256':selection['sourceSha256'],'eadSha256':selection['eadSha256'],
            'nativeSize':[record['imageService']['width'],record['imageService']['height']],'mask':mask,'anchors':anchors,'points':points,'adjustment':fit,
            'conversion':'../projection.json','evidence':list({e['id']:e for e in ev.values()}.values()),
            'evidenceKeys':{key:e['id'] for key,e in ev.items()},
            'quality':{'status':status,'reasons':reasons,'config':'../config.json','releaseEligible':False,'humanReview':'pending'},
            'review':{'reviewer':reviews['reviewer'],'date':datetime.now(timezone.utc).date().isoformat(),'type':'AI visual review; not an independent human survey',
                'coordinateProvenance':review.get('coordinateProvenance'),'printedLabelAnomalies':review.get('printedLabelAnomalies',[]),
                'notes':review['notes'],'corrections':review.get('corrections',[]),'candidateRegistration':review.get('candidateRegistration')}}
        save(folder/'maps'/(record['id']+'.json'),canonical);render_review(record,canonical,ev,review)
        rows.append({'inventoryNumber':n,'mapId':record['id'],'series':record['series'],'status':status,'reasons':reasons,'rmsPixels':fit['rmsPixels'],'rmsMetres':fit['rmsMetres'],
            'maxCheckPixels':max(p['errorPixels'] for p in fit['heldOutChecks']),'controlHullFraction':fit['controlHullFraction'],'originalCrs':review['crs']})
        all_evidence.update({e['id']:e for e in ev.values()})
        polygon=np.asarray(mask['resourceMask'],np.float32);lo,hi=polygon.min(axis=0),polygon.max(axis=0)
        samples[record['id']]=[{'resource':[float(x),float(y)],'geo':convert(to_rd(fit,[x,y]))} for y in np.linspace(lo[1],hi[1],13) for x in np.linspace(lo[0],hi[0],19) if cv2.pointPolygonTest(polygon,(float(x),float(y)),False)>=0]
        print(n,status,round(fit['rmsPixels'],2),round(rows[-1]['maxCheckPixels'],2),flush=True)
    evidence=list(all_evidence.values());save(folder/'evidence.json',{'items':evidence,'uniqueRequests':len(evidence),'bytes':sum(e['bytes'] for e in evidence),'offlineMeasurementNetworkRequests':0})
    save(folder/'viewer-samples.json',samples)
    report={'batchId':name,'scans':len(rows),'selectedScans':len(selection['records']),'passed':sum(r['status']=='batch-pass' for r in rows),'needsReview':sum(r['status']=='needs-review' for r in rows),
        'humanReview':'pending','results':rows,'qualityLimits':CONFIG,'priorPilotFeedback':'User visually accepted all 24 pilot maps; numerical thresholds and assumed uncertainty remain unchanged.',
        'limitations':['Pixel sigma is assumed, not statistically calibrated.','Checks share border anchors with controls.','Datum operation accuracy and historical map accuracy are separate from fit residuals.','Repeat-edition registration proposes image positions only; no attach tie points enter the absolute fit.']}
    save(folder/'report.json',report);return report
