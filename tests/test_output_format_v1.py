import copy
import importlib.util
import json
from pathlib import Path
import unittest
BASE=Path(__file__).resolve().parents[1]/'experiments/output-format-v1'
spec=importlib.util.spec_from_file_location('output_format_v1',BASE/'adapter.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class OutputFormatTests(unittest.TestCase):
    def test_valid_json_preserved_byte_for_byte(self):
        text=' \n{ "x": "á`", "n": 1.00 }\t'
        r=m.propose(text);self.assertEqual(r['status'],'unchanged');self.assertEqual(r['candidate_content'],text);self.assertEqual(r['edits'],[])
    def test_observed_response_repaired_only_outside_object(self):
        original=json.loads((BASE.parent/'issue-flow-v4/result-glm-01.json').read_text())['original_response']['content']
        r=m.propose(original);self.assertEqual(r['status'],'repair_candidate');self.assertEqual(r['original_content'],original)
        self.assertEqual(r['candidate_content'],original[:-1]);self.assertEqual(m.verify(r)['fields']['owner']['observed_value'],'Lina')
    def test_utf8_offsets_and_internal_backtick_preserved(self):
        text='{"x":"á`"}\n`\t';r=m.propose(text);edit=r['edits'][0];raw=text.encode()
        self.assertEqual(raw[edit['start_byte']:edit['end_byte']],b'`')
        self.assertEqual(r['candidate_content'].encode(),raw[:edit['start_byte']]+raw[edit['end_byte']:])
        self.assertEqual(m.verify(r),{'x':'á`'})
    def test_ambiguous_suffixes_rejected(self):
        for text in ('{} {}','{} explanation','{} //comment','{} ```','{} ` {}','{} ` do this','{}\u00a0'):
            with self.subTest(text=text),self.assertRaises(ValueError):m.propose(text)
    def test_prefix_fences_and_truncated_json_rejected(self):
        for text in ('answer: {}','```json\n{}\n```','{"x":','{"x":1,}`',''):
            with self.subTest(text=text),self.assertRaises(ValueError):m.propose(text)
    def test_duplicate_keys_and_nonfinite_rejected(self):
        for text in ('{"x":1,"x":2}`','{"x":NaN}`','{"x":Infinity}','{"x":1e999}`'):
            with self.subTest(text=text),self.assertRaises(ValueError):m.propose(text)
    def test_arrays_scalars_not_repaired(self):
        for text in ('[]`','null','"{}"`','1`'):
            with self.subTest(text=text),self.assertRaises(ValueError):m.propose(text)
    def test_changed_value_receipt_rejected_even_with_new_hash(self):
        r=m.propose('{"x":1}`');r['candidate_content']='{"x":2}';r['candidate_sha256']=m.sha(r['candidate_content'])
        with self.assertRaisesRegex(ValueError,'receipt_mismatch'):m.verify(r)
    def test_changed_policy_or_offsets_rejected(self):
        original=m.propose('{}`')
        for key,value in [('policy','permissive'),('status','unchanged'),('edits',[])]:
            r=copy.deepcopy(original);r[key]=value
            with self.assertRaisesRegex(ValueError,'receipt_mismatch'):m.verify(r)
    def test_size_and_invalid_unicode_rejected(self):
        for text in (' '*m.MAX_BYTES+'{}','{"x":"\ud800"}'):
            with self.assertRaises(ValueError):m.propose(text)
