import hashlib,runpy,unittest
from pathlib import Path
expand=runpy.run_path(str(Path(__file__).resolve().parents[1]/'experiments/evidence-expansion-v1/expansion.py'))['expand']
class EvidenceExpansionTests(unittest.TestCase):
 def test_literal_bytes_and_parent_are_preserved(self):
  source='Inicio. Evidencia útil. Final.'.encode();start=len('Inicio. '.encode());end=len('Inicio. Evidencia útil.'.encode())
  result=expand('Resumen',source,hashlib.sha256(source).hexdigest(),start,end)
  self.assertEqual(result['evidence'],'Resumen\n\nEvidencia útil.')
  self.assertEqual(result['parent_evidence_sha256'],hashlib.sha256(b'Resumen').hexdigest())
  self.assertEqual(result['admission'],'not_admitted')
 def test_stale_revision_and_bad_ranges_rejected(self):
  source=b'original';digest=hashlib.sha256(source).hexdigest()
  with self.assertRaises(ValueError):expand('base',source,'wrong',0,2)
  for start,end in ((-1,2),(0,99),(3,2),(True,2)):
   with self.assertRaises(ValueError):expand('base',source,digest,start,end)
 def test_split_utf8_rejected(self):
  source='á'.encode()
  with self.assertRaises(UnicodeDecodeError):expand('base',source,hashlib.sha256(source).hexdigest(),0,1)
