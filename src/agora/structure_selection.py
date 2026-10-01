"""Experimental source-structure selector; no rubric or expected-answer input."""
import re
from agora.subquestions import merge_ranges
STOP=set('which what are is the used use was were of for how and in to does do a an'.split())
def terms(text):
 return {w[:-1] if w.endswith('s') and len(w)>4 else w for w in re.findall(r'\w+',text.casefold()) if len(w)>2 and w not in STOP}
def nodes(paper):
 offset=len((paper['title']+'\n\n'+paper['abstract']+'\n\n').encode());out=[]
 for sec in paper['full_text']:
  title=sec['section_name'] or '';head=[offset,offset+len(title.encode())];offset=head[1]+2;paras=[]
  for text in sec['paragraphs']:
   end=offset+len(text.encode());paras.append(dict(text=text,range=[offset,end]));offset=end+2
  out.append(dict(title=title,heading=head,paragraphs=paras))
 return out,offset

def is_list(text):
 return len(text)<=180 and (text.rstrip().endswith(';') or bool(re.match(r'^\s*(?:[-*•]|\d+[.)])\s',text)))
def select(raw,question,sections,mode,budget=12000):
 if mode not in ('headings','headings-lists'):raise ValueError('mode')
 end=raw.find(b'\n\n');chosen=[[0,end]]
 if not 0<end<=budget:raise ValueError('initial_budget')
 q=terms(question);ranked=[]
 for i,s in enumerate(sections):
  head=len(terms(s['title'])&q);leaf=len(terms(s['title'].split(':::')[-1])&q)
  body=max([len(terms(p['text'])&q) for p in s['paragraphs']] or [0])
  lists=[j for j,p in enumerate(s['paragraphs']) if is_list(p['text'])]
  score=4*leaf+head
  if mode=='headings-lists':score+=body+(3 if lists and body else 0)
  if score:ranked.append((score,i,lists))
 ranked=sorted(ranked,key=lambda r:(-r[0],r[1]))[:3];quota=(budget-end)//max(1,len(ranked));reports=[]
 for score,i,lists in ranked:
  sec=sections[i];used=0;selected=[]
  order=list(range(len(sec['paragraphs'])))
  if mode=='headings-lists':
   priority=[j for k in lists for j in (k-1,k) if j>=0]
   order=list(dict.fromkeys(priority+sorted(order,key=lambda j:(-len(terms(sec['paragraphs'][j]['text'])&q),j))))
  candidates=([sec['heading']] if sec['heading'][1]>sec['heading'][0] else [])+[sec['paragraphs'][j]['range'] for j in order]
  for a,b in candidates:
   if used+b-a<=quota:used+=b-a;selected.append([a,b])
  chosen=merge_ranges(chosen+selected);reports.append(dict(section_index=i,title=sec['title'],score=score,list_paragraphs=lists,quota=quota,selected_bytes=used))
 return dict(ranges=chosen,bytes=sum(b-a for a,b in chosen),sections=reports,semantic_completeness='not_established')
