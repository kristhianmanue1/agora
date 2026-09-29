import unittest
from agora.function_retrieval import candidates, select
from agora.subquestions import merge_ranges

class FunctionRetrievalTests(unittest.TestCase):
    def run_selection(self,text,queries,budget=200,top_k=1):
        full={'spans':[{'text':text}]}
        return select(full,[{'id':str(i),'query':q} for i,q in enumerate(queries)],budget,top_k,merge_ranges)

    def test_exact_utf8_and_heading(self):
        text='7.1 Área médica\n \n1. Aprobar normas.\n \n2. Comprar equipo.\n'
        units=candidates(text)
        self.assertEqual(len(units),2)
        for u in units:
            self.assertEqual(text.encode()[u['ranges'][-1][0]:u['ranges'][-1][1]].decode(),u['text'])
        self.assertIn('Área médica',units[1]['heading'])

    def test_shared_remainder_and_limit(self):
        text='1. Alfa '+('dato '*12)+'\n\n2. Beta.\n'
        ranges,reports=self.run_selection(text,['Alfa','Beta'],90)
        self.assertTrue(all(r['selected_ranges'] for r in reports))
        self.assertLessEqual(sum(b-a for a,b in ranges),90)
        ranges,reports=self.run_selection(text,['Alfa','Beta'],10)
        self.assertFalse(reports[0]['selected_ranges'])

    def test_no_heading_inherited_across_pdf_pages(self):
        text='7.1 Área alfa\n\n1. Alfa.\n\n[PDF page 2]\n\n2. Beta.'
        self.assertEqual(candidates(text)[1]['heading'],'')

    def test_empty_or_unstructured_never_claims_coverage(self):
        ranges,reports=self.run_selection('Texto sin números.',['Texto'])
        self.assertFalse(ranges)
        self.assertEqual(reports[0]['candidate_status'],'no_candidates_within_budget')

    def test_deduplication_and_determinism(self):
        text='7.1 Alfa\n\n1. Aprobar normas.\n\n2. Revisar normas.'
        a=self.run_selection(text,['normas','normas'],100,2)
        self.assertEqual(a,self.run_selection(text,['normas','normas'],100,2))
        self.assertEqual(sum(b-a for a,b in a[0]),sum(b-a for a,b in merge_ranges(a[0])))
