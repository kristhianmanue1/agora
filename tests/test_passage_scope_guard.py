import json
import tempfile
import unittest
from pathlib import Path
from agora.passages import query_passages
from agora.source import FileSourceAdapter, digest

class ScopeGuardTests(unittest.TestCase):
    def test_partial_answer_cannot_close_source_question(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.txt'
            data = b'Grammar evaluation exists.\n\nUnrelated text.\n\nPOS tags determine the method.'
            path.write_bytes(data)
            calls = []
            def provider(system, user):
                calls.append((system, json.loads(user)))
                return {'finish_reason': 'stop', 'content': json.dumps({'parts': [
                    {'id':'P1','status':'answer','answer':'The document gives no further details.',
                     'quotes':['Grammar evaluation exists.']}]})}
            result = query_passages(FileSourceAdapter(path,'fixture'),digest(data),'Grammar?',provider,
                mode='reference', ranges=[(0,26)], scope_guard=True)
            self.assertEqual(result['schema'],'agora/passage-query/v0.3')
            self.assertEqual(result['answer_status'],'candidate_requires_expansion')
            self.assertTrue(result['requires_expansion'])
            self.assertFalse(result['document_absence_established'])
            self.assertEqual(calls[0][1]['reading_scope'],'selected_passages')
            self.assertIn('NOT the whole document', calls[0][0])

    def test_full_read_does_not_claim_semantic_certainty(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'source.txt';data=b'No owner was assigned.';p.write_bytes(data)
            def provider(system,user):
                return {'finish_reason':'stop','content':json.dumps({'parts':[
                    {'id':'P1','status':'answer','answer':'No owner assigned.', 'quotes':[data.decode()]}]})}
            r=query_passages(FileSourceAdapter(p,'fixture'),digest(data),'owner',provider,
                mode='source',scope_guard=True)
            self.assertEqual(r['answer_status'],'candidate')
            self.assertFalse(r['requires_expansion'])
            self.assertEqual(r['semantic_support'],'not_verified')
            self.assertFalse(r['document_absence_established'])

if __name__=='__main__': unittest.main()
