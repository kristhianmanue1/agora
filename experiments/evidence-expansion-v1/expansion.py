"""Bind an explicit expansion to source bytes; never overwrite its parent."""
import hashlib

def expand(base,source,expected_sha256,start,end):
 if hashlib.sha256(source).hexdigest()!=expected_sha256:raise ValueError('source_revision_mismatch')
 if type(start) is not int or type(end) is not int or not 0<=start<end<=len(source):raise ValueError('invalid_locator')
 passage=source[start:end].decode('utf-8')
 return dict(evidence=base+'\n\n'+passage,parent_evidence_sha256=hashlib.sha256(base.encode()).hexdigest(),source_sha256=expected_sha256,start_byte=start,end_byte=end,passage_sha256=hashlib.sha256(passage.encode()).hexdigest(),admission='not_admitted')
