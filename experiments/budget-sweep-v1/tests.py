import unittest
from run import run,load,B,R
class Tests(unittest.TestCase):
 def test_reproduction_and_limits(self):
  result=run();self.assertEqual(result,load(B/'result.json'));self.assertEqual(len(result['rows']),64)
  for row in result['rows']:self.assertLessEqual(row['bytes'],row['budget'])
 def test_previous_budget_unchanged(self):
  old=load(R/'experiments/hybrid-retrieval-v1/result.json')['rows'];new=load(B/'result.json')['rows']
  for r in old:
   match=next(x for x in new if x['case_id']==r['case_id'] and x['mode']==r['mode'] and x['budget']==12000)
   for key in ('ranges','bytes','covered_paragraphs'):self.assertEqual(r[key],match[key])
 def test_aliases_identical_not_new_trials(self):
  f=load(B/'live-freeze.json');rows=load(B/'result.json')['rows']
  for alias in f['aliases']:
   original=next(c for c in f['cases'] if c['id']==alias['reuse']);row=next(r for r in rows if r['case_id']==alias['case'] and r['budget']==alias['budget'] and r['mode']=='hybrid');self.assertEqual(original['ranges'],row['ranges'])
if __name__=='__main__':unittest.main()
