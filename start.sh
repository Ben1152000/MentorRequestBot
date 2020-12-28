#! /bin/sh

if screen -list | grep -q "bot"; then
    echo "Process already running."
else
    screen -S bot -dm python3 bot.py
    echo "Process started."
fi


