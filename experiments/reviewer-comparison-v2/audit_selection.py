"""Independently reparse the original CSV preserving embedded newlines."""
import csv,json,runpy
from pathlib import Path
BASE=Path(__file__).resolve().parent

def audit():
 with (BASE.parent/'attrscore-v1/inputs/AttrEval-GenSearch.csv').open(newline='') as f:rows=list(csv.DictReader(f))
 previous=[]
 for file in (BASE.parent/'attrscore-v1/inputs/pilot-01/cases.json',BASE.parent/'attrscore-v2/inputs/pilot-02/cases.json'):
  previous.extend(rows[c['source_row_index']] for c in json.loads(file.read_text()))
 selected,_=runpy.run_path(str(BASE.parent/'attrscore-v2/prepare.py'))['select'](rows,previous,count=8,seed='agora-reviewer-comparison-v2-20260928')
 meta=[c for c in json.loads((BASE/'cases-metadata.json').read_text()) if c['id'].startswith('attr-')]
 assert [c['row_index'] for c in selected]==[c['source_row_index'] for c in meta]
 cases={c['id']:c for c in json.loads((BASE/'inputs/cases.json').read_text())}
 for c in meta:
  row=rows[c['source_row_index']];case=cases[c['id']]
  assert (case['question'],case['claim'],case['evidence'])==(row['query'],row['answer'],row['reference'])
 return dict(original_csv_selection_identical=True,selected_texts_identical=True,prior_cases=len(previous),selected=len(meta),limitation='Frozen preparer used splitlines; unselected multiline rows may differ. Correct CSV parsing reproduced this exact selection and all selected text. Use newline-preserving parsing for future corpora.')
if __name__=='__main__':print(json.dumps(audit(),indent=2))
