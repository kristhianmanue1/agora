"""Bounded heuristic expansion; no semantic completeness claim or model calls."""
import re
CUES=re.compile(r'\b(?:except\w*|exclud\w*|unless|only|however|whereas|excluded|excepto|exclu\w*|salvo|únicamente|solamente|sin embargo)\b',re.I)
STOP=set('what which where when how why who whose does do did they their them these those this that with from into about use used using set sets the and are for was were have has been our any all can could would should'.split())
def terms(text):
 return {w[:-1] if w.endswith('s') and len(w)>4 else w for w in re.findall(r'\w+',text.casefold()) if len(w)>2 and w not in STOP}
def merge(ranges):
 result=[]
 for start,end in sorted(ranges):
  if result and start<=result[-1][1]:result[-1][1]=max(result[-1][1],end)
  else:result.append([start,end])
 return result
def expand(source,question,initial_ranges,total_budget=10000,max_added=2):
 if type(total_budget) is not int or total_budget<1 or type(max_added) is not int or not 1<=max_added<=8:raise ValueError('invalid_budget')
 text=source.decode('utf-8');ranges=[]
 for pair in initial_ranges:
  if len(pair)!=2 or any(type(x) is not int for x in pair) or not 0<=pair[0]<pair[1]<=len(source):raise ValueError('invalid_range')
  source[pair[0]:pair[1]].decode('utf-8');ranges.append(list(pair))
 chosen=merge(ranges);cost=lambda rs:sum(b-a for a,b in merge(rs))
 if cost(chosen)>total_budget:raise ValueError('initial_budget_exceeded')
 anchors=terms(question);initial_text=' '.join(source[a:b].decode() for a,b in chosen);context_terms=terms(initial_text);candidates=[]
 for m in re.finditer(r'[^\r\n]+(?:\r?\n(?!\r?\n)[^\r\n]+)*',text):
  value=m.group();start=len(text[:m.start()].encode());end=start+len(value.encode());hits=CUES.findall(value);overlap=anchors & terms(value)
  if not hits or not overlap or any(a<=start and end<=b for a,b in chosen):continue
  candidates.append(dict(start_byte=start,end_byte=end,question_overlap=sorted(overlap),context_overlap_count=len(context_terms & terms(value)),cues=hits))
 candidates.sort(key=lambda x:(-len(x['question_overlap']),-x['context_overlap_count'],x['start_byte']));added=[];skipped=[]
 for c in candidates:
  if len(added)>=max_added:break
  proposed=merge(chosen+[[c['start_byte'],c['end_byte']]])
  if cost(proposed)>total_budget:skipped.append(dict(c,reason='budget'));continue
  chosen=proposed;added.append(c)
 return dict(schema='agora/condition-expansion/v1-experimental',ranges=chosen,initial_bytes=cost(initial_ranges),delivered_bytes=cost(chosen),added=added,skipped=skipped,matching_candidates=len(candidates),question_anchors=sorted(anchors),local_scan_bytes=len(source),semantic_completeness='not_established',method='question-overlap-and-explicit-exception-cues',max_added=max_added,total_budget=total_budget)
