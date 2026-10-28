#!/bin/bash
# usage: render.sh page.html out.png width height   (Brave headless; fonts load from Google Fonts)
D="$(cd "$(dirname "$0")" && pwd)"
"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files --default-background-color=00000000 --virtual-time-budget=8000 --screenshot="$2" --window-size=$3,$4 "file://$D/$1" >/dev/null 2>&1
