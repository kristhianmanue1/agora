"""Behavioral tests for local source transport; no provider calls."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from agora.source import FileSourceAdapter, SourceError, digest, encode_record
from agora.transform import snapshot, TransformError


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'source.txt'
        self.data = ('Inicio: prohibido publicar.\r\n' + 'Distractor á 😀\n' * 900 +
                     'Final: permiso sólo para datos ficticios.\n').encode()
        self.path.write_bytes(self.data)
        self.revision = digest(self.data)
        self.adapter = FileSourceAdapter(self.path, 'synthetic-large')

    def test_inventory_reconstructs_exact_large_unicode_source(self):
        inventory = self.adapter.inventory(self.revision, unit_bytes=101)
        pieces = []
        position = 0
        for unit in inventory['units']:
            self.assertEqual(unit['start_byte'], position)
            raw = self.data[position:unit['end_byte']]
            raw.decode('utf-8')
            self.assertLessEqual(len(raw), 101)
            self.assertEqual(digest(raw), unit['sha256'])
            pieces.append(raw)
            position = unit['end_byte']
        self.assertGreater(len(self.data), 4096)
        self.assertEqual(b''.join(pieces), self.data)
        self.assertTrue(inventory['inventory_complete'])
        self.assertFalse(inventory['content_delivered'])
        self.assertEqual(inventory['evidence_sufficiency'], 'unknown')

    def test_distant_passages_and_expansion_preserve_exact_offsets(self):
        first_end = self.data.index(b'\n') + 1
        last_start = self.data.index(b'Final:')
        result = self.adapter.fetch(self.revision, [(0, first_end), (last_start, len(self.data))])
        self.assertEqual(result['coverage'], 'partial')
        for span in result['spans']:
            raw = self.data[span['start_byte']:span['end_byte']]
            self.assertEqual(span['text'].encode(), raw)
            self.assertEqual(span['sha256'], digest(raw))
        expanded = self.adapter.fetch(self.revision, [(0, len(self.data))])
        self.assertEqual(expanded['coverage'], 'full')
        self.assertEqual(expanded['evidence_sufficiency'], 'unknown')
        self.assertEqual(expanded['spans'][0]['text'].encode(), self.data)

    def test_change_same_size_detected_after_inventory(self):
        self.adapter.inventory(self.revision)
        self.path.write_bytes(self.data.replace(b'Inicio', b'Otroxx', 1))
        with self.assertRaisesRegex(SourceError, 'source_revision_mismatch'):
            self.adapter.fetch(self.revision, [(0, 6)])
        new = self.adapter.fetch(digest(self.path.read_bytes()), [(0, 6)])
        self.assertEqual(new['spans'][0]['text'], 'Otroxx')

    def test_independent_source_content_and_envelope_limits(self):
        with self.assertRaisesRegex(SourceError, 'source_budget_exceeded'):
            FileSourceAdapter(self.path, 'x', 4096).inventory(self.revision)
        with self.assertRaisesRegex(SourceError, 'content_budget_exceeded'):
            self.adapter.fetch(self.revision, [(0, 20)], content_budget=19)
        result = self.adapter.fetch(self.revision, [(0, 20)], content_budget=20)
        size = len(encode_record(result))
        self.assertEqual(self.adapter.fetch(self.revision, [(0, 20)],
                                           envelope_budget=size), result)
        with self.assertRaisesRegex(SourceError, 'envelope_budget_exceeded'):
            self.adapter.fetch(self.revision, [(0, 20)], envelope_budget=size - 1)
        with self.assertRaisesRegex(SourceError, 'envelope_budget_exceeded'):
            self.adapter.inventory(self.revision, envelope_budget=1)

    def test_invalid_ranges_fail_without_partial_results(self):
        for ranges in ([], [(0, 0)], [(-1, 1)], [(0, len(self.data) + 1)],
                       [(0, 6), (5, 8)], [(10, 12), (0, 2)], [(True, 2)],
                       [(0, 6), (0, 6)], [(0, 2, 3)], [(0, 1)] * 257):
            with self.subTest(ranges=str(ranges)[:50]), self.assertRaises(SourceError):
                self.adapter.fetch(self.revision, ranges)
        offset = self.data.index('😀'.encode())
        with self.assertRaisesRegex(SourceError, 'range_splits_utf8'):
            self.adapter.fetch(self.revision, [(offset, offset + 1)])

    def test_invalid_source_identity_and_encoding(self):
        for content, error in ((b'', 'empty_source'), (b'\xff', 'invalid_utf8')):
            self.path.write_bytes(content)
            with self.assertRaisesRegex(SourceError, error):
                self.adapter.inventory(digest(content))
        with self.assertRaisesRegex(SourceError, 'invalid_revision'):
            self.adapter.inventory('latest')
        with self.assertRaisesRegex(SourceError, 'invalid_source_id'):
            FileSourceAdapter(self.path, '')

    def test_partition_of_four_byte_characters_and_unit_limit(self):
        data = ('😀' * 10).encode()
        self.path.write_bytes(data)
        units = self.adapter.inventory(digest(data), 4)['units']
        self.assertEqual(len(units), 10)
        self.path.write_bytes(b'x' * (16384 * 4 + 1))
        with self.assertRaisesRegex(SourceError, 'unit_limit_exceeded'):
            self.adapter.inventory(digest(self.path.read_bytes()), 4)

    def test_adjacent_ranges_can_cover_whole_source(self):
        self.path.write_bytes(b'abcdef')
        result = self.adapter.fetch(digest(b'abcdef'), [(0, 3), (3, 6)])
        self.assertEqual(result['coverage'], 'full')
        self.assertFalse(result['truncated'])

    def test_legacy_source_limit_remains_explicit(self):
        with self.assertRaisesRegex(TransformError, 'invalid_source_size'):
            snapshot(self.data, self.revision, 'x', [])

    def cli(self, *extra):
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / 'src'),
                   PYTHONDONTWRITEBYTECODE='1')
        return subprocess.run([sys.executable, '-m', 'agora.source', *extra,
                               '--source', str(self.path), '--source-id', 'synthetic',
                               '--sha256', self.revision], env=env, capture_output=True, text=True)

    def test_cli_inventory_fetch_and_exclusive_output(self):
        out = Path(self.temp.name) / 'inventory.json'
        p = self.cli('inventory', '--out', str(out))
        self.assertEqual(p.returncode, 0, p.stderr)
        inv = json.loads(out.read_bytes())
        self.assertTrue(inv['inventory_complete'])
        before = out.read_bytes()
        self.assertEqual(self.cli('inventory', '--out', str(out)).returncode, 2)
        self.assertEqual(out.read_bytes(), before)
        result = Path(self.temp.name) / 'fetch.json'
        p = self.cli('fetch', '--range', '0:6', '--out', str(result))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(result.read_bytes())['spans'][0]['text'], 'Inicio')
        self.assertEqual(json.loads(p.stdout)['model_calls'], 0)

    def test_cli_rejection_creates_no_output(self):
        out = Path(self.temp.name) / 'bad.json'
        for args in (('fetch', '--range', '0:20', '--content-budget', '19'),
                     ('inventory', '--envelope-budget', '1'),
                     ('fetch', '--range', '0:1', '--unit-bytes', '4')):
            p = self.cli(*args, '--out', str(out))
            self.assertEqual(p.returncode, 2)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
