#! /bin/sh

./frida-portal -D

socat TCP-LISTEN:1337,reuseaddr,fork,max-children=1 EXEC:'uv run main.py',stderr
