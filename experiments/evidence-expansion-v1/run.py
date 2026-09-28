"""Use unchanged reviewer requests; expansion does not send the old model label."""
import runpy
from pathlib import Path
BASE=Path(__file__).resolve().parent
module=runpy.run_path(str(BASE.parent/'reviewer-comparison-v2/run.py'))
if __name__=='__main__':
 module['engine'].BASE=BASE/'inputs';module['engine'].payload=module['payload'];module['engine'].main()
