import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'data/georeferencing/nieuwe-stijl'
CACHE = ROOT / '.cache/georeferencing'
BASE = 'https://tu-delft-heritage.github.io/river-maps-iiif/'
PILOT = ['478', '821', '878', '498', '542', '940', '1050', '726', '1085', '596',
         '1139', '1140', '1212', '1252', '1273', '1327', '1337', '1344', '1359',
         '1401', '769', '947', '948', '949']


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def walk(node):
    yield node
    for child in node['children']:
        yield from walk(child)


def select():
    source = ROOT / 'data/nationaal-archief/nieuwe-stijl.json'
    snapshot = read(source)
    records = []
    excluded = []
    for group in snapshot['edition']['children']:
        for record in walk(group):
            if not record.get('metsUrl'):
                continue
            number = record['inventoryNumber']
            if group['code'] == 'D.01':
                excluded.append({'inventoryNumber': number, 'reason': 'sheet-index-or-legend'})
                continue
            images = snapshot['objects'][record['uuid']]['images']
            for image in images:
                map_id = record['uuid'] + '-' + image['id'] + '-main'
                manifest = f"manifests/nieuwe-stijl/series-{group['code'][2:]}.json"
                records.append({
                    'id': map_id, 'inventoryNumber': number, 'series': group['code'],
                    'title': record['title'], 'sourceRecordId': record['uuid'],
                    'sourceImageId': image['id'], 'imageService': image['info'],
                    'manifestPath': manifest,
                    'canvasId': BASE + manifest + '#canvas-' + record['uuid'] + '-' + image['id'],
                    'metadata': record['metadata'], 'metsUrl': record['metsUrl'],
                    'homepage': record['homepage'], 'pilot': number in PILOT,
                    **({'sharedSheet': 'appendix-a-76-3035'} if number in ['947', '948'] else {}),
                })
    if len(records) != 999 or len(excluded) != 10:
        raise ValueError('Inventory scope changed; reconcile the plan before processing')
    pilot = [r for r in records if r['pilot']]
    if len(pilot) != 24 or len({r['series'] for r in pilot}) != 16:
        raise ValueError('Pilot must contain 24 scans and all 16 map groups')
    selection = {'schemaVersion': 1, 'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                 'eadSha256': snapshot['eadSha256'], 'records': records, 'excluded': excluded,
                 'pilotInventoryNumbers': PILOT}
    save(DATA / 'selection.json', selection)
    return selection


def pilot_records():
    return [r for r in read(DATA / 'selection.json')['records'] if r['pilot']]
