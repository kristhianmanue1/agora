"""Reproduce the pinned local extraction; source contents remain gitignored."""
import hashlib,json,sys
from pathlib import Path
from pypdf import PdfReader
BASE=Path(__file__).resolve().parent
pdf=Path(sys.argv[1]);raw=pdf.read_bytes()
expected=json.loads((BASE/'extraction.json').read_text())
assert hashlib.sha256(raw).hexdigest()==expected['pdf_sha256'], 'different PDF'
parts=[f"\n\n[PDF page {i}]\n\n"+(p.extract_text() or '') for i,p in enumerate(PdfReader(pdf).pages,1)]
text=''.join(parts).encode()
assert hashlib.sha256(text).hexdigest()==expected['source_sha256'], 'extraction differs; inspect dependency version'
(BASE/'inputs').mkdir(exist_ok=False)
(BASE/'inputs/source.txt').write_bytes(text)
print(json.dumps({'pages':len(parts),'bytes':len(text),'source_sha256':expected['source_sha256']}))
