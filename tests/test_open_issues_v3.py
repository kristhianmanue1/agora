"""Controles de snapshots y candidatos de revisión: no juicio semántico."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
BASE=Path(__file__).resolve().parents[1]/'experiments/open-issues-v3'
spec=importlib.util.spec_from_file_location('issues_v3',BASE/'protocol.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class IssueV3Tests(unittest.TestCase):
 def setUp(self):
  c=json.loads((BASE/'cases.json').read_text())[0];self.data=m.payload(c,0)
  self.output=dict(fields=dict(date=dict(observed_value=None,support_status='withdrawn',missing_requirements=['date_confirmed'],relations=['refutation'],change_source_ids=['p2'],evidence=[dict(source_id='p2',quote='no existe fecha aprobada para Nube')]),owner=dict(observed_value='Lina',support_status='supported',missing_requirements=[],relations=['initial'],change_source_ids=[],evidence=[dict(source_id='p2',quote='Lina sigue siendo responsable')])),reason='Se retira fecha sin cambiar responsable.')
 def test_only_unreviewed_date_dependent_selected(self):
  r=m.validate(json.dumps(self.output),self.data)
  self.assertEqual(r['affected'],['schedule']);self.assertEqual(r['status'],'partial');self.assertEqual(r['reopened_fields'],['date'])
 def test_changed_bytes_and_dependency_revision_fail(self):
  for target in ('source','dependent'):
   data=copy.deepcopy(self.data)
   if target=='source':data['sources'][0]['text']+=' altered'
   else:data['dependents'][0]['basis'][0]['sha256']='0'*64
   with self.assertRaises(ValueError):m.validate(json.dumps(self.output),data)
 def test_old_object_relation_rejected_not_repaired(self):
  out=copy.deepcopy(self.output);out['fields']['date']['relations']=[dict(source_id='p2',relation='refutation')]
  with self.assertRaises(ValueError):m.validate(json.dumps(out),self.data)
 def test_unknown_or_uncited_change_rejected(self):
  for ids in [['missing'],['p1'],[]]:
   out=copy.deepcopy(self.output);out['fields']['date']['change_source_ids']=ids
   with self.assertRaises(ValueError):m.validate(json.dumps(out),self.data)
 def test_repeated_review_does_not_repeat_candidate(self):
  data=copy.deepcopy(self.data)
  data['dependents'][0]['reviewed_sources']=data['dependents'][2]['reviewed_sources']
  self.assertEqual(m.validate(json.dumps(self.output),data)['affected'],[])
 def test_missing_snapshot_is_not_assumed_current(self):
  data=copy.deepcopy(self.data);data['dependents'][0]['reviewed_sources']=[]
  with self.assertRaises(ValueError):m.validate(json.dumps(self.output),data)
if __name__=='__main__':unittest.main()
