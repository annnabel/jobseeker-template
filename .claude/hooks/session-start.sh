#!/bin/bash
set -euo pipefail

# Install dependencies for Claude Code on the web sessions only.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Runtime deps (core + optional sweep) plus dev tools for tests and linting.
# python-docx and pypdf let bin/intake.py read the resume a user drops into
# the chat during /setup; cffi repairs the system cryptography package pypdf
# imports, which ships broken in some web containers.
pip install --break-system-packages typst pyyaml httpx pydantic python-docx pypdf cffi pytest ruff

# Fail loudly at startup rather than silently mid-sweep.
python3 -c "import typst, yaml, httpx, pydantic"
python3 -m pytest --version
ruff --version
