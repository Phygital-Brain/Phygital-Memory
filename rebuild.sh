#!/bin/sh
# Rebuild the server binary and the .dmg, then (with --install) replace the app in /Applications and reopen it.
set -e
cd "$(dirname "$0")"
[ -d core/frontend/node_modules ] || (cd core/frontend && npm ci >/tmp/pm-front.log 2>&1)   # the page's build tools, once
(cd core/frontend && npm run -s build >/tmp/pm-front.log 2>&1)
sh core/packaging/build.sh >/tmp/pm-build.log 2>&1
rm -rf app/src-tauri/server
cp -R core/packaging/dist/phygital-memory-server app/src-tauri/server   # the server, a folder (Resources/server)
install -m 755 "$(readlink -f "$(command -v rclone)")" app/src-tauri/server/rclone   # the cloud helper (MIT)
install -m 755 "$(readlink -f "$(command -v syncthing)")" app/src-tauri/server/syncthing   # Mac-to-Mac sharing (MPL-2.0)
# Their licences go with them (Resources/server/licenses, shown in Settings › About): the texts as each project ships them.
L=app/src-tauri/server/licenses
mkdir -p "$L"
ST_HOME="$(dirname "$(readlink -f "$(command -v syncthing)")")/.."
RC_HOME="$(dirname "$(readlink -f "$(command -v rclone)")")/.."
{ echo "Syncthing $(syncthing --version | awk '{print $2}')"
  echo "Copyright the Syncthing contributors. Mozilla Public License 2.0. Included unchanged."
  echo "Source code: https://github.com/syncthing/syncthing"; echo; cat "$ST_HOME/LICENSE"; } > "$L/1-syncthing.txt"
{ echo "rclone $(rclone version | awk 'NR==1 {print $2}')"
  echo "MIT License. Included unchanged."
  echo "Source code: https://github.com/rclone/rclone"; echo; cat "$RC_HOME/COPYING"; } > "$L/2-rclone.txt"
cp core/phygital_memory/web/THIRD-PARTY-LICENSES.txt "$L/3-libraries-and-fonts.txt"   # the editor's libraries and the brand fonts
(cd core && uv run python packaging/python_licences.py "../$L/4-engine-python.txt" >/dev/null)   # Python and its libraries
python3 core/packaging/rust_licences.py app/src-tauri "$L/5-mac-window.txt" >/dev/null   # Tauri and its Rust crates
python3 core/packaging/compact_licences.py "$L" 3-libraries-and-fonts.txt 4-engine-python.txt 5-mac-window.txt 3-open-source-parts.txt >/dev/null   # each licence text once
cat > "$L/0-overview.txt" <<'TXT'
PHYGITAL MEMORY: OPEN-SOURCE PARTS

These open-source parts are inside Phygital Memory. Each part keeps its own licence.

Inside the app
  Sharing between Macs: Syncthing (MPL-2.0)
  Cloud storage: rclone (MIT)
  Note editor: CodeMirror and Lezer (MIT)
  Diagrams in notes: Mermaid and the libraries it uses (MIT, ISC, BSD-3-Clause, Unlicense)
  Graph view: Sigma, Graphology and d3 (MIT, ISC)
  Safe pasting: DOMPurify (MPL-2.0 or Apache-2.0)
  Fonts: Anybody, Hanken Grotesk and JetBrains Mono (SIL Open Font License 1.1)
  Engine: Python and its libraries (PSF-2.0, MIT, BSD, Apache-2.0)
  Mac window: Tauri and the Rust crates it uses (MIT, Apache-2.0, MPL-2.0 and others)

Thanks
  Baalda (github.com/naveedharri/baalda, Apache-2.0), for design and feature ideas. No Baalda code is included.
TXT
# The Touch ID helper. The Keychain trusts it by its signature: it's signed with this Mac's own fixed certificate
# (.signing, see its README), so a rebuilt helper keeps that trust and macOS never asks again after an update.
# The build stops if the helper isn't signed that way: an unsigned one would make macOS ask for every kept item.
T=core/packaging/touchid
SIGN=.signing
KC="$PWD/$SIGN/phygital-memory-signing.keychain-db"
[ -f "$KC" ] && [ -f "$SIGN/keychain-password" ] || { echo "missing $SIGN (the helper's signing certificate)"; exit 1; }
security unlock-keychain -p "$(cat "$SIGN/keychain-password")" "$KC"
ID=$(security find-identity "$KC" | awk '/Phygital Memory Local Signing/ {print $2; exit}')
# Frozen: macOS also remembers the helper's exact fingerprint for each kept item, so ANY change to it makes macOS ask
# for every item again. Its source must match the recorded hash; new Mac-only features go in a separate helper.
if [ "$(shasum -a 256 "$T/main.swift" | cut -d' ' -f1)" != "$(cat "$SIGN/helper-source.sha256")" ] && [ "$CHANGE_KEYCHAIN_HELPER" != "yes" ]; then
  echo "The Keychain helper's source changed. That would make macOS ask again for every kept item."
  echo "Put new features in a separate helper. To change it anyway: CHANGE_KEYCHAIN_HELPER=yes sh rebuild.sh, then update $SIGN/helper-source.sha256"
  exit 1
fi
if [ ! -f "$T/bin/Phygital Memory" ] || [ "$T/main.swift" -nt "$T/bin/Phygital Memory" ]; then
  mkdir -p "$T/bin" && swiftc -O -o "$T/bin/Phygital Memory" "$T/main.swift" 2>/dev/null
fi
codesign -f -s "$ID" --keychain "$KC" -i "Phygital Memory" "$T/bin/Phygital Memory" 2>/dev/null
check_helper() {
  codesign -dr- "$1" 2>&1 | grep -qi "certificate leaf = H\"$ID\"" || { echo "helper not signed with the fixed certificate: $1"; exit 1; }
}
check_helper "$T/bin/Phygital Memory"
mkdir -p app/src-tauri/server/touchid && cp -p "$T/bin/Phygital Memory" app/src-tauri/server/touchid/
# The .dmg step sometimes can't eject its disk image ("Resource busy"): then build just the app, which is what gets installed.
rm -f "app/src-tauri/target/release/bundle/dmg/Phygital Memory_0.1.0_aarch64.dmg"   # so an old .dmg never passes for a new one
(cd app && cargo tauri build --bundles app,dmg >/tmp/pm-tauri.log 2>&1) || (cd app && cargo tauri build --bundles app >>/tmp/pm-tauri.log 2>&1)
check_helper "app/src-tauri/target/release/bundle/macos/Phygital Memory.app/Contents/Resources/server/touchid/Phygital Memory"
DMG="app/src-tauri/target/release/bundle/dmg/Phygital Memory_0.1.0_aarch64.dmg"
if [ -f "$DMG" ]; then   # the finished .dmg goes in release/, wearing the app icon in Finder
  cp "$DMG" "release/Phygital Memory.dmg"
  osascript -l JavaScript -e 'ObjC.import("AppKit"); $.NSWorkspace.sharedWorkspace.setIconForFileOptions($.NSImage.alloc.initWithContentsOfFile("'"$PWD/brand/png/app-icon-1024.png"'"), "'"$PWD/release/Phygital Memory.dmg"'", 0)' >/dev/null
  echo "built: release/Phygital Memory.dmg"
else
  echo "no .dmg this time: make one from the installed app (see README)"
fi
if [ "$1" = "--install" ]; then
  osascript -e 'quit app "Phygital Memory"' 2>/dev/null || true
  sleep 2
  pkill -f "Phygital Memory.app/Contents/MacOS" 2>/dev/null || true
  pkill -f "Phygital Memory.app/Contents/Resources/server/" 2>/dev/null || true   # its server and helpers too, so no
                                                                                    # Keychain question is left open
  rm -rf "/Applications/Phygital Memory.app"
  cp -R "app/src-tauri/target/release/bundle/macos/Phygital Memory.app" /Applications/
  open "/Applications/Phygital Memory.app"
  echo "installed and opened"
fi
