import importlib.util
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('sync_na', ROOT / 'scripts/sync-nationaal-archief.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class ArchiveSourceTest(unittest.TestCase):
    def test_exact_inventory_mapping_and_undigitized_exclusion(self):
        ead = ET.parse(ROOT / 'data/nationaal-archief/2.16.5150.xml').getroot()
        section = next(c for c in ead.findall('archdesc/dsc/c') if sync.identifier(c, 'series_code') == 'D')
        snapshot = json.loads((ROOT / 'data/nationaal-archief/nieuwe-stijl.json').read_text())
        self.assertEqual(sync.component(section), snapshot['edition'])
        original = {sync.identifier(c, 'urn:uuid'): c.find('did/dao').get('href')
                    for c in section.iter('c') if c.find('did/dao') is not None}
        resolved = {c['uuid']: c['metsUrl'] for c in sync.walk(snapshot['edition']) if c.get('metsUrl')}
        self.assertEqual(original, resolved)
        self.assertEqual(len(original), 1009)
        self.assertEqual(set(original), set(snapshot['objects']))
        missing = {sync.identifier(c, 'urn:uuid') for c in section.iter('c')
                   if c.get('level') == 'file' and c.find('did/dao') is None}
        self.assertTrue(missing.isdisjoint(c['uuid'] for c in sync.walk(snapshot['edition'])))

    def test_preserves_mixed_content_and_normalized_dates(self):
        node = ET.fromstring('<did><unitdate normal="1995-04">april 1995</unitdate>'
                             '<unittitle>Maas <emph>kaart</emph> vervolg</unittitle></did>')
        fields = sync.metadata(node)
        self.assertIn({'label': 'Datering (ISO)', 'value': '1995-04'}, fields)
        self.assertIn({'label': 'Titel', 'value': 'Maas kaart vervolg'}, fields)

    def test_raw_mets_images_are_all_represented(self):
        snapshot = json.loads((ROOT / 'data/nationaal-archief/nieuwe-stijl.json').read_text())
        for obj in snapshot['objects'].values():
            mets = ET.fromstring(obj['metsXml'])
            physical = mets.findall("m:structMap[@TYPE='PHYSICAL']//m:div", sync.NS)
            ids = [d.get('ID') for d in physical if d.findall('m:fptr', sync.NS)]
            self.assertEqual(ids, [image['id'] for image in obj['images']])


if __name__ == '__main__':
    unittest.main()
