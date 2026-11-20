#!/usr/bin/env python3
"""Build the essay's evidence figures offline, from final records and cached scans.

Requires Pillow and NumPy (the georeferencing environment already supplies both).
No image generation, contrast enhancement, OCR, network access or data mutation.
See docs/georeferencing/nieuwe-stijl-georeferencing-essay.md for reproduction and interpretation.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PAPER = '#f4f0e7'
INK = '#243a39'
MUTED = '#63736c'
GREEN = '#21735e'
BLUE = '#32639a'
RED = '#ad4639'
LINE = '#c8c9bb'
RESAMPLE = Image.Resampling.LANCZOS
PROVENANCE = {'schemaVersion': 1, 'method': 'Offline crops of saved evidence; no generated map content',
              'figures': {}, 'mosaic': {}}


def font(size, style='sans'):
    choices = {
        'serif': ['Georgia.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'],
        'sans': ['Arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'],
        'bold': ['Arial Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'],
    }[style]
    for name in choices:
        p = Path(name) if name.startswith('/') else Path('/System/Library/Fonts/Supplemental') / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    raise FileNotFoundError('Install Georgia/Arial or DejaVu fonts to render figure labels')


def label(im, xy, text, size=26, color=INK, style='sans'):
    ImageDraw.Draw(im).text(xy, text, font=font(size, style), fill=color)


def panel(width, height, title, subtitle):
    im = Image.new('RGB', (width, height), PAPER)
    label(im, (60, 34), title, 54, style='serif')
    label(im, (62, 106), subtitle, 26, MUTED)
    ImageDraw.Draw(im).line((60, 154, width - 60, 154), fill=LINE, width=2)
    return im


def paste_fit(dst, src, box):
    x, y, w, h = box
    s = min(w / src.width, h / src.height)
    resized = src.resize((round(src.width * s), round(src.height * s)), RESAMPLE)
    xy = (round(x + (w - resized.width) / 2), round(y + (h - resized.height) / 2))
    dst.paste(resized, xy, resized if resized.mode == 'RGBA' else None)
    return xy, s


def save(im, name):
    path = OUT / f'{name}.jpg'
    im.save(path, quality=92, subsampling=0, optimize=True)
    return path


def evidence(d, key):
    eid = d['evidenceKeys'][key]
    return next(e for e in d['evidence'] if e['id'] == eid)


def load_evidence(e):
    path = CACHE / 'images' / (e['id'] + '.jpg')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == e['sha256'], f'Changed evidence: {path}'
    with Image.open(path) as im:
        assert list(im.size) == e['decodedSize']
        return im.convert('RGB')


def source(d, e, bounds=None):
    return {'inventoryNumber': d['source']['inventoryNumber'], 'canonical': PATHS[d['id']],
            'homepage': d['source']['homepage'], 'evidenceId': e['id'],
            'url': e['url'], 'sha256': e['sha256'], 'cropInDecodedEvidence': bounds}


def local_coords(e, coords):
    return (np.asarray(coords) - np.array(e['region'][:2])) * np.array(e['decodedSize']) / np.array(e['region'][2:])


def cross_crop(d, p, radius=27):
    e = next(e for e in d['evidence'] if e['id'] == p['evidenceId'])
    im = load_evidence(e)
    x, y = local_coords(e, p['resourceCoords'])
    assert 0 <= x < im.width and 0 <= y < im.height
    size = 2*radius+1
    left = max(0, min(round(x)-radius, im.width-size))
    top = max(0, min(round(y)-radius, im.height-size))
    bounds = [left, top, left+size, top+size]
    assert 0 <= bounds[0] < bounds[2] <= im.width and 0 <= bounds[1] < bounds[3] <= im.height
    return im.crop(bounds), e, bounds


def hero():
    d = INVENTORY['1433'][0]
    e = evidence(d, 'overview')
    scan = load_evidence(e)
    im = panel(2400, 1430, 'A river map finds its bearings',
               'Haringvliet · sheet 864 · inventory 1433')
    label(im, (65, 184), '01   THE SCANNED SHEET', 28, style='bold')
    label(im, (1260, 184), '02   POSITIONED ON ITS RD GRID', 28, style='bold')
    paste_fit(im, scan, (60, 245, 1110, 1050))

    A = np.array(d['adjustment']['linear'])
    b = np.array(d['adjustment']['intercept'])
    mask = np.array(d['mask']['resourceMask'])
    rd = (mask - b) @ np.linalg.inv(A).T
    lo, hi = rd.min(axis=0), rd.max(axis=0)
    s = min(980 / (hi[0] - lo[0]), 990 / (hi[1] - lo[1]))
    size = tuple(np.ceil((hi - lo) * s).astype(int))
    # Pillow needs output->input coordinates. Output y runs down; northing runs up.
    native_from_out = A @ np.diag([1/s, -1/s])
    native_offset = A @ np.array([lo[0], hi[1]]) + b
    sc = np.array(e['decodedSize']) / np.array(e['region'][2:])
    M = native_from_out * sc[:, None]
    off = (native_offset - e['region'][:2]) * sc
    coeff = tuple(np.column_stack((M, off)).ravel())
    alpha = Image.new('L', scan.size, 0)
    ImageDraw.Draw(alpha).polygon([tuple(p) for p in local_coords(e, mask)], fill=255)
    rgba = scan.convert('RGBA'); rgba.putalpha(alpha)
    north = rgba.transform(size, Image.Transform.AFFINE, coeff, Image.Resampling.BICUBIC)
    paste_fit(im, north, (1240, 245, 1100, 1050))
    draw = ImageDraw.Draw(im)
    draw.line((2300, 405, 2300, 290), fill=INK, width=4)
    draw.polygon([(2300, 275), (2288, 300), (2312, 300)], fill=INK)
    label(im, (2275, 236), 'N', 28, style='bold')
    label(im, (65, 1330), 'The original image stays intact. A saved mask and coordinates describe how to place it.', 30)
    label(im, (65, 1377), 'Illustration from the cached overview and saved affine fit; north means RD grid north.', 23, MUTED)
    save(im, '01-finding-north')
    PROVENANCE['figures']['01-finding-north'] = {'sources': [source(d, e)],
        'method': 'Left: unchanged overview. Right: overview masked and resampled with saved RD-to-image affine, grid north up.'}


def five_crosses():
    d = INVENTORY['1433'][0]
    im = panel(2400, 820, 'Five small marks, two different jobs',
               'Four points position the sheet. The fifth tests a place the fit was not allowed to use.')
    sources = []
    for i, p in enumerate(d['points']):
        x = 65 + i * 463
        is_check = p['role'] == 'check'
        c = BLUE if is_check else GREEN
        label(im, (x, 190), f'{i + 1:02d}   ' + ('CHECK' if is_check else 'CONTROL'), 29, c, 'bold')
        crop, e, bounds = cross_crop(d, p, radius=45)
        paste_fit(im, crop, (x, 250, 410, 350))
        E, N = p['originalProjected']['coordinates']
        label(im, (x, 637), f'E {E:,.0f} m', 30)
        label(im, (x, 681), f'N {N:,.0f} m', 30)
        sources.append({**source(d, e, bounds), 'pointId': p['id'], 'role': p['role']})
    label(im, (65, 762), 'Original RD New coordinates · cross centres are measured; arrow tips indicate the grid direction.', 25, MUTED)
    save(im, '02-five-crosses')
    PROVENANCE['figures']['02-five-crosses'] = {'sources': sources,
        'method': 'Unmarked source crops enlarged without changing their orientation or contrast.'}


def masks():
    im = panel(2400, 2090, 'Where does the map end?',
               'Saved review images · red outline: mask · green: fitted controls · blue: withheld check')
    sources = []
    for i, (n, title, note) in enumerate([
        ('1433', 'A title in the corner', 'A short notch leaves the title outside the geographic overlay.'),
        ('631', 'A title halfway down the side', 'The map continues above and below the label.'),
        ('875', 'A table set into the bottom edge', 'A narrow opening reaches the table; map detail survives on both sides.'),
    ]):
        d = INVENTORY[n][0]
        p = CACHE / 'review' / f'{n}-mask.jpg'
        with Image.open(p) as original:
            original = original.convert('RGB')
            scale = np.array(original.size) / d['nativeSize']
            pts = np.array(d['mask']['resourceMask']) * scale
            mn, mx = pts.min(axis=0), pts.max(axis=0)
            bounds = [max(0, int(mn[0])-25), max(0, int(mn[1])-25),
                      min(original.width, int(mx[0])+25), min(original.height, int(mx[1])+25)]
            crop = original.crop(bounds)
        y = 185 + i * 625
        paste_fit(im, crop, (60, y, 1540, 570))
        label(im, (1660, y+105), f'INVENTORY {n}', 25, MUTED, 'bold')
        # Deliberate line breaks keep the narrow explanatory column readable.
        titles = {'1433': ['A title in', 'the corner'], '631': ['A title halfway', 'down the side'],
                  '875': ['A table set into', 'the bottom edge']}
        for k, line in enumerate(titles[n]):
            label(im, (1660, y+155+k*54), line, 42, style='serif')
        notes = {'1433': ['A short notch leaves the title', 'outside the geographic overlay.'],
                 '631': ['The map continues above', 'and below the label.'],
                 '875': ['A narrow opening reaches the table;', 'map detail survives on both sides.']}
        for k, line in enumerate(notes[n]):
            label(im, (1660, y+295+k*43), line, 27, MUTED)
        sources.append({'inventoryNumber': n, 'canonical': PATHS[d['id']],
            'reviewImage': f'review/{n}-mask.jpg', 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
            'cropInReviewImage': bounds})
    save(im, '03-masks')
    PROVENANCE['figures']['03-masks'] = {'sources': sources,
        'method': 'Crops of saved review overlays; colored marks were already present in these diagnostic images.'}


def bad_label():
    d = INVENTORY['1455'][0]
    e = evidence(d, 'br')
    scan = load_evidence(e)
    im = panel(2400, 1220, 'The number that did not belong',
               'Inventory 1455 · the source prints “-50.000” where the surrounding grid disagrees')
    label(im, (65, 185), 'THE LOWER-RIGHT CORNER', 26, style='bold')
    xy, s = paste_fit(im, scan, (60, 240, 1480, 825))
    bounds = [870, 847, 955, 892]
    draw = ImageDraw.Draw(im)
    rect = [xy[0]+bounds[0]*s, xy[1]+bounds[1]*s, xy[0]+bounds[2]*s, xy[1]+bounds[3]*s]
    draw.rectangle(rect, outline=RED, width=3)
    label(im, (1640, 185), 'ENLARGED SOURCE LABELS', 26, style='bold')
    specs = [('br', bounds, 'Lower border: -50.000', RED),
             ('tl', [1136, 105, 1220, 153], 'Top border: -39.400', GREEN),
             ('bl', [1020, 839, 1106, 885], 'Lower-left: -40.400', GREEN)]
    sources = [source(d, e)]
    for i, (key, box, text, col) in enumerate(specs):
        ev = evidence(d, key)
        crop = load_evidence(ev).crop(box)
        paste_fit(im, crop, (1635, 245+i*270, 650, 170))
        label(im, (1640, 430+i*270), text, 28, col)
        sources.append(source(d, ev, box))
    label(im, (65, 1127), 'The conflicting label is preserved in the record. The fit uses the consistent labels and 200-metre steps.', 29)
    label(im, (65, 1174), 'The image has not been corrected or repainted.', 23, MUTED)
    save(im, '04-unexpected-coordinate')
    PROVENANCE['figures']['04-unexpected-coordinate'] = {'sources': sources,
        'method': 'Source corner plus enlarged, unretouched label crops; red box locates the first inset.'}


def missing_labels():
    im = panel(2400, 1260, 'One sheet helps read another',
               'Sheet 880 · the same grid survives across different editions of the Haringvliet map')
    sources = []
    for i, n in enumerate(['812', '1459']):
        d = INVENTORY[n][0]
        e = evidence(d, 'tl'); scan = load_evidence(e)
        x = 60+i*1180
        label(im, (x, 190), f'INVENTORY {n}', 29, style='bold')
        label(im, (x, 238), 'Easting labels absent here' if n == '812' else 'Easting labels present here', 28, MUTED)
        xy, s = paste_fit(im, scan, (x, 305, 1100, 620))
        p = d['points'][0]
        px, py = local_coords(e, p['resourceCoords'])
        draw = ImageDraw.Draw(im)
        cx, cy = xy[0]+px*s, xy[1]+py*s
        draw.ellipse((cx-15,cy-15,cx+15,cy+15), outline=BLUE, width=3)
        label(im, (x, 955), 'Circled cross: E 68,000 m · N 427,400 m', 28, BLUE)
        sources.append(source(d, e))
        if n == '1459':
            bounds = [1095, 110, 1185, 175]
            crop = scan.crop(bounds)
            paste_fit(im, crop, (x+865, 185, 190, 130))
            sources.append(source(d, e, bounds))
    label(im, (65, 1080), 'Grid direction, spacing and shared cartography connect the copies; the easting anchor comes from 1459.', 29)
    label(im, (65, 1130), '812 retains its own northing labels. This borrowed anchor is recorded as a dependency, not an independent check.', 27, MUTED)
    label(im, (65, 1197), 'Native detail crops shown in their original orientations; the two scans have different framing.', 23, MUTED)
    save(im, '05-missing-labels')
    PROVENANCE['figures']['05-missing-labels'] = {'sources': sources,
        'method': 'Unchanged upper-left details with circles around the same assigned grid coordinate; enlarged 68.0 label on 1459.'}


def mosaic(records):
    tile, gap, groupgap, margin, header = 64, 3, 15, 100, 280
    groups_across = 15
    groupwidth = 5*tile+4*gap
    rows = math.ceil(len(records)/groups_across)
    width = 2*margin + groups_across*groupwidth + (groups_across-1)*groupgap
    height = header + rows*(tile+10) + 175
    im = Image.new('RGB', (width, height), PAPER)
    label(im, (margin, 50), '4,995 small anchors', 108, style='serif')
    label(im, (margin+3, 191), '999 scanned maps · four fitted crosses + one withheld check per map · archival order', 42, MUTED)
    cells, seen = [], set()
    for j, d in enumerate(records):
        assert len(d['points']) == 5
        assert [p['role'] for p in d['points']] == ['control']*4+['check']
        for k, p in enumerate(d['points']):
            identity = (d['id'], p['id'])
            assert identity not in seen
            seen.add(identity)
            crop, e, bounds = cross_crop(d, p)
            x = margin + (j % groups_across)*(groupwidth+groupgap) + k*(tile+gap)
            y = header + (j // groups_across)*(tile+10)
            im.paste(crop.resize((tile,tile), RESAMPLE), (x,y))
            cells.append({'mapId': d['id'], 'inventoryNumber': d['source']['inventoryNumber'],
                'pointId': p['id'], 'role': p['role'], 'evidenceId': e['id'],
                'crop': bounds, 'posterXY': [x,y]})
    assert len(cells) == 4995
    label(im, (margin, height-125), 'Each group of five belongs to one scan. These are the measured marks, not every printed cross.', 38)
    label(im, (margin, height-67), 'Nationaal Archief · inventory 2.16.5150 · source images: Public Domain Mark · no marks generated or repainted', 32, MUTED)
    save(im, '06-all-crosses-full')
    preview = im.copy(); preview.thumbnail((2000,2000), RESAMPLE)
    save(preview, '06-all-crosses')
    PROVENANCE['mosaic'] = {'maps': len(records), 'crosses': len(cells), 'order': 'selection.json records; saved point order',
        'tileSize': tile, 'tileSourceSize': 55, 'mapsPerRow': groups_across,
        'posterSize': list(im.size), 'cells': cells,
        'canonicalRecords': {d['id']: PATHS[d['id']] for d in records},
        'note': 'Repeated editions may depict the same ground location. Five cells per scan; final row has six unused map slots. Six crops are shifted within the evidence boundary to avoid padding unavailable image content.'}


def main():
    global OUT, CACHE, INVENTORY, PATHS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--cache-root', type=Path, help='Default: REPO/.cache/georeferencing')
    parser.add_argument('--output', type=Path, help='Default: REPO/docs/georeferencing/images/georeferencing-essay')
    args = parser.parse_args()
    repo = args.repo.resolve()
    CACHE = args.cache_root or repo / '.cache/georeferencing'
    OUT = args.output or repo / 'docs/georeferencing/images/georeferencing-essay'
    OUT.mkdir(parents=True, exist_ok=True)
    base = repo / 'data/georeferencing/nieuwe-stijl'
    docs, PATHS, INVENTORY = {}, {}, {}
    PROVENANCE['canonicalSha256'] = {}
    for p in sorted([*base.glob('maps/*.json'), *base.glob('batches/batch-*/maps/*.json')]):
        d = json.loads(p.read_text())
        assert d['id'] not in docs, f'Duplicate map: {d["id"]}'
        docs[d['id']] = d
        PATHS[d['id']] = str(p.relative_to(repo))
        PROVENANCE['canonicalSha256'][d['id']] = hashlib.sha256(p.read_bytes()).hexdigest()
        INVENTORY.setdefault(str(d['source']['inventoryNumber']), []).append(d)
    selection = json.loads((base/'selection.json').read_text())['records']
    records = [docs[r['id']] for r in selection]
    assert len(records) == len(docs) == 999
    for name, fn in [('north-up illustration', hero), ('five crosses', five_crosses),
                     ('mask gallery', masks), ('coordinate anomaly', bad_label), ('missing labels', missing_labels),
                     ('all measured crosses', lambda: mosaic(records))]:
        fn(); print(f'Built {name}', flush=True)
    PROVENANCE['outputs'] = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
        'size': list(Image.open(p).size)} for p in sorted(OUT.glob('*.jpg'))}
    (OUT/'provenance.json').write_text(json.dumps(PROVENANCE, ensure_ascii=False, separators=(',', ':'))+'\n')
    print(f'Saved seven JPEGs and provenance in {OUT}')


if __name__ == '__main__':
    main()
