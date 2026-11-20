import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/georeferencing'))
from georeference.timing import record_command

class TimingTests(unittest.TestCase):
    def test_records_measured_success_and_failure_without_estimated_tokens(self):
        with tempfile.TemporaryDirectory() as tmp, patch('georeference.timing.batch_dir',return_value=Path(tmp)):
            with patch('georeference.timing.perf_counter',side_effect=[10.0,12.5]):
                with record_command('batch-03','acquire'):pass
            with patch('georeference.timing.perf_counter',side_effect=[20.0,21.25]):
                with self.assertRaisesRegex(RuntimeError,'failed'):
                    with record_command('batch-03','measure'):raise RuntimeError('failed')
            value=json.loads((Path(tmp)/'processing.json').read_text())
            self.assertEqual([(r['elapsedSeconds'],r['success']) for r in value['commands']],[(2.5,True),(1.25,False)])
            self.assertNotIn('tokenUsage',value)
            self.assertNotIn('visionTokenUsage',value)
            self.assertIsNone(value['completedAt'])
            self.assertIsNone(value['elapsedSeconds'])
