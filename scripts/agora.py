#!/usr/bin/env python3
"""Single checkout entry point for agent discovery and explicit dispatch."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from agora.agent_cli import main
if __name__ == '__main__':
    raise SystemExit(main())
