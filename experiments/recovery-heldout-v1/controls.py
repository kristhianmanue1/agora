"""Run the existing no-omission and insufficient-budget regression controls."""
import json,sys,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[1];sys.path[:0]=[str(R/'src'),str(R/'tests')]
from test_coverage_recovery import RecoveryTests
names=['test_covered_is_not_global_completeness','test_budget_and_initial_context','test_uncertain_or_contradicted_stops_before_search']
result=unittest.TextTestRunner().run(unittest.TestSuite(RecoveryTests(n) for n in names))
assert result.wasSuccessful()
with (B/'controls.json').open('x') as out:json.dump(dict(origin='Existing producer-defined synthetic controls, not semantic adjudication',tests=names,tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors)),out,indent=2)
