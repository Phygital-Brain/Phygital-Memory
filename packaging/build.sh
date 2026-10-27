#!/bin/sh
set -e
cd "$(dirname "$0")/.."
P=phygital_memory
# A folder, not one file: one file unpacks itself on every start, which doubled the start time.
uv run pyinstaller --noconfirm --clean --onedir --noupx --name phygital-memory-server \
  --distpath packaging/dist --workpath packaging/build --specpath packaging \
  --paths . \
  --collect-submodules phygital_memory \
  --collect-all wsgidav --collect-submodules cheroot \
  --add-data "$PWD/$P/app.html:$P" \
  --add-data "$PWD/$P/closeask.html:$P" \
  --add-data "$PWD/$P/web:$P/web" \
  --add-data "$PWD/$P/engram_config.json:$P" \
  --add-data "$PWD/$P/vault/words_en.txt:$P/vault" \
  packaging/entry.py
