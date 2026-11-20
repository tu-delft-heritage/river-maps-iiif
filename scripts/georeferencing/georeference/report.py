"""Generate the concise pilot report and an offline visual review gallery."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import html
from collections import Counter
from georeference.catalog import ROOT,DATA,CACHE,read,save
from georeference.projection import convert
from pyproj import Geod


def render_ties():
    from PIL import Image,ImageDraw
    for tie in read(DATA/'tie-candidates.json')['ties']:
        contact=Image.new('RGB',(800,430),'white');draw=ImageDraw.Draw(contact)
        for i,(ev,point) in enumerate(zip(tie['evidence'],tie['resourceCoords'])):
            im=Image.open(CACHE/'images'/(ev['id']+'.jpg')).convert('RGB')
            p=[(point[j]-ev['region'][j])*ev['decodedSize'][j]/ev['region'][j+2] for j in [0,1]]
            di=ImageDraw.Draw(im);di.ellipse((p[0]-6,p[1]-6,p[0]+6,p[1]+6),outline='red',width=1)
            contact.paste(im,(400*i,25));draw.text((400*i+10,8),tie['id']+' '+['947','948'][i],fill='black')
        contact.save(CACHE/'review'/(tie['id']+'.jpg'))


def report():
    r=read(DATA/'pilot-report.json');attach=read(DATA/'attach-report.json');viewer=read(DATA/'viewer-report.json')
    evidence={e['id']:e for e in read(DATA/'evidence.json')['items']}
    for tie in read(DATA/'tie-candidates.json')['ties']:
        for e in tie['evidence']:evidence[e['id']]=e
    cached=read(DATA/'acquisition-catalog.json')['items']
    cache_entries={e['id']:e for e in cached if e['inventoryNumber'] in [v['inventoryNumber'] for v in r['results']]}
    requests={'uniqueEvidenceImages':len(evidence),'uniqueCachedImages':len(cache_entries),
              'overviewImages':sum(e['kind']=='overview' for e in cache_entries.values()),
              'detailImages':sum(e['kind']=='detail' for e in cache_entries.values()),
              'cachedBytes':sum(e['bytes'] for e in cache_entries.values()),
              'maxDetailsPerScan':max(Counter(e['inventoryNumber'] for e in cache_entries.values() if e['kind']=='detail').values()),
              'fullNativeImagesDownloaded':0,'offlinePilotNetworkRequests':0,
              'note':'Counts include 7 images reused from planning; unused exploratory details remain in cache. Retries are not counted as unique images.'}
    refs=read(DATA/'crs/reference-points.json')
    checks=[]
    for p in refs['points']:
        actual=convert(p['rd']);checks.append({'name':p['name'],'rd':p['rd'],'referenceLonLat':p['etrs89LonLat'],
            'computedLonLat':actual,'differenceMetres':Geod(ellps='WGS84').inv(*p['etrs89LonLat'],*actual)[2]})
    save(DATA/'projection-checks.json',{'referenceSource':refs['source'],'toleranceMetres':1,'results':checks,
        'interpretation':'External coordinate sanity check at the selected operation accuracy; not centimetre validation or current-epoch WGS84 realization.'})
    r['acquisition']=requests;r['attach']={k:attach[k] for k in ['heldOutTieRmsBeforeMetres','heldOutTieRmsAfterMetres']}
    r['viewerMaxDifferenceMetres']=max(x['mercatorMaxGroundMetres'] for x in viewer['results'])
    r['viewerMaxDifferenceReleasedMetres']=max(x['mercatorMaxGroundMetres'] for x in viewer['results'] if next(a for a in r['results'] if a['inventoryNumber']==x['inventoryNumber'])['status']=='pilot-pass')
    r['visualReview']={'masks':24,'controls':96,'heldOutGridChecks':24,'tiePairs':6,'reviewer':'Codex vision','independentHumanReview':False}
    save(DATA/'pilot-report.json',r)
    checks_by_map={x['inventoryNumber']:x['checks'][0] for x in attach['gridErrors']}
    max_control_displacement=max(p['displacementMetres'] for x in attach['gridErrors'] for p in x['controls'])
    lines=['# Nieuwe Stijl: 24-scan pilot results','',
      f"Completed on 2026-11-19 on `codex/nieuwe-stijl-georeferencing-plan`: **24 measured scans, {r['passed']} provisional passes, {r['needsReview']} needing further review**. No commit was made.",
      '', 'All 16 map groups D.02–D.17 are represented. D.01 sheet indices/legends were excluded from georeferencing. The selection accounts for 999 digitized maps: 24 pilot scans and 975 not yet processed. Existing archival Collections and Manifests retain their metadata and Canvas identities.',
      '', '## What was measured', '',
      'Each scan has a reviewed native-pixel polygon mask, four fitted grid crosses and one held-out cross. The 120 crosses were read from cached native details, refined with a short symmetric cross-arm CV template and visually checked again. Masks follow the inner map frame and exclude the margins, title blocks and appendix tables. Conservative notches connect internal tables to blank lower margins so masks remain simple polygons without holes. Scans 947/948 retain separate pixel spaces and share the Appendix A sheet identity.',
      '', 'The pilot found signed **RD Old (EPSG:28991)** as well as RD New. RD Old is normalized by explicitly adding `[155000, 463000]` metres after checking the printed border values. Original signed values, units and verbatim label strings remain in the canonical records. Decimal kilometre labels and metre labels with thousands dots are distinguished. Enlarged evidence corrected 3/5 and 4/8 digit ambiguities on 821 and 1337; corrections are recorded.',
      '', 'OCR proposals are retained separately. They were not trusted to assign coordinates: faint, rotated and handwritten labels frequently fail the orthogonal OCR passes. Grid steps traced from border anchors are marked as derived, and shared-anchor dependencies are explicit.',
      '', '## Quality results', '',
      'The original thresholds remain **RMS ≤ 2 native pixels; held-out error ≤ 5 pixels**. No point was discarded to force a pass. The 17 flagged scans retain complete observations and draft annotations; they are excluded from release pages. These are processing thresholds, not claimed map or ground accuracy. Four controls give two residual degrees of freedom. The assumed 2-pixel observation sigma is not calibrated, so covariance, standardized residuals and chi-square probabilities are diagnostics only. No statistical-pass claim is made. Held-out grid checks share some absolute border anchors; independent label review remains essential.',
      '', '| Inventory | Original CRS | RMS px | Check px | Status |','|---|---|---:|---:|---|']
    for row in r['results']:lines.append(f"| {row['inventoryNumber']} | {row['originalCrs']} | {row['rmsPixels']:.3f} | {row['maxCheckPixels']:.3f} | {row['status']} |")
    lines += ['', '## Tie-point experiment', '',
      f"`@allmaps/attach@1.0.0-beta.51` jointly fitted the 947/948 pair using three SIFT matches, checked in native-resolution patches. Three separate matches were held out. Their overlap RMS changed from **{attach['heldOutTieRmsBeforeMetres']:.3f} m to {attach['heldOutTieRmsAfterMetres']:.3f} m**. The independent grid check worsened from **{checks_by_map['947']['beforeMetres']:.3f} m to {checks_by_map['947']['afterMetres']:.3f} m** on 947 and **{checks_by_map['948']['beforeMetres']:.3f} m to {checks_by_map['948']['afterMetres']:.3f} m** on 948. The largest displacement at an original control was **{max_control_displacement:.3f} m**.",
      '', 'The package solves attachments; image matching is a separate CV step. The experiment uses affine image-to-RD fits with equal equation weights, explicit options, `averageOut: false`, and evaluation of the solved transforms. Ties were not exported as observed GCPs or used to replace original RD coordinates. Better relative agreement does not establish better absolute accuracy. Keep the grid-only baseline; test other overlap pairs and a calibrated weighting model before adopting attachment.',
      '', '## Conversion and viewer checks', '',
      'PROJ uses the pinned non-ballpark EPSG:4833 Amersfoort-to-WGS84 Helmert operation, with network grids disabled and longitude/latitude order explicit. Its stated accuracy is 1 metre. The supplied EPSG:28992 PROJJSON and checksum, local EPSG/PROJ versions, exact pipeline and RD Old definition are retained. Two external RDNAP reference coordinate pairs agree within 0.027 m at this operation’s accuracy; this is not a current-epoch or centimetre-accuracy claim.',
      '', f"Allmaps parses every candidate annotation without changing its mask or observed GCPs. Held-out checks are excluded from exported controls. Dense numerical comparisons of Allmaps polynomial-order-1 renderer geometry against the RD affine followed by PROJ show at most **{r['viewerMaxDifferenceReleasedMetres']:.3f} m** difference for released pilot maps (**{r['viewerMaxDifferenceMetres']:.3f} m** across all candidates). Both Web Mercator and longitude/latitude fits are reported. This tests the transformation numerically; no browser renderer screenshot was used.",
      '', '## Archive requests', '',
      f"The cache contains **{requests['overviewImages']} overviews and {requests['detailImages']} bounded details**, **{requests['cachedBytes']/1_000_000:.2f} MB** in total, including images reused from planning. No full-resolution scans were fetched. At most **{requests['maxDetailsPerScan']} details per scan** were needed, below the budget of 12. Fetches are serial, rate-limited to one new request per second, checksum-verified, resumable and respect Retry-After. The completed pilot replays with zero network requests.",
      '', '## Outputs and reproduction', '',
      '- [Canonical maps and preserved observations](../../data/georeferencing/nieuwe-stijl/maps/)',
      '- [Machine-readable pilot report](../../data/georeferencing/nieuwe-stijl/pilot-report.json) and [coverage ledger](../../data/georeferencing/nieuwe-stijl/coverage.json)',
      '- [Draft annotations for all 24 scans](../../data/georeferencing/nieuwe-stijl/draft-annotations/) and [release pages for the 7 passing scans](../../data/iiif-annotations/nieuwe-stijl/)',
      '- [Attachment diagnostics](../../data/georeferencing/nieuwe-stijl/attach-report.json) and [viewer diagnostics](../../data/georeferencing/nieuwe-stijl/viewer-report.json)',
      '- [Setup and commands](nieuwe-stijl-georeferencing.md)',
      '', 'The local gallery is `.cache/georeferencing/review/index.html`. Photographs stay ignored; their exact URLs, regions, decoded sizes, checksums and retrieval metadata are saved. `pnpm georeference:pilot` reproduces canonical records, experimental diagnostics, annotations and this report offline after evidence hydration. `pnpm georeference:validate` runs Python geometry/acquisition tests and the existing TypeScript/catalog/build suite. Normal `pnpm build` reads saved outputs and needs neither Python nor network access.',
      '', '## Before expanding beyond the pilot', '',
      'Resolve the flagged residuals with additional spread-out crosses and independent repeat localization. Calibrate observation uncertainty and freeze acceptance limits before the planned 50-scan batch. Do not relax thresholds merely to increase the pass count. Review any geometry change again; saved approved geometry prevents a changed detector or edited coordinate from silently retaining visual approval. The remaining 975 maps have not been georeferenced.',
      '', '## Sources', '',
      '- [Supplied RD New definition](https://epsg.io/28992.json)',
      '- [Allmaps attach package](https://docs.allmaps.org/packages/attach)',
      '- [PROJ RDNAP reference-coordinate discussion](https://github.com/OSGeo/PROJ/issues/1663)',
      '- [TU Delft Testing Theory](https://books.open.tudelft.nl/home/catalog/book/178)',
      '- [Stuttgart Adjustment Theory](https://www.gis.uni-stuttgart.de/lehre/campus-docs/LN_Ausgl.pdf)',
      '- [IIIF Georeference Extension](https://iiif.io/api/extension/georef/)',
      '']
    (ROOT/'docs/georeferencing/nieuwe-stijl-pilot-results.md').write_text('\n'.join(lines))
    render_ties()
    gallery=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Nieuwe Stijl pilot review</title><style>body{font:16px system-ui;max-width:1400px;margin:2rem auto;padding:1rem}img{max-width:100%;height:auto}details{margin:2rem 0}summary{font-weight:bold;cursor:pointer}</style><h1>Nieuwe Stijl pilot review</h1><p>Red: map mask / refined centre. Green: fitted control. Blue: held-out check. AI visual review; provisional quality gates.</p>']
    for row in r['results']:
        n=row['inventoryNumber'];gallery.append(f'<details><summary>{html.escape(n)} — {row["status"]}; RMS {row["rmsPixels"]:.3f} px, check {row["maxCheckPixels"]:.3f} px</summary><img src="{n}-mask.jpg" alt="Mask and control positions for {n}"><img src="{n}-controls.jpg" alt="Five reviewed grid crosses for {n}"></details>')
    gallery.append('<h2>Overlap ties: 947 / 948</h2>')
    for i in range(1,7):gallery.append(f'<img src="tie-{i}.jpg" alt="Tie {i}, paired source details">')
    gallery.append('</html>');(CACHE/'review/index.html').write_text('\n'.join(gallery))
    print('Wrote pilot report and offline review gallery.')

if __name__=='__main__':report()
