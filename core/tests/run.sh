#!/bin/sh
# Run one test from anywhere: sh core/tests/run.sh test_sharing.py (it runs from core, which holds the app's code).
# Most need a fresh test memory first: sh core/tests/run.sh make_test_vault.py --fresh
set -e
cd "$(dirname "$0")/.."
T="$1"; shift
PYTHONPATH=. exec uv run python "tests/$T" "$@"
