"""Integridad, completitud visible y recuperación sin archivos laterales."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/'experiments/skopos-issue-bridge-v2/envelope.py';s=importlib.util.spec_from_file_location('envelope_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class EnvelopeTests(unittest.TestCase):
 def setUp(self):
  text='Dice "mañana".\nSegunda línea.';loc=dict(id='s',start_ms=0,end_ms=10,speaker='Sintético');content=text+'\n\n'
  self.packet=dict(schema='skopos/meeting-evidence-packet/v0',source_id='x',revision=1,source_sha256='a'*64,capture_complete_declared=False,selection_complete='not_established',text=content,content_sha256=hashlib.sha256(content.encode()).hexdigest(),spans=[dict(start_byte=0,end_byte=len(text.encode()),text=text,locator=loc)])
  self.fetch=lambda *args:dict(status='verified',sha256='a'*64,segment=dict(loc,text=text))
 def test_roundtrip_unicode_quotes_newlines_and_metadata(self):
  source,_=m.create(self.packet,'2026-10-08',self.fetch)
  self.assertEqual(m.recover(source),self.packet);self.assertIn(self.packet['spans'][0]['text'],source['text'])
 def test_modified_envelope_or_identity_rejected(self):
  source,_=m.create(self.packet,'2026-10-08',self.fetch)
  for changed in [dict(source,text=source['text']+'x'),dict(source,id='skopos-packet:wrong')]:
   with self.assertRaises(ValueError):m.recover(changed)
 def test_metadata_rewrite_even_with_outer_hash_fails_identity(self):
  source,_=m.create(self.packet,'2026-10-08',self.fetch)
  source['text']=source['text'].replace('"capture_complete_declared":false','"capture_complete_declared":true');source['sha256']=hashlib.sha256(source['text'].encode()).hexdigest()
  with self.assertRaisesRegex(ValueError,'packet_binding'):m.recover(source)
 def test_provider_receives_policy_without_promoting_source_to_instruction(self):
  seen=[];wrapped=m.with_completeness_policy(lambda system,user:seen.append((system,user)))
  wrapped('BASE','DATA');self.assertIn(m.POLICY,seen[0][0]);self.assertEqual(seen[0][1],'DATA')
if __name__=='__main__':unittest.main()
