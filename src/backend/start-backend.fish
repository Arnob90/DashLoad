#!/bin/fish
set script_dir (dirname (realpath (status --current-filename)))
set current_dir (pwd)
cd $script_dir
source "$script_dir/venv/bin/activate.fish"
uvicorn --reload "server:app" --log-config "./log_config.yaml"
cd $current_dir
