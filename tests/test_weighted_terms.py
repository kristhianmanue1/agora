import json
import tempfile
import unittest
from pathlib import Path
from agora.weighted_terms import scores
from agora.passages import lexical_ranges
from agora.source import FileSourceAdapter,digest
from agora.subquestions import prepare_subquestions
from agora.plan_generation import generate

class WeightedTests(unittest.TestCase):
    def test_rare_term_outweighs_common_term(self):
        values=scores(['common','common','rare','common'],'common rare')
        self.assertGreater(values[2],values[0])
    def test_english_stop_words_do_not_create_matches(self):
        self.assertEqual(scores(['the and from','the what'],'the from what'),[0,0])
    def test_term_repetition_does_not_inflate_score(self):
        self.assertEqual(*scores(['rare rare rare','rare'],'rare'))
    def test_language_is_not_silently_translated(self):
        self.assertEqual(scores(['training labels collected'],'etiquetas entrenamiento'),[0])
    def test_stop_filter_preserves_content_in_span(self):
        raw=b'the rare\n\nthe common\n\nthe common'
        env={'spans':[{'text':raw.decode()}],'source':{'source_bytes':len(raw)}}
        ranges,info=lexical_ranges(env,'the rare common',8,1,ranking='idf')
        self.assertEqual(ranges,[(0,8)])
        self.assertEqual(raw[slice(*ranges[0])],b'the rare')
        self.assertEqual(info['method'],'lexical-paragraph-idf/v0.1')
    def test_new_plan_reproduces_without_changing_old_contract(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'s.txt';raw=b'rare\n\ncommon\n\ncommon';path.write_bytes(raw)
            adapter=FileSourceAdapter(path,'test');spec={'schema':'agora/subquestions-input/v1-experimental','questions':[{'id':'P1','query':'rare common','reference_ranges':[]}]}
            old=prepare_subquestions(adapter,digest(raw),spec,4,1)
            new=prepare_subquestions(adapter,digest(raw),spec,4,1,'paragraphs-idf')
            self.assertEqual(old['schema'],'agora/subquestions-plan/v1-experimental')
            self.assertEqual(new['schema'],'agora/subquestions-plan/v4-idf-experimental')
            def provider(system,user):
                return {'finish_reason':'stop','content':json.dumps({'parts':[{'id':'P1','status':'answer','answer':'rare','quotes':['rare']}]})}
            data=json.dumps(new).encode();r=generate(path,data,digest(data),'rare common',provider,scope_guard=True)
            self.assertEqual(r['execution_status'],'complete');self.assertTrue(r['requires_expansion'])
