import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts/georeferencing'))
from georeference.catalog import DATA, read
from georeference.pilot import coordinate_dependencies


class BorderAxisTests(unittest.TestCase):
    def test_same_number_can_label_different_axes_on_the_same_sheet(self):
        review = read(DATA / 'batches/batch-07/reviews.json')['maps']['1123']
        evidence = {key: {'id': key} for key in review['labels']}
        p1 = coordinate_dependencies(review, [42500, 43000], evidence)
        p5 = coordinate_dependencies(review, [43000, 42500], evidence)
        self.assertEqual([a['resultMetres'] for a in p1], [42500, 43000])
        self.assertIn('left border', p1[0]['method'])
        self.assertIn('top border', p5[1]['method'])
        self.assertEqual(p5[0]['evidenceId'], 'br')
        bad = copy.deepcopy(review)
        bad['pointBorderAnchors'][0]['axes'][0]['signedSteps'] = 1
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            coordinate_dependencies(bad, [42500, 43000], evidence)


if __name__ == '__main__':
    unittest.main()
