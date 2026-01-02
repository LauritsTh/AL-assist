#!/usr/bin/env bash
xev -root | while read line; do
  echo "$line" | grep -q "keycode 65" && sleep 3 && python3 ~/.local/share/al/al.py
done
