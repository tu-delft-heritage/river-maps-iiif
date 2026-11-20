"""Build canonical pilot observations and review artifacts from the saved evidence."""
import hashlib
import math
from functools import reduce
import cv2
import numpy as np
from PIL import Image, ImageDraw
from .catalog import ROOT, DATA, CACHE, read, save, pilot_records
from .acquire import original_point
from .geometry import adjust, to_pixel, to_rd, predict_uncertainty, validate_mask, area
from .measure import refine_cross
from .projection import normalize_rd, convert, definition
from .labels import parse_grid_label

CONFIG={'version':1,'rmsPixelsLimit':2.0,'checkPixelsLimit':5.0,
        'sigmaPixels':2.0,'sigmaStatus':'assumed, not calibrated from independent repeated measurements',
        'minControlHullFraction':.20,'maxDesignCondition':1000,
        'statusMeaning':'pilot-pass is a provisional processing screen, not a ground-accuracy or statistical claim',
        'maxOverviewLongSide':2000,'maxDetailsPerMap':12,'maxDetailArea':1800000}


def evidence_for(number):
    work=CACHE/'work'/number
    values={x['corner']:x['evidence'] for x in read(work/'corners.json')}
    values['overview']=read(work/'overview.json')
    for p in sorted(work.glob('*.json')):
        value=read(p)
        if isinstance(value,dict) and value.get('kind') in ['detail','overview']:
            values[p.stem]=value
    # Verify the exact bytes consumed by CV and the reviewer.
    for ev in values.values():
        p=CACHE/'images'/(ev['id']+'.jpg')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=ev['sha256']:
            raise ValueError('Evidence checksum mismatch: '+ev['id'])
    return values


def mask_for(record,review,ev):
    candidate=read(CACHE/'work'/record['inventoryNumber']/'frame-candidate.json')
    frame=candidate['resourceFrame']
    if 'frameCorners' in review:
        frame=[original_point(p,ev[c]) for p,c in zip(review['frameCorners'],['tl','tr','br','bl'])]
    for index,p in review.get('frameNativeOverrides',{}).items():frame[int(index)]=p
    tl,tr,br,bl=[np.array(p,float) for p in frame]
    # Shift the boundary slightly inwards to exclude the printed neatline itself.
    centre=np.mean(frame,axis=0)
    tl,tr,br,bl=[p+2*(centre-p)/np.linalg.norm(centre-p) for p in [tl,tr,br,bl]]
    mask=[tl.tolist(),tr.tolist(),br.tolist()]
    if 'bottomTableNotchOverview' in review:
        left,right,top=review['bottomTableNotchOverview']
        left,top=original_point([left,top],ev['overview'])
        right,_=original_point([right,0],ev['overview'])
        def bottom_y(x):return bl[1]+(br[1]-bl[1])*(x-bl[0])/(br[0]-bl[0])
        mask += [[right,bottom_y(right)],[right,top],[left,top],[left,bottom_y(left)]]
    if 'titleNotch' in review:
        corner,x,y=review['titleNotch'];x,y=original_point([x,y],ev[corner])
        # Small conservative margin around the title text / box.
        if corner=='br':
            y-=3
            mask=[tl.tolist(),tr.tolist(),[br[0],y],[x-3,y],[x-3,br[1]],bl.tolist()]
        elif corner=='bl':
            y-=3
            mask += [[x+3,bl[1]],[x+3,y],[bl[0],y]]
        elif corner=='tr':
            y+=3
            top=tl[1]+(tr[1]-tl[1])*(x-3-tl[0])/(tr[0]-tl[0])
            mask=[tl.tolist(),[x-3,top],[x-3,y],[tr[0],y],br.tolist(),bl.tolist()]
        elif corner=='tl':
            y+=3
            top=tl[1]+(tr[1]-tl[1])*(x+3-tl[0])/(tr[0]-tl[0])
            mask=[[tl[0],y],[x+3,y],[x+3,top],tr.tolist(),br.tolist(),bl.tolist()]
        else:raise ValueError('Unknown title corner: '+corner)
    elif 'leftTableNotchOverview' in review:
        x,y=original_point(review['leftTableNotchOverview'],ev['overview'])
        mask += [[x,bl[1]],[x,y],[bl[0],y]]
    else:mask.append(bl.tolist())
    if 'sideTitleNotch' in review:
        if any(k in review for k in ['titleNotch','bottomTableNotchOverview','leftTableNotchOverview']):
            raise ValueError('Side title notch cannot be combined with another notch')
        notch=review['sideTitleNotch'];side=notch['side'];key=notch['evidenceKey']
        left,top=original_point(notch['bounds'][:2],ev[key])
        right,bottom=original_point(notch['bounds'][2:],ev[key]);top-=3;bottom+=3
        if not max(tl[1],tr[1])<top<bottom<min(bl[1],br[1]):
            raise ValueError('Side title must lie between top and bottom frame edges')
        if side=='left':
            x=right+3
            def edge_x(y):return tl[0]+(bl[0]-tl[0])*(y-tl[1])/(bl[1]-tl[1])
            mask=[tl.tolist(),tr.tolist(),br.tolist(),bl.tolist(),
                  [edge_x(bottom),bottom],[x,bottom],[x,top],[edge_x(top),top]]
        elif side=='right':
            x=left-3
            def edge_x(y):return tr[0]+(br[0]-tr[0])*(y-tr[1])/(br[1]-tr[1])
            mask=[tl.tolist(),tr.tolist(),[edge_x(top),top],[x,top],
                  [x,bottom],[edge_x(bottom),bottom],br.tolist(),bl.tolist()]
        else:raise ValueError('Unknown title side: '+side)
    if 'topLeftCaptionNotch' in review:
        x,y=original_point(review['topLeftCaptionNotch'],ev['tl']);x+=3;y+=3
        def top_y(z):return tl[1]+(tr[1]-tl[1])*(z-tl[0])/(tr[0]-tl[0])
        # Extend an existing top-left title notch only where its caption is wider.
        index=2 if review.get('titleNotch',[None])[0]=='tl' else 0
        edge=mask[index]
        if not edge[0]<x<tr[0] or not top_y(x)<y<bl[1]:
            raise ValueError('Caption notch must meet the top-left map edge')
        if index and y>=mask[index-1][1]:raise ValueError('Caption must sit above the title bottom')
        mask[index:index+1]=[[edge[0],y],[x,y],[x,top_y(x)]]
    if 'topRightCaptionNotch' in review:
        if review.get('titleNotch',[None])[0]=='tr':
            raise ValueError('Top-right caption and title require one combined notch')
        x,y=original_point(review['topRightCaptionNotch'],ev['tr']);x-=3;y+=3
        top=tl[1]+(tr[1]-tl[1])*(x-tl[0])/(tr[0]-tl[0])
        right=tr[0]+(br[0]-tr[0])*(y-tr[1])/(br[1]-tr[1])
        if not tl[0]<x<tr[0] or not top<y<br[1]:
            raise ValueError('Caption notch must meet the top-right map edge')
        index=next(i for i,p in enumerate(mask) if np.allclose(p,tr))
        mask[index:index+1]=[[x,top],[x,y],[right,y]]
    validate_mask(mask,[record['imageService']['width'],record['imageService']['height']])
    return {'resourceMask':mask,'candidateFrame':candidate['resourceFrame'],'reviewedFrame':frame,
            'method':'Canny/Hough overview proposal; saved native detail visual corrections and conservative concave notches',
            'edgeKinds':['scan-crop-edge' if record['inventoryNumber'] in ['947','948'] else 'printed-inner-frame',
                         'title-or-table-notch'],
            'tablePolicy':'Internal tables removed with a notch to the nearest blank edge; no holes or disconnected polygons.',
            'reviewStatus':'ai-visually-reviewed'}


def render_review(record,canonical,evidence,review):
    n=record['inventoryNumber'];work=CACHE/'review';work.mkdir(parents=True,exist_ok=True)
    ev=evidence['overview'];im=Image.open(CACHE/'images'/(ev['id']+'.jpg')).convert('RGB')
    sx=ev['decodedSize'][0]/ev['region'][2];sy=ev['decodedSize'][1]/ev['region'][3]
    d=ImageDraw.Draw(im)
    vertices=[(x*sx,y*sy) for x,y in canonical['mask']['resourceMask']]
    d.line(vertices+[vertices[0]],fill='red',width=2)
    for i,(x,y) in enumerate(vertices):d.text((x+4,y+3),str(i+1),fill='red')
    for p in canonical['points']:
        x,y=p['resourceCoords'];x*=sx;y*=sy;color='blue' if p['role']=='check' else 'lime'
        d.ellipse((x-5,y-5,x+5,y+5),outline=color,width=2);d.text((x+8,y),p['id'],fill=color)
    im.save(work/(n+'-mask.jpg'))
    tiles=Image.new('RGB',(250*len(canonical['points']),310),'white');draw=ImageDraw.Draw(tiles)
    for i,(p,seed) in enumerate(zip(canonical['points'],review['points'])):
        e=evidence[seed[0]];source=Image.open(CACHE/'images'/(e['id']+'.jpg')).convert('RGB')
        x,y=seed[1:3];crop=source.crop((x-25,y-25,x+26,y+26)).resize((204,204))
        cd=ImageDraw.Draw(crop)
        q=p['localization']['candidate'] if p['localization']['accepted'] else [x,y]
        cx=(q[0]-x+25)*4;cy=(q[1]-y+25)*4
        cd.ellipse((cx-5,cy-5,cx+5,cy+5),outline='red',width=1)
        tiles.paste(crop,(250*i+20,25));draw.text((250*i+10,240),n+' '+p['id']+' '+p['role'],fill='black')
        draw.text((250*i+10,260),str(p['originalProjected']['coordinates']),fill='black')
    tiles.save(work/(n+'-controls.jpg'))


def reviewed_label_value(text, review):
    """Use an explicit visual interpretation only when the printed separator is absent."""
    override=review.get("labelInterpretations",{}).get(text)
    return override["metres"] if override is not None else parse_grid_label(text,review.get("printedUnit","metre"))


def coordinate_dependencies(review, raw_pair, evidence):
    """Describe integer steps from reviewed border values, never use OCR to assign them."""
    explicit=[a for a in review.get('pointBorderAnchors',[]) if a['coordinates']==list(raw_pair)]
    if explicit:
        if len(explicit)!=1:raise ValueError('Duplicate explicit point anchors')
        entry=explicit[0];interval=entry['gridIntervalMetres'];result=[]
        if interval<=0 or [a['axis'] for a in entry['axes']]!=['easting','northing']:
            raise ValueError('Invalid explicit border axes')
        for axis,a in enumerate(entry['axes']):
            key,text=a['evidenceKey'],a['borderText']
            if text not in review['labels'][key]:raise ValueError('Explicit anchor lacks a reviewed label')
            value=reviewed_label_value(text,review);steps=a['signedSteps']
            if not float(steps).is_integer() or value+steps*interval!=raw_pair[axis]:
                raise ValueError('Explicit anchor disagrees with assigned coordinate')
            result.append({'axis':a['axis'],'borderText':text,'borderValueMetres':value,
                'evidenceId':evidence[key]['id'],'gridIntervalMetres':interval,'signedSteps':steps,
                'resultMetres':raw_pair[axis],
                'method':'explicitly reviewed axis and border location: '+a['borderLocation']})
        return result
    pairs=np.array([p[3:5] for p in review['points']])
    centre=pairs.mean(axis=0)
    anchors=[[],[]]
    for corner,labels in review['labels'].items():
        for text in labels:
            value=reviewed_label_value(text,review)
            axis=int(np.argmin(np.abs(centre-value)))
            anchors[axis].append((value,text,corner))
    external={a["axis"]:a for a in review.get("externalBorderAnchors",[])}
    for axis,name in enumerate(["easting","northing"]):
        if not anchors[axis] and name in external:
            a=external[name]
            if parse_grid_label(a["verbatim"],a["printedUnit"])!=a["valueMetres"]:
                raise ValueError('External border value disagrees with printed label')
            if not a.get("sourceInventoryNumber") or not a.get("evidence",{}).get("id") or not a.get("method"):
                raise ValueError('External border anchor requires source, evidence and review method')
            anchors[axis].append((a["valueMetres"],a["verbatim"],None))
        if not anchors[axis]:raise ValueError('Missing reviewed '+name+' border anchor')
    differences=[]
    for axis in [0,1]:
        values=sorted(set([int(p[axis]) for p in pairs]+[int(v[0]) for v in anchors[axis]]))
        differences += [b-a for a,b in zip(values,values[1:]) if b>a]
    interval=reduce(math.gcd,differences)
    if interval<=0:raise ValueError('Cannot establish grid interval')
    result=[]
    for axis in [0,1]:
        value,text,corner=min(anchors[axis],key=lambda a:abs(a[0]-raw_pair[axis]))
        steps=(raw_pair[axis]-value)/interval
        if not float(steps).is_integer():raise ValueError('Inconsistent verified grid steps')
        result.append({'axis':['easting','northing'][axis],'borderText':text,'borderValueMetres':value,
            'evidenceId':evidence[corner]['id'] if corner is not None else external[['easting','northing'][axis]]['evidence']['id'],'gridIntervalMetres':interval,'signedSteps':int(steps),
            'resultMetres':raw_pair[axis],
            'method':'value read on border and cross associated by grid direction' if steps==0 else 'integer intervals traced from a reviewed border value'})
        if corner is None:
            a=external[["easting","northing"][axis]]
            result[-1].update(method=a["method"],sourceInventoryNumber=a["sourceInventoryNumber"],externalAnchor=True)
    return result


def geometry_snapshot(mask,points):
    return {'resourceMask':mask['resourceMask'],
            'points':[{k:p[k] for k in ['id','role','resourceCoords','rdNew','geo','originalProjected']} for p in points]}


def run_pilot():
    reviews=read(DATA/'reviews.json');selection=read(DATA/'selection.json')
    approved=read(DATA/'geometry-review.json')['maps']
    rows=[];all_evidence={};viewer_samples={}
    save(DATA/'config.json',CONFIG);save(DATA/'projection.json',definition())
    for record in pilot_records():
        n=record['inventoryNumber'];review=reviews['maps'][n];ev=evidence_for(n)
        raw=[p[3:5] for p in review['points']]
        rd=[normalize_rd(p,review['crs']) for p in raw]
        seeds=[original_point(p[1:3],ev[p[0]]) for p in review['points']]
        control=[i for i,p in enumerate(review['points']) if len(p)==5 or p[5]!='check']
        check=[i for i in range(len(raw)) if i not in control]
        initial=adjust([rd[i] for i in control],[seeds[i] for i in control])
        directions=np.asarray(initial['linear']).T
        points=[]
        for i,p in enumerate(review['points']):
            evidence=ev[p[0]]
            image=cv2.imread(str(CACHE/'images'/(evidence['id']+'.jpg')))
            local,localization=refine_cross(image,p[1:3],directions)
            resource=original_point(local,evidence)
            points.append({'id':'p'+str(i+1),'role':'control' if i in control else 'check',
                'resourceCoords':resource,'reviewedSeedResourceCoords':seeds[i],
                'originalProjected':{'crs':review['crs'],'coordinates':raw[i],'unit':'metre',
                                     'printedUnit':review.get('printedUnit','metre')},
                'rdNew':rd[i],'geo':convert(rd[i]),'evidenceId':evidence['id'],
                'resourceFromEvidence':[[evidence['region'][2]/evidence['decodedSize'][0],0,evidence['region'][0]],
                                        [0,evidence['region'][3]/evidence['decodedSize'][1],evidence['region'][1]]],
                'coordinateDerivation':{'method':'border-label and verified grid-interval tracing','axes':coordinate_dependencies(review,raw[i],ev),
                  'anchorIds':[n+'-'+c for c in review['labels']]+[n+'-external-'+a['axis'] for a in review.get('externalBorderAnchors',[])],
                  'sharedAnchorWarning':'Controls and checks share border anchors; checks test geometry, not independent protection against a uniform grid-origin error.'},
                'sigmaPixels':2.0,'uncertaintyStatus':'assumed','localization':localization,
                'visualReview':'accepted source cross and coordinate assignment by Codex vision'})
        fit=adjust([rd[i] for i in control],[points[i]['resourceCoords'] for i in control])
        fit['heldOutChecks']=[]
        for i in check:
            residual=np.array(points[i]['resourceCoords'])-to_pixel(fit,rd[i])
            fit['heldOutChecks'].append({'pointId':points[i]['id'],'residualPixels':residual.tolist(),
                'errorPixels':float(np.linalg.norm(residual)),
                'errorMetres':float(np.linalg.norm(residual@np.linalg.inv(fit['linear']).T)),
                'usedInFit':False})
        mask=mask_for(record,review,ev)
        hull=cv2.convexHull(np.array([points[i]['resourceCoords'] for i in control],np.float32))
        fit['controlHullFraction']=abs(float(cv2.contourArea(hull)))/area(mask['resourceMask'])
        fit['maskVertexPredictedSigmaPixels']=[predict_uncertainty(fit,p) for p in to_rd(fit,mask['resourceMask'])]
        reasons=[]
        if fit['rmsPixels']>CONFIG['rmsPixelsLimit']:reasons.append('rms-above-2px')
        if not check:reasons.append('no-held-out-check')
        if any(p['errorPixels']>CONFIG['checkPixelsLimit'] for p in fit['heldOutChecks']):reasons.append('check-above-5px')
        if fit['controlHullFraction']<CONFIG['minControlHullFraction']:reasons.append('poor-control-coverage')
        if approved.get(record['id'])!=geometry_snapshot(mask,points):
            reasons.append('geometry-review-required')
            mask['reviewStatus']='needs-review'
        status='needs-review' if reasons else 'pilot-pass'
        for p in points:
            if cv2.pointPolygonTest(np.asarray(mask['resourceMask'],np.float32),tuple(p['resourceCoords']),False)<0:
                reasons.append('point-outside-mask');status='needs-review'
        anchors=[{'id':n+'-'+c,'evidenceId':ev[c]['id'],'verbatimLabels':labels,'parsedMetres':[parse_grid_label(label,review.get('printedUnit','metre')) for label in labels],
                  'unit':review.get('printedUnit','metre'),'readingMethod':'vision, original native-resolution evidence',
                  'coordinateSystem':review['crs']} for c,labels in review['labels'].items()]
        canonical={'schemaVersion':1,'id':record['id'],'source':record,
            'sourceSha256':selection['sourceSha256'],'eadSha256':selection['eadSha256'],
            'nativeSize':[record['imageService']['width'],record['imageService']['height']],
            'mask':mask,'anchors':anchors,'points':points,'adjustment':fit,
            'conversion':'../projection.json','evidence':list({e['id']:e for e in ev.values()}.values()),
            'quality':{'status':status,'reasons':reasons,'config':'../config.json','releaseEligible':status=='pilot-pass'},
            'review':{'reviewer':reviews['reviewer'],'date':'2026-11-19','type':'AI visual review; not an independent human survey',
                      'notes':review['notes'],'corrections':review.get('corrections',[])}}
        save(DATA/'maps'/(record['id']+'.json'),canonical)
        polygon=np.asarray(mask['resourceMask'],np.float32)
        lo,hi=polygon.min(axis=0),polygon.max(axis=0)
        samples=[]
        for y in np.linspace(lo[1],hi[1],13):
            for x in np.linspace(lo[0],hi[0],19):
                if cv2.pointPolygonTest(polygon,(float(x),float(y)),False)>=0:
                    resource=[float(x),float(y)]
                    samples.append({'resource':resource,'geo':convert(to_rd(fit,resource))})
        viewer_samples[record['id']]=samples
        render_review(record,canonical,ev,review)
        rows.append({'inventoryNumber':n,'mapId':record['id'],'series':record['series'],'status':status,
                     'reasons':reasons,'rmsPixels':fit['rmsPixels'],'rmsMetres':fit['rmsMetres'],
                     'maxCheckPixels':max([p['errorPixels'] for p in fit['heldOutChecks']],default=None),
                     'controlHullFraction':fit['controlHullFraction'],'originalCrs':review['crs']})
        all_evidence.update({e['id']:e for e in ev.values()})
        print(n,status,round(fit['rmsPixels'],3),round(rows[-1]['maxCheckPixels'],3),flush=True)
    coverage=[{'id':r['id'],'inventoryNumber':r['inventoryNumber'],
               'status':next((a['status'] for a in rows if a['mapId']==r['id']),'not-in-pilot')} for r in selection['records']]
    save(DATA/'coverage.json',{'selectedMaps':999,'excludedIndices':selection['excluded'],'records':coverage})
    evidence=list(all_evidence.values())
    save(DATA/'evidence.json',{'items':evidence,'uniqueRequests':len(evidence),'bytes':sum(e['bytes'] for e in evidence),
                             'offlineRunNetworkRequests':0})
    report={'pilotScans':len(rows),'passed':sum(r['status']=='pilot-pass' for r in rows),
            'needsReview':sum(r['status']=='needs-review' for r in rows),'notInPilot':975,
            'excludedIndices':10,'results':rows,'qualityLimits':CONFIG,
            'limitations':['Pixel sigma is assumed; no calibrated statistical-pass claim.',
              'Held-out crosses share some border anchors with controls.',
              'One-metre datum-operation accuracy is separate from image fit and historical map accuracy.',
              'Only the 24-scan pilot has been measured; 975 selected maps remain unprocessed.']}
    save(DATA/'pilot-report.json',report)
    save(DATA/'viewer-samples.json',viewer_samples)
    return report
