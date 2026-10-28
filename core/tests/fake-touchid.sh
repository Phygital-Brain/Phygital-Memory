#!/bin/sh
# A stand-in for the Touch ID helper, for tests: the "finger" is the word in $D/answer (yes or no).
D="${FAKE_TOUCHID_DIR:?}"
yes() { echo "$1" >> "$D/asked"; [ "$(cat "$D/answer" 2>/dev/null)" = "yes" ]; }
case "$1" in
  can) [ ! -f "$D/none" ] ;;
  ask) yes "$2" ;;
  save) cat > "$D/kept-$3" ;;
  get) yes unlock || exit 3; [ -f "$D/kept-$3" ] && cat "$D/kept-$3" ;;
  has) [ -f "$D/kept-$3" ] ;;
  forget) rm -f "$D/kept-$3" ;;
  *) exit 2 ;;
esac
