#!/bin/bash
# ヨヨイ 창구 지킴이 — 7980 이 안 열려 있으면 켠다(크론 1분 · @reboot).
# 끄기 = 크론의 창구 줄 두 개를 빼고 pkill -f ch/문.py
/usr/bin/ss -ltn | grep -q '127.0.0.1:7980 ' && exit 0
mkdir -p "$HOME/창구-자료" || exit 1
cd "$HOME/douzo/ch" || exit 1
nohup /usr/bin/python3 -I "$HOME/douzo/ch/문.py" >> "$HOME/창구-자료/문.err" 2>&1 &
