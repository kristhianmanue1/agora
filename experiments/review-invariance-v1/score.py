"""Do not confuse stable wrong judgments with correct invariant support."""
AXES=('support','relevance','language','recommendation')
VALUES={'support':{'supported','contradicted','insufficient'},'relevance':{'relevant','extra','uncertain'},'language':{'match','mismatch','uncertain'},'recommendation':{'needs_revision','needs_adjudication'}}
def scores(gold,predictions):
 if set(predictions)-set(gold):raise ValueError('unknown_case')
 groups={};correct={};valid={};failed=missing=0
 for cid,g in gold.items():
  groups.setdefault(g['pair'],[]).append(cid);p=predictions.get(cid,'not_run')
  if p in ('failed','not_run'):
   failed+=p=='failed';missing+=p=='not_run';correct[cid]=False;continue
  if type(p) is not dict or set(p)!=set(AXES) or any(p[k] not in VALUES[k] for k in AXES):raise ValueError('invalid_prediction')
  valid[cid]=p;correct[cid]=p==g['expected']
 pairs=[]
 for name,ids in sorted(groups.items()):
  if len(ids)!=2:raise ValueError('invalid_pair')
  complete=all(x in valid for x in ids)
  stable=complete and len({valid[x]['support'] for x in ids})==1
  pairs.append(dict(pair=name,origin=gold[ids[0]]['origin'],both_valid=complete,support_stable=stable,correct=all(correct[x] for x in ids)))
 return dict(cases=len(gold),valid=len(valid),failed=failed,not_run=missing,correct=sum(correct.values()),pairs=pairs,
             stable_pairs=sum(x['support_stable'] for x in pairs),correct_pairs=sum(x['correct'] for x in pairs))
