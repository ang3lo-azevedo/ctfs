#!/bin/sh

tmux new -d
tmux send "tail -n 0 -F /var/log/ops/error.log" Enter
tmux source ~/.tmux.conf
exec tmux attach
