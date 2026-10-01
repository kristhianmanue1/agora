"""Monotonic accumulation of frozen scheduled candidates, never semantic closure."""
from agora.subquestions import merge_ranges

def accumulate(raw,scheduled):
 previous=[];history=[];backlog=[];last_budget=0
 cost=lambda rs:sum(b-a for a,b in merge_ranges(rs))
 for index,(budget,candidates) in enumerate(scheduled):
  if type(budget) is not int or budget<=last_budget:raise ValueError('invalid_schedule')
  last_budget=budget;before=cost(previous);pending=[]
  for pair in merge_ranges(backlog+candidates):
   a,b=pair
   if type(a) is not int or type(b) is not int or not 0<=a<b<=len(raw):raise ValueError('invalid_range')
   raw[a:b].decode();proposed=merge_ranges(previous+[pair])
   if cost(proposed)<=budget:previous=proposed
   else:pending.append(pair)
  backlog=pending
  future=[p for _,rs in scheduled[index+1:] for p in rs]
  exhausted=cost(previous+backlog+future)==cost(previous)
  reason='scheduled_candidates_exhausted' if exhausted else 'budget_schedule_exhausted' if index==len(scheduled)-1 else 'continue'
  history.append(dict(budget=budget,ranges=previous,bytes=cost(previous),added_bytes=cost(previous)-before,skipped_ranges=pending,stop_reason=reason,semantic_completeness='not_established'))
  if exhausted:break
 return history
