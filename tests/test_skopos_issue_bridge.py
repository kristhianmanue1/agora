"""El consumidor verifica rangos y localizadores sin confiar en etiquetas."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/'experiments/skopos-issue-bridge-v1/bridge.py';s=importlib.util.spec_from_file_location('bridge_tests',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class BridgeTests(unittest.TestCase):
 def setUp(self):
  text='Entrega: mañana.';raw=(text+'\n\n').encode();loc=dict(id='one',start_ms=0,end_ms=1000,speaker='Sintético')
  self.packet=dict(schema='skopos/meeting-evidence-packet/v0',source_id='s',revision=1,source_sha256='a'*64,capture_complete_declared=False,selection_complete='not_established',text=raw.decode(),content_sha256=hashlib.sha256(raw).hexdigest(),spans=[dict(start_byte=0,end_byte=len(text.encode()),text=text,locator=loc)])
  self.record=dict(status='verified',sha256='a'*64,segment=dict(loc,text=text))
 def fetch(self,*args):return self.record
 def test_preserves_incompleteness_and_native_locator(self):
  source,receipt=m.convert(self.packet,'2026-10-08',self.fetch)
  self.assertFalse(receipt['capture_complete_declared']);self.assertEqual(receipt['selection_complete'],'not_established');self.assertIn(m.digest(self.packet),source['id'])
  self.assertEqual(m.locate(self.packet,'mañana'),[self.packet['spans'][0]['locator']])
 def test_hash_range_and_native_mismatch_rejected(self):
  variants=[]
  a=copy.deepcopy(self.packet);a['text']+='x';variants.append(a)
  a=copy.deepcopy(self.packet);a['spans'][0]['start_byte']=1;variants.append(a)
  a=copy.deepcopy(self.packet);a['spans'][0]['locator']['speaker']='Otro';variants.append(a)
  for value in variants:
   with self.assertRaises(ValueError):m.convert(value,'2026-10-08',self.fetch)
 def test_unavailable_origin_and_unmapped_quote_rejected(self):
  with self.assertRaises(ValueError):m.convert(self.packet,'2026-10-08',lambda *a:dict(status='source_unavailable'))
  with self.assertRaises(ValueError):m.locate(self.packet,'inexistente')
if __name__=='__main__':unittest.main()
