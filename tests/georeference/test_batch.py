import sys, unittest, copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/georeferencing'))
from georeference.batch import batch_dir,validate_selection
from georeference.catalog import DATA,read
from georeference.geometry import validate_mask,adjust,to_pixel
from georeference.pilot import geometry_snapshot,CONFIG
import numpy as np
from jsonschema import Draft202012Validator

class BatchTests(unittest.TestCase):
    def test_series_remainder_is_24_without_crossing_into_d03(self):
        selected=read(batch_dir('batch-02')/'selection.json')
        previous=read(batch_dir('batch-01')/'selection.json')['records']
        prior={r['id'] for r in previous}
        catalog=read(DATA/'selection.json')['records']
        expected=[r for r in catalog if not r['pilot'] and r['id'] not in prior and r['series']=='D.02']
        self.assertEqual(validate_selection(selected),expected)
        self.assertEqual(len(expected),24)
        self.assertEqual(selected['series'],'D.02')
        self.assertEqual({r['id'] for r in catalog if r['series']=='D.02'},
                         {r['id'] for r in catalog if r['series']=='D.02' and (r['pilot'] or r['id'] in prior)} | {r['id'] for r in expected})
        for key,value in [('selectedCount',50),('selectedCount',True),('series','D.03')]:
            bad=copy.deepcopy(selected);bad[key]=value
            with self.assertRaises(ValueError):validate_selection(bad)
    def test_full_series_contains_all_remaining_d03_maps(self):
        selected=read(batch_dir('batch-03')/'selection.json')
        records=validate_selection(selected)
        self.assertEqual((selected['mode'],selected['series'],len(records)),('whole-series','D.03',81))
        self.assertEqual(records,[r for r in read(DATA/'selection.json')['records'] if r['series']=='D.03' and not r['pilot']])
        for change in ['incomplete','reordered','wrong-series']:
            bad=copy.deepcopy(selected)
            if change=='incomplete':bad['records'].pop();bad['selectedCount']-=1
            elif change=='reordered':bad['records'].reverse()
            else:bad['series']='D.04'
            with self.assertRaises(ValueError):validate_selection(bad)
    def test_next_fifty_exclude_pilot_and_indices(self):
        selected=read(batch_dir('batch-01')/'selection.json');actual=validate_selection(selected)
        expected=[r for r in read(DATA/'selection.json')['records'] if not r['pilot']][:50]
        self.assertEqual(actual,expected)
        for modification in ['duplicate','source','pilot']:
            bad=copy.deepcopy(selected)
            if modification=='duplicate':bad['records'][1]=bad['records'][0]
            elif modification=='source':bad['sourceSha256']='changed'
            else:bad['records'][0]['pilot']=True
            with self.assertRaises(ValueError):validate_selection(bad)
    def test_all_masks_and_held_out_checks_are_reproducible(self):
        maps=[];approved={}
        validator=Draft202012Validator(read(DATA/'schemas/map.schema.json'))
        for selection_path in sorted((DATA/'batches').glob('batch-*/selection.json')):
            selection=read(selection_path);name=selection['batchId'];count=len(selection['records'])
            folder=batch_dir(name);approved.update(read(folder/'geometry-review.json')['maps'])
            batch=[read(p) for p in (folder/'maps').glob('*.json')];self.assertEqual(len(batch),count);maps.extend(batch)
        self.assertEqual(len(maps),975)
        for m in maps:
            validator.validate(m)
            evidence_ids={e['id'] for e in m['evidence']}
            anchor_ids={a['id'] for a in m['anchors']}
            for point in m['points']:
                self.assertEqual([a['axis'] for a in point['coordinateDerivation']['axes']],['easting','northing'])
                self.assertLessEqual(set(point['coordinateDerivation']['anchorIds']),anchor_ids)
                self.assertTrue(all(a['evidenceId'] in evidence_ids for a in point['coordinateDerivation']['axes']))
            validate_mask(m['mask']['resourceMask'],m['nativeSize'])
            self.assertEqual(geometry_snapshot(m['mask'],m['points']),approved[m['id']])
            controls=[p for p in m['points'] if p['role']=='control'];checks=[p for p in m['points'] if p['role']=='check']
            self.assertEqual((len(controls),len(checks)),(4,1))
            fit=adjust([p['rdNew'] for p in controls],[p['resourceCoords'] for p in controls])
            self.assertAlmostEqual(fit['rmsPixels'],m['adjustment']['rmsPixels'])
            err=float(np.linalg.norm(np.array(checks[0]['resourceCoords'])-to_pixel(fit,checks[0]['rdNew'])))
            self.assertAlmostEqual(err,m['adjustment']['heldOutChecks'][0]['errorPixels'])
            self.assertFalse(m['adjustment']['heldOutChecks'][0]['usedInFit'])
            self.assertFalse(m['quality']['releaseEligible'])
            self.assertEqual(m['quality']['humanReview'],'pending')
            self.assertEqual('rms-above-2px' in m['quality']['reasons'],fit['rmsPixels']>CONFIG['rmsPixelsLimit'])
            self.assertNotIn('geometry-review-required',m['quality']['reasons'])
    def test_cached_evidence_within_request_budgets(self):
        for selection_path in sorted((DATA/'batches').glob('batch-*/selection.json')):
            selection=read(selection_path);name=selection['batchId'];count=len(selection['records'])
            evidence=read(batch_dir(name)/'evidence.json')['items']
            self.assertEqual(len({e['id'] for e in evidence}),len(evidence))
            self.assertEqual(sum(e['kind']=='overview' for e in evidence),count)
            for e in evidence:
                if e['kind']=='detail':self.assertLessEqual(np.prod(e['decodedSize']),1800000)
            for n in {e['inventoryNumber'] for e in evidence}:
                self.assertLessEqual(sum(e['inventoryNumber']==n and e['kind']=='detail' for e in evidence),12)
