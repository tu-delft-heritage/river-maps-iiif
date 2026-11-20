"""Portable evidence recipe. Photographs stay in the ignored cache."""
import hashlib
from .catalog import DATA,CACHE,read,save,pilot_records
from .acquire import ImageCache


def freeze_inputs():
    inputs={}
    for r in pilot_records():
        n=r['inventoryNumber'];work=CACHE/'work'/n
        inputs[n]={p.name:read(p) for p in sorted(work.glob('*.json'))}
    save(DATA/'evidence-inputs.json',{'schemaVersion':1,'work':inputs})


def hydrate(offline=True):
    inputs=read(DATA/'evidence-inputs.json');records={r['id']:r for r in pilot_records()}
    items={}
    for values in inputs['work'].values():
        for value in values.values():
            if isinstance(value,dict) and 'sha256' in value:items[value['id']]=value
            if isinstance(value,list):
                for row in value:
                    if isinstance(row,dict) and 'evidence' in row:items[row['evidence']['id']]=row['evidence']
    for t in read(DATA/'tie-candidates.json')['ties']:
        for e in t['evidence']:items[e['id']]=e
    for e in read(DATA/'acquisition-catalog.json')['items']:items[e['id']]=e
    cache=ImageCache(offline=offline)
    for e in items.values():
        acquired,path=cache.get(records[e['mapId']],e['url'],e['region'],e['kind'])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=e['sha256']:
            raise ValueError('Archive response changed; review required: '+e['url'])
    for n,values in inputs['work'].items():
        for name,value in values.items():save(CACHE/'work'/n/name,value)
    print({'networkRequests':cache.network_requests,'cacheHits':cache.cache_hits})
