#!/bin/sh
# Kept for old habits: the build is packaging/build.py now (it runs on Mac, Windows and Linux).
set -e
cd "$(dirname "$0")/.."
exec uv run python packaging/build.py
