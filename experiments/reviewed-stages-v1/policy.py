"""Experimental routing of separate coverage and fidelity reviews."""
def decide(generation,coverage,fidelity,has_next):
 if generation!='complete':return 'stop_invalid_generation'
 if coverage.get('status')!='complete':return 'stop_inconclusive_coverage'
 if fidelity.get('status')!='completed':return 'stop_inconclusive_fidelity'
 if fidelity.get('label')!='supported':return 'requires_fidelity_inspection'
 labels=[r['status'] for r in coverage['requirements']]
 if not labels or any(v in ('uncertain','contradicted') for v in labels):return 'requires_coverage_inspection'
 if all(v=='covered' for v in labels):return 'candidate_ready_for_explicit_review'
 return 'expand' if has_next else 'insufficient_evidence'
