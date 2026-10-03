import hashlib
import unittest
from selector import expand, paragraphs

class ExpansionChecks(unittest.TestCase):
    def state(self, raw, selected=(0,)):
        ps = paragraphs(raw)
        return {'source_sha256':hashlib.sha256(raw).hexdigest(),'question':'compare','ranges':[[ps[i][0],ps[i][1]] for i in selected]}
    def test_increment_preserves_and_links(self):
        raw = 'Alpha: café model.\n\nAlpha receives a sentence.\n\nAlpha beats Beta.\n\nUnrelated results.'.encode()
        start = self.state(raw)
        small = expand(raw,'compare',start,50)
        large = expand(raw,'compare',small,500)
        self.assertTrue(set(map(tuple,small['ranges'])) <= set(map(tuple,large['ranges'])))
        self.assertEqual(len(large['ranges']),3)
        self.assertEqual(large['ranges'],expand(raw,'compare',start,500)['ranges'])
        for a,b in large['ranges']:raw[a:b].decode()
    def test_changed_source_question_and_low_budget(self):
        raw=b'Alpha: model.\n\nAlpha input.';state=self.state(raw)
        for value,q,b in [(raw+b'x','compare',100),(raw,'different',100),(raw,'compare',1)]:
            with self.assertRaises(ValueError):expand(value,q,state,b)
    def test_duplicate_and_mid_paragraph(self):
        raw=b'Alpha: model.';state=self.state(raw)
        for ranges in [[[0,5]],state['ranges']*2,[[True,13]]]:
            with self.assertRaises(ValueError):expand(raw,'compare',dict(state,ranges=ranges),100)
    def test_no_inferred_link(self):
        raw=b'Alpha: model.\n\nThis system receives sentences.'
        self.assertEqual(len(expand(raw,'compare',self.state(raw),100)['ranges']),1)

if __name__=='__main__':unittest.main()
