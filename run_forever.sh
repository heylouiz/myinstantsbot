#!/bin/sh

# This script keeps the bot running "forever", if it dies
# the script will relaunch it
while true; do
  python3 myinstantsbot.py
  sleep 4s
done
