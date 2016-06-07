#!/bin/sh

# This script keeps the bot running "forever", if it dies
# the script will relaunch it
RC=1
while [ $RC -ne 0 ]; do
   python3 myinstantsbot.py
      RC=$?
      done
