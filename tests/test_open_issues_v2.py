"""Controles de reapertura parcial y propagación por campo declarado."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'experiments/open-issues-v2'
spec=importlib.util.spec_from_file_location('issue_v2',P/'protocol.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class IssueV2Tests(unittest.TestCase):
 def setUp(self):
  self.case=json.loads((P/'cases.json').read_text())[2]
  self.data=p.payload(self.case,0,self.case['prior'])
  self.out=dict(fields=dict(date=dict(observed_value=None,support_status='withdrawn',missing_requirements=['date_confirmed'],relations=['refutation'],evidence=[dict(source_id='p2',quote='no existe fecha aprobada para Nube')]),owner=dict(observed_value='Lina',support_status='supported',missing_requirements=[],relations=['initial'],evidence=[dict(source_id='p2',quote='Lina sigue siendo responsable')])),reason='Se retira sólo la fecha.')
 def test_partial_reopening_does_not_invalidate_owner(self):
  result=p.validate(json.dumps(self.out),self.data)
  self.assertEqual(result['status'],'partial');self.assertEqual(result['reopened_fields'],['date']);self.assertEqual(result['affected'],['schedule'])
 def test_rejects_fabricated_quote_and_unknown_requirement(self):
  for field,value in [('evidence',[dict(source_id='p2',quote='fecha aprobada: mañana')]),('missing_requirements',['invented'])]:
   bad=copy.deepcopy(self.out);bad['fields']['date'][field]=value
   with self.assertRaises(ValueError):p.validate(json.dumps(bad),self.data)
 def test_model_cannot_override_derived_state(self):
  for key in ('status','affected','reopened_fields'):
   bad=dict(self.out,**{key:'resolved'})
   with self.assertRaises(ValueError):p.validate(json.dumps(bad),self.data)
 def test_false_history_is_separate_from_sources(self):
  case=json.loads((P/'cases.json').read_text())[0]
  a=p.payload(case,0);b=p.payload(case,0,case['prior'])
  self.assertEqual(a['sources'],b['sources']);self.assertIsNone(a['previous_assessment'])
  self.assertEqual(b['previous_assessment']['fields']['date']['observed_value'],'2026-11-30')
 def test_withdrawal_cannot_keep_approved_value(self):
  for changes in [dict(observed_value='2026-10-21'),dict(relations=['update']),dict(missing_requirements=[])]:
   bad=copy.deepcopy(self.out);bad['fields']['date'].update(changes)
   with self.assertRaises(ValueError):p.validate(json.dumps(bad),self.data)
if __name__=='__main__':unittest.main()
