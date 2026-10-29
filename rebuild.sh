#!/bin/sh
# Rebuild the server binary and the .dmg, then (with --install) replace the app in /Applications and reopen it.
set -e
cd "$(dirname "$0")"
[ -d core/frontend/node_modules ] || (cd core/frontend && npm ci >/tmp/pm-front.log 2>&1)   # the page's build tools, once
(cd core/frontend && npm run -s build >/tmp/pm-front.log 2>&1)
# The engine, then the engine + Syncthing + rclone + every licence into app/src-tauri/server. The same two scripts
# build Windows and Linux on GitHub (with --fetch there), so all three come from one source.
(cd core && uv run python packaging/build.py) >/tmp/pm-build.log 2>&1
python3 core/packaging/bundle_server.py >/tmp/pm-bundle.log 2>&1
# The Touch ID helper. The Keychain trusts it by its signature: it's signed with this Mac's own fixed certificate
# (.signing, see its README), so a rebuilt helper keeps that trust and macOS never asks again after an update.
# The build stops if the helper isn't signed that way: an unsigned one would make macOS ask for every kept item.
T=core/packaging/touchid
SIGN="${PHYGITAL_MEMORY_SIGNING:-.signing}"   # the keys folder: .signing here, or set PHYGITAL_MEMORY_SIGNING to keep it elsewhere
KC="$(cd "$SIGN" 2>/dev/null && pwd)/phygital-memory-signing.keychain-db"
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
# The update files are signed with the app's own update key ($SIGN/updater.key): the app only installs updates
# signed with it. Never printed; only this build reads it.
export TAURI_SIGNING_PRIVATE_KEY="$(cat "$SIGN/updater.key")"
export TAURI_SIGNING_PRIVATE_KEY_PASSWORD="$(cat "$SIGN/updater-password")"
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
