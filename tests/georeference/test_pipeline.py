import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/georeferencing'))
import unittest
import tempfile
from unittest.mock import patch
from io import BytesIO
from urllib.error import HTTPError
import json
import numpy as np
import cv2
from PIL import Image
from pyproj import Geod, Transformer, CRS
from jsonschema import Draft202012Validator
from georeference.catalog import DATA,read
from georeference.geometry import adjust,to_pixel,to_rd,validate_mask
from georeference.measure import refine_cross
from georeference.projection import normalize_rd,convert,definition,TRANSFORMER
from georeference.acquire import original_point,region_request,ImageCache,retry_seconds

class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.rd=np.array([[100000,430000],[104000,430000],[104000,432000],[100000,432000],[102000,431000]],float)
        self.linear=np.array([[.7,.8],[.82,-.68]])
        self.pixels=self.rd@self.linear.T+[-400000,250000]
    def test_rotated_sheared_affine_and_covariance(self):
        noise=np.array([[1,-1],[-1,1],[1,.5],[-1,-.5],[0,0]])
        f=adjust(self.rd,self.pixels+noise)
        self.assertEqual(f['degreesOfFreedom'],4)
        self.assertIsNone(f['statisticalPass'])
        np.testing.assert_allclose(to_rd(f,to_pixel(f,self.rd)),self.rd,atol=1e-8)
        self.assertLess(f['rmsPixels'],2)
    def test_three_points_are_not_accuracy_validation(self):
        f=adjust(self.rd[:3],self.pixels[:3]);self.assertEqual(f['degreesOfFreedom'],0)
        self.assertIsNone(f['chiSquareUpperTailAssumingSigma']);self.assertTrue(f['minimalControl'])
    def test_collinear_and_near_collinear(self):
        for rd in [np.array([[0,0],[1,1],[2,2]]),np.array([[0,0],[1,1],[2,2.000001]])]:
            with self.assertRaises(ValueError):adjust(rd,rd)
    def test_digit_error_detected_but_uniform_offset_not(self):
        bad=self.rd.copy();bad[0,0]+=1000
        self.assertGreater(adjust(bad,self.pixels)['rmsPixels'],50)
        a=adjust(self.rd,self.pixels);b=adjust(self.rd+[1000,0],self.pixels)
        self.assertAlmostEqual(a['rmsPixels'],b['rmsPixels'],places=7)
        # This is why separate absolute-label checks are mandatory.
    def test_mask_concavity_and_invalid_polygons(self):
        validate_mask([[0,0],[10,0],[10,6],[6,6],[6,10],[0,10]],[10,10])
        for p in [[[0,0],[10,10],[10,0],[0,10]],[[0,0],[11,0],[0,10]],[[0,0],[0,10],[10,0]]]:
            with self.assertRaises(ValueError):validate_mask(p,[10,10])
    def test_explicit_printed_label_interpretation(self):
        from georeference.pilot import reviewed_label_value, coordinate_dependencies
        r={'printedUnit':'kilometre','labelInterpretations':{'1040':{'metres':104000,'reason':'Visually confirmed against 104.5 and opposite border'}},'points':[['tl',1,1,104000,419000],['tr',2,1,104500,419000]],'labels':{'tl':['1040','104.5','419.0']}}
        self.assertEqual(reviewed_label_value('1040',r),104000)
        self.assertEqual(reviewed_label_value('1040',{'printedUnit':'kilometre'}),1040000)
        axes=coordinate_dependencies(r,[104000,419000],{'tl':{'id':'source'}})
        self.assertEqual(axes[0]['borderText'],'1040')
        self.assertEqual(axes[0]['borderValueMetres'],104000)
        self.assertEqual(axes[0]['gridIntervalMetres'],500)

    def test_missing_axis_requires_traceable_external_border_anchor(self):
        from georeference.pilot import coordinate_dependencies
        r={'printedUnit':'kilometre','points':[['tl',1,1,68000,427400],['tr',2,1,68200,427200]],'labels':{'tl':['427.4','427.2']}}
        ev={'tl':{'id':'own-northing'}}
        with self.assertRaisesRegex(ValueError,'Missing reviewed easting'):
            coordinate_dependencies(r,[68200,427200],ev)
        a={'axis':'easting','verbatim':'68.0','valueMetres':68000,'printedUnit':'kilometre','sourceInventoryNumber':'1459','evidence':{'id':'external-native-crop'},'method':'Visually matched printed grid in another edition'}
        r['externalBorderAnchors']=[a]
        axes=coordinate_dependencies(r,[68200,427200],ev)
        self.assertEqual(axes[0]['signedSteps'],1)
        self.assertEqual(axes[0]['sourceInventoryNumber'],'1459')
        self.assertEqual(axes[0]['evidenceId'],'external-native-crop')
        self.assertTrue(axes[0]['externalAnchor'])
        self.assertEqual(axes[1]['evidenceId'],'own-northing')
        a['valueMetres']=69000
        with self.assertRaisesRegex(ValueError,'disagrees with printed label'):
            coordinate_dependencies(r,[68200,427200],ev)
        a['valueMetres']=68000
        a['evidence']={}
        with self.assertRaisesRegex(ValueError,'requires source, evidence'):
            coordinate_dependencies(r,[68200,427200],ev)

    def test_corner_title_masks_exclude_title_and_keep_map(self):
        from georeference.pilot import mask_for
        record={'inventoryNumber':'test','imageService':{'width':1000,'height':800}}
        frame=[[100,100],[900,100],[900,700],[100,700]]
        ev={c:{'region':[0,0,1000,800],'decodedSize':[1000,800]} for c in ['tl','tr','br','bl']}
        cases={'tr':([700,200],[800,150],[800,400]),'tl':([300,200],[200,150],[200,400]),
               'br':([700,600],[800,650],[800,400]),'bl':([300,600],[200,650],[200,400])}
        for corner,(notch,title,cartography) in cases.items():
            with self.subTest(corner=corner),patch('georeference.pilot.read',return_value={'resourceFrame':frame}):
                mask=mask_for(record,{'titleNotch':[corner,*notch]},ev)['resourceMask']
                polygon=np.asarray(mask,np.float32)
                self.assertLess(cv2.pointPolygonTest(polygon,tuple(title),False),0)
                self.assertGreater(cv2.pointPolygonTest(polygon,tuple(cartography),False),0)
                self.assertGreater(cv2.pointPolygonTest(polygon,(500,400),False),0)
    def test_side_titles_preserve_cartography_above_and_below(self):
        from georeference.pilot import mask_for
        record={'inventoryNumber':'test','imageService':{'width':1000,'height':800}}
        frame=[[100,100],[900,110],[910,700],[110,690]]
        ev={'detail':{'region':[0,200,1000,400],'decodedSize':[500,200]}}
        for side,bounds,title,keep in [('left',[50,50,150,100],[200,350],[200,250]),
                                       ('right',[350,50,450,100],[800,350],[800,250])]:
            review={'sideTitleNotch':{'side':side,'evidenceKey':'detail','bounds':bounds}}
            with self.subTest(side=side),patch('georeference.pilot.read',return_value={'resourceFrame':frame}):
                polygon=np.asarray(mask_for(record,review,ev)['resourceMask'],np.float32)
                self.assertLess(cv2.pointPolygonTest(polygon,tuple(title),False),0)
                for p in [keep,[keep[0],500],[500,350]]:
                    self.assertGreater(cv2.pointPolygonTest(polygon,tuple(p),False),0)
    def test_caption_with_separate_title_retains_map_between_notches(self):
        from georeference.pilot import mask_for
        record={'inventoryNumber':'test','imageService':{'width':1000,'height':800}}
        ev={c:{'region':[0,0,1000,800],'decodedSize':[1000,800]} for c in ['tl','bl']}
        for corner,y,title in [('tl',300,[200,200]),('bl',600,[200,650])]:
            with self.subTest(corner=corner),patch('georeference.pilot.read',return_value={'resourceFrame':[[100,100],[900,100],[900,700],[100,700]]}):
                review={'titleNotch':[corner,300,y],'topLeftCaptionNotch':[500,150]}
                polygon=np.asarray(mask_for(record,review,ev)['resourceMask'],np.float32)
                for p in [title,[400,125]]:self.assertLess(cv2.pointPolygonTest(polygon,tuple(p),False),0)
                for p in [[400,250],[600,125],[200,400]]:self.assertGreater(cv2.pointPolygonTest(polygon,tuple(p),False),0)
    def test_side_title_and_top_caption_can_coexist(self):
        from georeference.pilot import mask_for
        record={'inventoryNumber':'test','imageService':{'width':1000,'height':800}}
        ev={'tl':{'region':[0,0,1000,800],'decodedSize':[1000,800]}}
        review={'sideTitleNotch':{'side':'right','evidenceKey':'tl','bounds':[700,300,900,400]},
                'topLeftCaptionNotch':[500,150]}
        with patch('georeference.pilot.read',return_value={'resourceFrame':[[100,100],[900,100],[900,700],[100,700]]}):
            polygon=np.asarray(mask_for(record,review,ev)['resourceMask'],np.float32)
            for p in [[400,125],[800,350]]:self.assertLess(cv2.pointPolygonTest(polygon,tuple(p),False),0)
            for p in [[200,250],[800,250],[800,500],[600,125]]:self.assertGreater(cv2.pointPolygonTest(polygon,tuple(p),False),0)
    def test_top_right_caption_preserves_map_below_and_left(self):
        from georeference.pilot import mask_for
        record={'inventoryNumber':'test','imageService':{'width':1000,'height':800}}
        ev={c:{'region':[0,0,1000,800],'decodedSize':[1000,800]} for c in ['tr','br']}
        review={'titleNotch':['br',700,600],'topRightCaptionNotch':[750,180]}
        with patch('georeference.pilot.read',return_value={'resourceFrame':[[100,100],[900,110],[910,700],[110,690]]}):
            polygon=np.asarray(mask_for(record,review,ev)['resourceMask'],np.float32)
            for p in [[800,140],[800,650]]:self.assertLess(cv2.pointPolygonTest(polygon,tuple(p),False),0)
            for p in [[800,250],[650,140],[500,400]]:self.assertGreater(cv2.pointPolygonTest(polygon,tuple(p),False),0)
    def test_cv_cross_arms_ignore_arrow_tip(self):
        im=np.full((81,81,3),240,np.uint8);centre=np.array([40.,40.]);angles=[.52,.52+np.pi/2]
        directions=[np.array([np.cos(a),np.sin(a)]) for a in angles]
        for d in directions:cv2.line(im,tuple(np.rint(centre-d*13).astype(int)),tuple(np.rint(centre+d*13).astype(int)),(20,20,20),2)
        p,record=refine_cross(im,[41.5,39.2],directions)
        self.assertTrue(record['accepted']);self.assertLess(np.linalg.norm(np.array(p)-centre),1)

class ProjectionTests(unittest.TestCase):
    def test_printed_units_and_separators_are_explicit(self):
        from georeference.labels import parse_grid_label
        self.assertEqual(parse_grid_label('129.2','kilometre'),129200)
        self.assertEqual(parse_grid_label('-386','hectometre'),-38600)
        self.assertEqual(parse_grid_label('-52.800','metre'),-52800)
        self.assertEqual(parse_grid_label('+53000','metre'),53000)
        with self.assertRaises(ValueError):parse_grid_label('129.2','metre')

    def test_external_reference_coordinates_not_only_roundtrip(self):
        refs=read(DATA/'crs/reference-points.json')
        for p in refs['points']:
            actual=convert(p['rd']);error=Geod(ellps='WGS84').inv(*p['etrs89LonLat'],*actual)[2]
            self.assertLess(error,refs['toleranceMetres'])
    def test_rd_old_is_explicit_and_matches_epsg(self):
        old=[-54000,-28400];new=normalize_rd(old,'EPSG:28991')
        self.assertEqual(new,[101000,434600]);self.assertEqual(old,[-54000,-28400])
        expected=Transformer.from_crs(28991,28992,always_xy=True).transform(*old)
        np.testing.assert_allclose(new,expected,atol=1e-7)
    def test_axis_and_thousandfold_errors_rejected(self):
        for p in [[430000,100000],[100,430],[100000000,430000000]]:
            with self.assertRaises(ValueError):convert(p)
    def test_pinned_nonballpark_no_missing_grids(self):
        d=definition();self.assertFalse(d['networkEnabled']);self.assertFalse(d['ballpark']);self.assertEqual(d['gridFiles'],[])
        self.assertIn('helmert',d['pipeline']);self.assertEqual(d['axisOrder'],['longitude','latitude'])

class AcquisitionTests(unittest.TestCase):
    def test_resize_and_inverse_rotation_use_actual_dimensions(self):
        ev={'region':[1000,2000,600,400],'decodedSize':[300,200]}
        self.assertEqual(original_point([150,50],ev),[1300,2100])
        ev['inverseLocalAffine']=[[0,-1,300],[1,0,0]]
        self.assertEqual(original_point([50,150],ev),[1300,2100])
    def test_bounded_details_preserve_query_service(self):
        r={'imageService':{'id':'https://example.org/iip?IIIF=x.jp2','width':8000,'height':5000,'maxWidth':1500}}
        url,rect=region_request(r,[7000,4000,5000,4000])
        self.assertEqual(rect,[7000,4000,1000,1000]);self.assertIn('?IIIF=x.jp2/7000,4000',url)
    def test_retry_after_dates(self):
        self.assertEqual(retry_seconds('12'),12)
        self.assertEqual(retry_seconds('Thu, 01 Jan 1970 00:01:00 GMT',0),60)
        self.assertEqual(retry_seconds('bad'),0)
    def test_cache_rate_limits_retries_and_corruption(self):
        payload=BytesIO();Image.new('RGB',(10,10),'white').save(payload,format='JPEG');body=payload.getvalue()
        class Response(BytesIO):
            headers={}
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        clock=[100.0];requests=[]
        def sleep(seconds):clock[0]+=seconds
        def request(*args,**kwargs):
            requests.append(clock[0])
            if len(requests)==1:raise HTTPError('x',429,'busy',{'Retry-After':'7'},None)
            return Response(body)
        r={'id':'test','inventoryNumber':'test'}
        with tempfile.TemporaryDirectory() as td,patch('georeference.acquire.urlopen',side_effect=request),patch('georeference.acquire.time.time',side_effect=lambda:clock[0]),patch('georeference.acquire.time.sleep',side_effect=sleep):
            c=ImageCache(td);a,path=c.get(r,'https://example.org/a',[0,0,10,10]);c.get(r,'https://example.org/b',[0,0,10,10])
            self.assertGreaterEqual(requests[1]-requests[0],7);self.assertGreaterEqual(requests[2]-requests[1],1)
            offline=ImageCache(td,offline=True);offline.get(r,'https://example.org/a',[0,0,10,10]);self.assertEqual(offline.network_requests,0)
            path.write_bytes(b'broken')
            with self.assertRaises(ValueError):offline.get(r,'https://example.org/a',[0,0,10,10])
    def test_interrupted_download_and_budget(self):
        r={'id':'test','inventoryNumber':'test'}
        with tempfile.TemporaryDirectory() as td,patch('georeference.acquire.urlopen',side_effect=OSError('interrupted')),patch('georeference.acquire.time.sleep'):
            c=ImageCache(td)
            with self.assertRaises(OSError):c.get(r,'https://example.org/a',[0,0,10,10])
            self.assertEqual(c.network_requests,5);self.assertEqual(list((Path(td)/'images').glob('*.json')),[])
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'images';p.mkdir()
            for i in range(12):(p/f'{i}.json').write_text(json.dumps({'mapId':'test','kind':'detail'}))
            with self.assertRaisesRegex(ValueError,'budget'):ImageCache(td).get(r,'https://example.org/a',[0,0,10,10])

class PilotTests(unittest.TestCase):
    def test_all_selected_maps_accounted_for(self):
        selection=read(DATA/'selection.json');ledger=read(DATA/'coverage.json')
        self.assertEqual(len(selection['records']),999);self.assertEqual(len(selection['excluded']),10)
        self.assertEqual(len(set(r['id'] for r in selection['records'])),999)
        self.assertFalse(any(r['series']=='D.01' for r in selection['records']))
        self.assertEqual(sum(r['status']=='not-in-pilot' for r in ledger['records']),975)
    def test_canonical_schema_and_geographic_evidence(self):
        schema=read(DATA/'schemas/map.schema.json');validator=Draft202012Validator(schema)
        maps=list((DATA/'maps').glob('*.json'));self.assertEqual(len(maps),24)
        for path in maps:
            m=read(path);validator.validate(m);validate_mask(m['mask']['resourceMask'],m['nativeSize'])
            self.assertEqual(len([p for p in m['points'] if p['role']=='control']),4)
            self.assertEqual(len([p for p in m['points'] if p['role']=='check']),1)
            self.assertEqual(m['adjustment']['degreesOfFreedom'],2)
            ids={e['id'] for e in m['evidence']}
            for p in m['points']:
                self.assertIn(p['evidenceId'],ids)
                self.assertEqual(normalize_rd(p['originalProjected']['coordinates'],p['originalProjected']['crs']),p['rdNew'])
                np.testing.assert_allclose(convert(p['rdNew']),p['geo'],atol=1e-10)
                for axis, derivation in enumerate(p['coordinateDerivation']['axes']):
                    self.assertIn(derivation['evidenceId'],ids)
                    self.assertEqual(derivation['axis'],['easting','northing'][axis])
                    self.assertEqual(derivation['borderValueMetres']+derivation['signedSteps']*derivation['gridIntervalMetres'],p['originalProjected']['coordinates'][axis])
                    self.assertEqual(derivation['resultMetres'],p['originalProjected']['coordinates'][axis])
            if m['quality']['releaseEligible']:
                self.assertLessEqual(m['adjustment']['rmsPixels'],2)
                self.assertLessEqual(max(c['errorPixels'] for c in m['adjustment']['heldOutChecks']),5)
    def test_ties_are_held_out_and_separate(self):
        ties=read(DATA/'tie-candidates.json')['ties'];self.assertEqual(sum(t['role']=='fit' for t in ties),3)
        self.assertTrue(all(t['visualReview']=='accepted' for t in ties))
        self.assertEqual(sum(t['role']=='check' for t in ties),3)
        report=read(DATA/'attach-report.json');self.assertFalse(report['options']['averageOut'])

if __name__=='__main__':unittest.main()
