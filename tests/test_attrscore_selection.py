import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/'experiments/attrscore-v2/prepare.py'
spec=importlib.util.spec_from_file_location('attrscore_select',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def row(n,label):return dict(query='Q'+str(n),answer='A'+str(n),reference='R'+str(n),label=label)
class AttrScoreSelectionTests(unittest.TestCase):
 def test_each_prior_field_excludes_even_if_other_fields_differ(self):
  old=row('old','Attributable');rows=[]
  for n,k in enumerate(('query','answer','reference')):
   r=row(n,'Attributable');r[k]='  '+old[k].upper()+'  ';rows.append(r)
  rows += [row('new'+str(i),label) for i,label in enumerate(m.MAPPING)]
  selected,report=m.select(rows,[old],count=1)
  self.assertEqual(len(selected),3);self.assertEqual(len(report['excluded']),3)
 def test_new_sample_has_no_shared_field_across_classes(self):
  rows=[row('a','Attributable'),row('b','Contradictory'),row('c','Contradictory'),row('d','Extrapolatory')]
  rows[1]['reference']=rows[0]['reference']
  selected,_=m.select(rows,[],count=1)
  self.assertEqual({x['row_index'] for x in selected},{0,2,3})
 def test_insufficient_cases_fails_instead_of_weakening_deduplication(self):
  with self.assertRaises(ValueError):m.select([row('a','Attributable')],[],count=1)
 def test_seeded_selection_is_reproducible(self):
  rows=[row(str(i)+label,label) for label in m.MAPPING for i in range(4)]
  a,_=m.select(rows,[],count=2);b,_=m.select(rows,[],count=2)
  self.assertEqual([x['identity'] for x in a],[x['identity'] for x in b]);self.assertEqual(len(a),6)
