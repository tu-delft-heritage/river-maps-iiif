"""Batch selection and evidence acquisition, sharing the pilot's polite cache."""
import hashlib
import re
import cv2
from PIL import Image, ImageDraw
from .catalog import ROOT,DATA,CACHE,read,save
from .acquire import ImageCache,overview_request,region_request,original_point
from .prepare import frame_lines

def batch_dir(name):
    if not re.fullmatch(r'batch-\d{2}',name):raise ValueError('Expected batch-NN')
    return DATA/'batches'/name

def validate_selection(selection):
    """Reject stale snapshots, pilot/index leakage, duplicates and modified source records."""
    source=ROOT/'data/nationaal-archief/nieuwe-stijl.json'
    catalog=read(DATA/'selection.json')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=selection['sourceSha256'] or selection['sourceSha256']!=catalog['sourceSha256'] or selection['eadSha256']!=catalog['eadSha256']:
        raise ValueError('Batch/source snapshot mismatch')
    known={r['id']:r for r in catalog['records']}
    records=selection['records']
    count=selection.get('selectedCount',50)
    maximum=len(known) if selection.get('mode')=='whole-series' else 50
    if type(count) is not int or not 1<=count<=maximum or len(records)!=count or len({r['id'] for r in records})!=count:
        raise ValueError('Batch must contain its declared count of distinct scans within scope')
    for record in records:
        if record.get('pilot') or record['series']=='D.01' or known.get(record['id'])!=record:
            raise ValueError('Batch contains a pilot, index or modified source record')
        if selection.get('series') and record['series']!=selection['series']:
            raise ValueError('Record is outside the selected series')
    if selection.get('mode')=='whole-series':
        if not selection.get('series'):raise ValueError('Whole-series batches require a series')
        prior={r['id'] for r in catalog['records'] if r['pilot']}
        for path in (DATA/'batches').glob('*/selection.json'):
            if path.parent.name<selection['batchId']:prior.update(r['id'] for r in read(path)['records'])
        expected=[r for r in catalog['records'] if r['series']==selection['series'] and r['id'] not in prior]
        if records!=expected:raise ValueError('Whole-series selection is incomplete or out of source order')
    return records

def select_batch(name,series=None,limit=None):
    if limit is not None and (type(limit) is not int or not 1<=limit<=50):raise ValueError('Batch size must be between 1 and 50')
    folder=batch_dir(name)
    if (folder/'selection.json').exists():
        selection=read(folder/'selection.json');validate_selection(selection)
        if series and selection.get('series')!=series:raise ValueError('Saved batch has a different series scope')
        return selection
    selection=read(DATA/'selection.json')
    source=ROOT/'data/nationaal-archief/nieuwe-stijl.json'
    if hashlib.sha256(source.read_bytes()).hexdigest()!=selection['sourceSha256']:
        raise ValueError('Source snapshot changed')
    used={r['id'] for r in selection['records'] if r['pilot']}
    for path in (DATA/'batches').glob('*/selection.json'):
        used.update(r['id'] for r in read(path)['records'])
    eligible=[r for r in selection['records'] if r['id'] not in used]
    if not series and limit is None and eligible:series=eligible[0]['series']
    records=[r for r in eligible if not series or r['series']==series][:limit]
    if not records or any(r['series']=='D.01' for r in records):raise ValueError('No eligible maps in scope')
    value={'schemaVersion':1,'batchId':name,'sourceSha256':selection['sourceSha256'],
           'eadSha256':selection['eadSha256'],'selectedCount':len(records),'series':series,'requestedLimit':limit,'mode':'whole-series' if limit is None else 'limited',
           'selectionRule':'Next unprocessed digitized maps within scope, in saved archival source order; exclude pilot and earlier batches.',
           'records':records}
    save(folder/'selection.json',value)
    print({'batch':name,'scans':len(records),'inventories':[r['inventoryNumber'] for r in records]},flush=True)
    return value

def acquire_batch(name,offline=False,inventory=None):
    selection=read(batch_dir(name)/'selection.json');cache=ImageCache(offline=offline)
    for record in validate_selection(selection):
        n=record['inventoryNumber']
        if inventory and n not in inventory:continue
        work=CACHE/'work'/n
        ev,path=cache.get(record,*overview_request(record),'overview')
        save(work/'overview.json',ev)
        image=cv2.imread(str(path))
        try:
            frame=frame_lines(image,n)
            method='Canny/Hough inner-frame proposal'
        except ValueError:
            h,w=image.shape[:2]
            frame=[[.14*w,.215*h],[.86*w,.215*h],[.86*w,.78*h],[.14*w,.78*h]]
            method='Layout-window acquisition fallback; frame requires native evidence review'
        original=[original_point(p,ev) for p in frame]
        save(work/'frame-candidate.json',{'overviewFrame':frame,'resourceFrame':original,
             'method':method,'reviewStatus':'unreviewed'})
        preview=Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
        ImageDraw.Draw(preview).line([tuple(p) for p in frame+[frame[0]]],fill='red',width=2)
        preview.save(work/'frame-preview.jpg')
        details=[]
        for corner,p in zip(['tl','tr','br','bl'],original):
            x=p[0]-(180 if corner.endswith('l') else 1620)
            y=p[1]-(160 if corner.startswith('t') else 840)
            evidence,_=cache.get(record,*region_request(record,[x,y,1800,1000]))
            details.append({'corner':corner,'evidence':evidence})
        save(work/'corners.json',details)
        print(n,'prepared',flush=True)
    print({'networkRequests':cache.network_requests,'cacheHits':cache.cache_hits},flush=True)

def hydrate_batch(name,offline=False):
    """Replay the saved evidence ledger, including adaptive crops, without new proposals."""
    folder=batch_dir(name);cache=ImageCache(offline=offline)
    for record in validate_selection(read(folder/'selection.json')):
        canonical=read(folder/'maps'/(record['id']+'.json'));by_id={}
        for expected in canonical['evidence']:
            actual,_=cache.get(record,expected['url'],expected['region'],expected['kind'])
            if actual['sha256']!=expected['sha256'] or actual['decodedSize']!=expected['decodedSize']:
                raise ValueError('Remote evidence changed; review required: '+expected['id'])
            by_id[expected['id']]=expected
        ev={key:by_id[value] for key,value in canonical['evidenceKeys'].items()}
        work=CACHE/'work'/record['inventoryNumber']
        save(work/'corners.json',[{'corner':key,'evidence':ev[key]} for key in ['tl','tr','br','bl']])
        for key,value in ev.items():
            if key not in ['tl','tr','br','bl']:save(work/(key+'.json'),value)
        save(work/'frame-candidate.json',{'resourceFrame':canonical['mask']['candidateFrame'],
            'method':'Restored original acquisition proposal; reviewed native frame stored separately.'})
    print({'networkRequests':cache.network_requests,'cacheHits':cache.cache_hits},flush=True)
