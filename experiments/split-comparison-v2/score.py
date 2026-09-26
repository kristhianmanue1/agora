"""Recompute judgments from preserved outputs; report missing coverage explicitly."""
import json
from pathlib import Path
import sys
from audit import audit


def score(directory):
    root = Path(directory)
    if not (root/"summary.json").is_file():
        raise ValueError("run_in_progress_or_unclosed")
    audit(directory)
    load = lambda name: json.loads((root/name).read_text())
    gold, calls, rows = load('gold.json'), load('calls.json'), load('scores.json')
    summary = {}
    for mode in ('combined', 'split'):
        results = []
        for identity, expected in gold.items():
            selected = [r for r in rows if r['mode'] == mode and r['case'] == identity]
            if len(selected) > 1:
                raise ValueError('duplicate_case')
            if not selected:
                results.append({'case':identity, 'status':'not_attempted'})
                continue
            row = selected[0]
            result = load(identity+'-'+mode+'.json')
            entry = {'case':identity, 'status':result['execution_status'], 'seconds':row['seconds']}
            if result['execution_status'] == 'complete':
                claim = result['assessment']['claims'][0] if mode == 'combined' else result['assessment'][0]
                entry.update(support=claim['support'], relevance=claim['relevance'],
                             support_correct=claim['support']==expected['support'],
                             relevance_correct=claim['relevance']==expected['relevance'])
                entry['joint_correct'] = entry['support_correct'] and entry['relevance_correct']
            for key in ('support_correct','relevance_correct','joint_correct'):
                if row[key] != entry.get(key, False):
                    raise ValueError('recorded_score_mismatch')
            results.append(entry)
        complete = [r for r in results if r['status']=='complete']
        pair_ids = {identity.split('-')[0] for identity in gold}
        pairs = sum(all(next(r for r in results if r['case']==p+'-'+suffix).get('joint_correct',False)
                        for suffix in ('on','off')) for p in pair_ids)
        arm_calls = [c for c in calls if c['mode']==mode]
        summary[mode] = {'planned':len(gold), 'complete':len(complete),
            'support_correct':sum(r['support_correct'] for r in complete),
            'relevance_correct':sum(r['relevance_correct'] for r in complete),
            'joint_correct':sum(r['joint_correct'] for r in complete),
            'correct_pairs':pairs, 'planned_pairs':len(pair_ids),
            'attempted_calls':len(arm_calls),
            'known_tokens':sum(c.get('tokens',0) for c in arm_calls),
            'unknown_usage_calls':sum('tokens' not in c for c in arm_calls),
            'complete_case_seconds':sum(r['seconds'] for r in complete), 'cases':results}
    return summary

if __name__ == '__main__':
    print(json.dumps(score(sys.argv[1]), indent=2))
