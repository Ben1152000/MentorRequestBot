#! /bin/sh

if screen -list | grep -q "bot"; then
    screen -S bot -X quit
    echo "Process ended."
else
    echo "No process running."
fi

