"""Experimental selectors. No annotations or expected answers are accepted."""
import re
from agora.subquestions import merge_ranges
from agora.passages import lexical_ranges
STOP=set('which what are is the used use was were of for how and in to does do a an'.split())
VARIANTS=('exact-paragraphs','filtered-paragraphs','exact-sections','filtered-sections')
def cost(ranges):return sum(b-a for a,b in merge_ranges(ranges))
def select(envelope,question,sections,variant,budget=12000):
 if variant not in VARIANTS:raise ValueError('unknown_variant')
 raw=envelope['spans'][0]['text'].encode();end=raw.find(b'\n\n')
 if end<=0 or end>budget:raise ValueError('invalid_initial_context')
 initial=[[0,end]];query=question
 if variant.startswith('filtered'):
  query=' '.join(w for w in re.findall(r'\w+',question) if w.casefold() not in STOP)
 seeds,stats=lexical_ranges(envelope,query,budget,3)
 chosen=initial;skipped=[]
 def add(pair):
  nonlocal chosen
  if cost(chosen+[pair])<=budget:chosen=merge_ranges(chosen+[pair]);return True
  skipped.append(pair);return False
 if variant.endswith('paragraphs'):
  text=raw.decode();paragraphs=[]
  for m in re.finditer(r'[^\r\n]+(?:\r?\n(?!\r?\n)[^\r\n]+)*',text):
   a=len(text[:m.start()].encode());paragraphs.append([a,a+len(m.group().encode())])
  for x,y in seeds:
   indices=[i for i,(a,b) in enumerate(paragraphs) if a<y and b>x]
   if indices:
    for pair in paragraphs[indices[0]:indices[-1]+4]:add(pair)
 else:
  touched=[(a,b) for a,b in sections if any(a<y and b>x for x,y in seeds)]
  for pair in touched:add(list(pair))
  # Keep seed passages that did not fit as a full section. No oracle fallback.
  for pair in seeds:add(list(pair))
 return dict(query=query,ranges=chosen,bytes=cost(chosen),initial_ranges=initial,skipped_ranges=merge_ranges(skipped),retrieval=stats)
