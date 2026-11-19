#!/usr/bin/env python3
"""Snapshot EAD, METS and Image API metadata; never download map images.

Python 3 standard library only. Completed requests are cached for resumable syncs.
The committed snapshot is replaced only after every record has been resolved.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SOURCE = 'https://www.nationaalarchief.nl/onderzoeken/archief/2.16.5150/download/xml'
DEST = ROOT / 'data/nationaal-archief'
NS = {'m': 'http://www.loc.gov/METS/', 'r': 'http://www.archivesportaleurope.net/Portal/profiles/rights/'}
XLINK = '{http://www.w3.org/1999/xlink}href'
REQUEST_LOCK = threading.Lock()
NEXT_REQUEST = 0.0
LABELS = {
    'unittitle': 'Titel', 'unitdate': 'Datering', 'unitid': 'Identificatie',
    'materialspec': 'Kaartschaal / materiaal', 'physdesc': 'Fysieke beschrijving',
    'scopecontent': 'Inhoud', 'arrangement': 'Ordening / exemplaar',
    'relatedmaterial': 'Verwant materiaal', 'processinfo': 'Verantwoording bewerking',
    'controlaccess': 'Trefwoorden', 'custodhist': 'Geschiedenis van het beheer',
    'accessrestrict': 'Openbaarheid', 'userestrict': 'Gebruiksbeperkingen',
    'altformavail': 'Andere verschijningsvormen', 'separatedmaterial': 'Afgescheiden materiaal',
    'origination': 'Archiefvormer', 'repository': 'Archiefdienst', 'physloc': 'Locatie',
    'langmaterial': 'Taal', 'abstract': 'Samenvatting', 'bioghist': 'Geschiedenis',
}


def text(element):
    if element is None:
        return ''
    # Keep boundaries between paragraphs, line breaks and inline references.
    return ' '.join(' '.join(element.itertext()).split())


def identifier(element, kind):
    return element.findtext(f"did/unitid[@type='{kind}']", '')


def metadata(element):
    result = []
    for child in element:
        if child.tag == 'did':
            result.extend(metadata(child))
        elif child.tag not in ('c', 'dao', 'head') and text(child):
            label = child.get('label', LABELS.get(child.tag, child.tag)).strip().rstrip(':')
            if child.get('type'):
                label += f" ({child.get('type')})"
            result.append({'label': label, 'value': text(child)})
            if child.tag == 'unitdate' and child.get('normal'):
                result.append({'label': 'Datering (ISO)', 'value': child.get('normal')})
    return result


def component(element):
    uuid = identifier(element, 'urn:uuid')
    if not uuid:
        raise ValueError('EAD component has no stable UUID')
    result = {
        'uuid': uuid, 'level': element.get('level'),
        'code': identifier(element, 'series_code'),
        'inventoryNumber': identifier(element, 'BD'),
        'title': text(element.find('did/unittitle')),
        'metadata': metadata(element),
        'children': [component(c) for c in element.findall('c')],
    }
    handle = identifier(element, 'handle')
    if handle:
        result['homepage'] = handle
    daos = element.findall('did/dao')
    if len(daos) > 1:
        raise ValueError(f'Multiple DAO links need explicit handling: {uuid}')
    if daos:
        if daos[0].get('role') != 'METS':
            raise ValueError(f'Unexpected DAO format: {uuid}')
        result['metsUrl'] = daos[0].get('href')
    # Keep descriptive groups only when they contain digitized descendants.
    result['children'] = [child for child in result['children'] if child is not None]
    if not daos and not result['children']:
        return None
    return result


def walk(node):
    yield node
    for child in node['children']:
        yield from walk(child)


def fetch(url, cache, refresh=False):
    global NEXT_REQUEST
    path = cache / hashlib.sha256(url.encode()).hexdigest()
    if path.exists() and not refresh:
        return path.read_bytes()
    for attempt in range(6):
        try:
            # Bound the total request rate, regardless of the worker count.
            with REQUEST_LOCK:
                delay = NEXT_REQUEST - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
                NEXT_REQUEST = time.monotonic() + 0.4
            request = Request(url, headers={'User-Agent': 'river-maps-iiif metadata sync/1.0'})
            with urlopen(request, timeout=45) as response:
                data = response.read()
            temporary = path.with_suffix('.tmp')
            temporary.write_bytes(data)
            temporary.replace(path)
            return data
        except Exception as error:
            if attempt == 5:
                raise
            delay = 2 ** attempt
            if isinstance(error, HTTPError) and error.code == 429:
                retry = error.headers.get('Retry-After', '')
                delay = max(30, int(retry) if retry.isdigit() else delay)
                with REQUEST_LOCK:
                    NEXT_REQUEST = max(NEXT_REQUEST, time.monotonic() + delay)
            time.sleep(delay)


def resolve_record(record, cache, refresh):
    raw = fetch(record['metsUrl'], cache, refresh).decode('utf-8')
    mets = ET.fromstring(raw)
    files = {}
    for group in mets.findall('m:fileSec/m:fileGrp', NS):
        for file in group.findall('m:file', NS):
            loc = file.find('m:FLocat', NS)
            files[file.get('ID')] = {
                'group': group.get('USE'), 'url': loc.get(XLINK),
                'format': file.get('MIMETYPE'), 'size': file.get('SIZE'),
            }
    rights = []
    for declaration in mets.findall('.//r:RightsDeclarationMD', NS):
        rights.append({
            'category': declaration.get('RIGHTSCATEGORY'),
            'metadata': [{'label': child.tag.split('}')[-1], 'value': text(child)}
                         for child in declaration if text(child)],
        })
    images = []
    physical = mets.findall("m:structMap[@TYPE='PHYSICAL']//m:div", NS)
    for div in physical:
        pointers = div.findall('m:fptr', NS)
        if not pointers:
            continue
        linked = [files[p.get('FILEID')] for p in pointers]
        by_group = {file['group']: file for file in linked}
        display, original = by_group.get('DISPLAY'), by_group.get('DEFAULT')
        if not display or not original or original['format'] != 'image/jpeg':
            raise ValueError(f'Missing image/service: {record["metsUrl"]}')
        info = json.loads(fetch(display['url'], cache, refresh))
        if (info.get('type') != 'ImageService3' or info.get('profile') not in ('level0', 'level1', 'level2')
                or not isinstance(info.get('width'), int) or info['width'] <= 0
                or not isinstance(info.get('height'), int) or info['height'] <= 0
                or not info.get('id') or not display['url'].endswith('/info.json')):
            raise ValueError(f'Invalid Image API response: {display["url"]}')
        if info['id'] != display['url'][:-len('/info.json')]:
            raise ValueError(f'Unexpected Image API identity: {display["url"]}')
        images.append({
            'id': div.get('ID'), 'order': int(div.get('ORDER', len(images) + 1)),
            'label': div.get('LABEL'), 'image': original,
            'thumbnail': by_group.get('THUMBS'), 'infoUrl': display['url'], 'info': info,
        })
    if not images or len({image['id'] for image in images}) != len(images):
        raise ValueError(f'Empty or duplicate image sequence: {record["metsUrl"]}')
    return {'metsUrl': record['metsUrl'], 'metsXml': raw, 'rights': rights,
            'images': sorted(images, key=lambda image: image['order'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ead', type=Path, help='Use an already downloaded EAD XML')
    parser.add_argument('--cache-dir', type=Path, default=ROOT / '.cache/nationaal-archief')
    parser.add_argument('--refresh', action='store_true', help='Refresh cached METS and image metadata')
    parser.add_argument('--workers', type=int, choices=range(1, 9), default=4)
    args = parser.parse_args()
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    # Always fetch the current finding aid unless a specific local snapshot was supplied.
    raw_ead = args.ead.read_bytes() if args.ead else fetch(SOURCE, args.cache_dir, True)
    ead = ET.fromstring(raw_ead)
    if text(ead.find('eadheader/eadid')) != '2.16.5150':
        raise ValueError('Wrong archive inventory')
    section = next(c for c in ead.findall('archdesc/dsc/c') if identifier(c, 'series_code') == 'D')
    edition = component(section)
    records = [node for node in walk(edition) if node.get('metsUrl')]
    if not records or len({r['metsUrl'] for r in records}) != len(records):
        raise ValueError('Empty or duplicate digital-object links')
    objects = {}
    print(f'Resolving {len(records)} digital records in {len(edition["children"])} series...', flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(resolve_record, r, args.cache_dir, args.refresh): r for r in records}
        for count, future in enumerate(as_completed(futures), 1):
            record = futures[future]
            objects[record['uuid']] = future.result()
            if count % 100 == 0 or count == len(records):
                print(f'  {count}/{len(records)} resolved', flush=True)
    header = ead.find('eadheader')
    snapshot = {
        'schemaVersion': 1, 'source': SOURCE,
        'retrievedAt': datetime.now(timezone.utc).isoformat(),
        'eadSha256': hashlib.sha256(raw_ead).hexdigest(),
        'eadVersion': text(header.find('filedesc/editionstmt/edition')),
        'archive': {'title': text(header.find('filedesc/titlestmt/titleproper')),
                    'homepage': header.find('eadid').get('url'),
                    'metadata': metadata(ead.find('archdesc/did'))},
        'edition': edition,
        'objects': {r['uuid']: objects[r['uuid']] for r in records},
    }
    # All network responses and parsing have succeeded before touching committed data.
    DEST.mkdir(parents=True, exist_ok=True)
    for name, content in [('2.16.5150.xml', raw_ead),
                          ('nieuwe-stijl.json', (json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n').encode())]:
        path = DEST / name
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_bytes(content)
        temporary.replace(path)
    print(f'Saved {len(records)} records and {sum(len(o["images"]) for o in objects.values())} images. Run pnpm validate.')


if __name__ == '__main__':
    main()
