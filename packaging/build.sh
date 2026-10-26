#!/bin/sh
set -e
cd "$(dirname "$0")/.."
P=phygital_memory
uv run pyinstaller --noconfirm --clean --onefile --name phygital-memory-server \
  --distpath packaging/dist --workpath packaging/build --specpath packaging \
  --paths . \
  --collect-submodules phygital_memory \
  --collect-all wsgidav --collect-submodules cheroot \
  --add-data "$PWD/$P/app.html:$P" \
  --add-data "$PWD/$P/web:$P/web" \
  --add-data "$PWD/$P/engram_config.json:$P" \
  --add-data "$PWD/$P/vault/words_en.txt:$P/vault" \
  packaging/entry.py
