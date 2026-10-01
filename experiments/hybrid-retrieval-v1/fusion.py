"""Frozen quota fusion of source ranges; no answers or rubric inputs."""
from itertools import zip_longest
from agora.subquestions import merge_ranges

def fuse(raw,lexical,structural,budget=12000):
 if type(budget) is not int or budget<1:raise ValueError('invalid_budget')
 title=raw.find(b'\n\n')
 if not 0<title<=budget:raise ValueError('invalid_initial')
 chosen=[[0,title]];cost=lambda rows:sum(b-a for a,b in merge_ranges(rows))
 streams=[lexical,structural];remaining=[[],[]];allocations=[];quota=(budget-title)//2
 for index,stream in enumerate(streams):
  spent=0
  for pair in stream:
   a,b=pair
   if not 0<=a<b<=len(raw):raise ValueError('invalid_range')
   raw[a:b].decode();proposed=merge_ranges(chosen+[pair]);delta=cost(proposed)-cost(chosen)
   if spent+delta<=quota:chosen=proposed;spent+=delta
   else:remaining[index].append(pair)
  allocations.append(spent)
 # Redistribute unused total budget by alternation, lexical first, without truncation.
 skipped=[]
 for pairset in zip_longest(*remaining):
  for pair in pairset:
   if pair is None:continue
   proposed=merge_ranges(chosen+[pair])
   if cost(proposed)<=budget:chosen=proposed
   else:skipped.append(pair)
 return dict(ranges=chosen,bytes=cost(chosen),quota_per_channel=quota,first_pass_added_bytes=allocations,skipped_ranges=merge_ranges(skipped),semantic_completeness='not_established')
