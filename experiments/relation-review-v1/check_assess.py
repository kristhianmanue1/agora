import json,tempfile,unittest
from pathlib import Path
from assess import assess

HERE=Path(__file__).parent
class AssessmentChecks(unittest.TestCase):
    def test_disagreements_preserved(self):
        result=assess(HERE)
        self.assertEqual(result['exact_matches'],7)
        self.assertEqual({d['id'] for d in result['disagreements']},{'C02','C08','D02'})
        self.assertFalse(result['semantic_admission'])
    def test_tampering_and_missing_answer_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            for name in ['freeze.json','request.json','review.json']:(p/name).write_bytes((HERE/name).read_bytes())
            original=(p/'request.json').read_bytes();(p/'request.json').write_bytes(original+b' ')
            with self.assertRaisesRegex(ValueError,'request_digest_mismatch'):assess(p)
            (p/'request.json').write_bytes(original)
            review=json.loads((p/'review.json').read_text());del review['response']['answers']['C01'];(p/'review.json').write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError,'answer_keys_mismatch'):assess(p)

if __name__=='__main__':unittest.main()
