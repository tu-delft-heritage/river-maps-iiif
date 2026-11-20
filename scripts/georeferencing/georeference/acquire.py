from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import fcntl
from io import BytesIO
import json
from pathlib import Path
import random
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from PIL import Image
from .catalog import CACHE, save


def retry_seconds(value, now=None):
    if not value:
        return 0
    if value.strip().isdigit():
        return int(value)
    try:
        return max(0, parsedate_to_datetime(value).timestamp() - (time.time() if now is None else now))
    except (ValueError, TypeError):
        return 0


def overview_request(record):
    info = record['imageService']
    sizes = info.get('sizes', [])
    size = min(sizes, key=lambda s: abs(max(s['width'], s['height']) - 1800)) if sizes else {'width': min(1800, info['width'])}
    return info['id'] + f"/full/{size['width']},/0/default.jpg", [0, 0, info['width'], info['height']]


def region_request(record, region):
    info = record['imageService']
    x, y, w, h = region
    x, y = max(0, int(x)), max(0, int(y))
    w, h = min(int(w), info['width'] - x), min(int(h), info['height'] - y)
    if min(w, h) <= 0:
        raise ValueError('Region is outside the image')
    scale = min(1, (1_800_000 / (w*h)) ** .5,
                info.get('maxWidth', w) / w, info.get('maxHeight', h) / h,
                (info.get('maxArea', w*h) / (w*h)) ** .5)
    width = max(1, int(w * scale))
    return info['id'] + f'/{x},{y},{w},{h}/{width},/0/default.jpg', [x, y, w, h]


class ImageCache:
    """Sequential per-host acquisition. A persistent timestamp also bounds resumed runs."""
    def __init__(self, directory=CACHE, offline=False, interval=1.0):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.offline, self.interval = offline, interval
        self.network_requests = 0
        self.cache_hits = 0

    def get(self, record, url, region, kind='detail'):
        # Fail fast if a second worker would violate the single-flight host policy.
        with (self.directory/'acquire.lock').open('w') as lock:
            try:
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError('Another acquisition worker is active') from error
            return self._get_locked(record,url,region,kind)

    def _get_locked(self, record, url, region, kind='detail'):
        key = hashlib.sha256(url.encode()).hexdigest()
        image_path = self.directory / 'images' / (key + '.jpg')
        metadata_path = image_path.with_suffix('.json')
        if metadata_path.exists() and image_path.exists():
            result = json.loads(metadata_path.read_text())
            if hashlib.sha256(image_path.read_bytes()).hexdigest() != result['sha256']:
                raise ValueError(f'Corrupt cached image: {key}')
            self.cache_hits += 1
            return result, image_path
        if self.offline:
            raise FileNotFoundError(f'No cached evidence for {url}')
        existing = [json.loads(p.read_text()) for p in (self.directory / 'images').glob('*.json')]
        used = [e for e in existing if e['mapId'] == record['id'] and e['kind'] == 'detail']
        if kind == 'detail' and len(used) >= 12:
            raise ValueError(f'Detail request budget exhausted: {record["inventoryNumber"]}')
        for attempt in range(5):
            timestamp = self.directory / 'last-request.txt'
            if timestamp.exists():
                time.sleep(max(0, float(timestamp.read_text()) + self.interval - time.time()))
            timestamp.write_text(str(time.time()))
            self.network_requests += 1
            try:
                with urlopen(Request(url, headers={'User-Agent': 'river-maps-iiif georeferencing/1.0'}), timeout=45) as response:
                    body = response.read()
                    headers = response.headers
                with Image.open(BytesIO(body)) as image:
                    image.load()
                    size = list(image.size)
                if kind == 'detail' and size[0]*size[1]>1_800_000:
                    raise ValueError('IIIF server exceeded the detail pixel budget')
                result = {'id': key, 'mapId': record['id'], 'inventoryNumber': record['inventoryNumber'],
                          'kind': kind, 'url': url, 'region': region, 'decodedSize': size,
                          'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body),
                          'retrievedAt': datetime.now(timezone.utc).isoformat(),
                          'etag': headers.get('ETag'), 'lastModified': headers.get('Last-Modified')}
                image_path.parent.mkdir(parents=True, exist_ok=True)
                temporary = image_path.with_suffix('.tmp')
                temporary.write_bytes(body)
                temporary.replace(image_path)
                save(metadata_path, result)
                return result, image_path
            except HTTPError as error:
                if error.code not in (429, 500, 502, 503, 504) or attempt == 4:
                    raise
                delay = max(retry_seconds(error.headers.get('Retry-After')), 2 ** (attempt + 2))
                time.sleep(delay + random.uniform(0, 1))
            except (TimeoutError, OSError):
                if attempt == 4:
                    raise
                time.sleep(2 ** (attempt + 1))


def original_point(point, evidence):
    # Optional inverse deskew maps a rotated local analysis image back to the decoded crop.
    if 'inverseLocalAffine' in evidence:
        a,b=evidence['inverseLocalAffine']
        point=[a[0]*point[0]+a[1]*point[1]+a[2],b[0]*point[0]+b[1]*point[1]+b[2]]
    x, y, width, height = evidence['region']
    decoded_width, decoded_height = evidence['decodedSize']
    return [x + point[0] * width / decoded_width, y + point[1] * height / decoded_height]
