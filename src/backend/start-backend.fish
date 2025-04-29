#!/bin/fish
set script_dir (dirname (realpath (status --current-filename)))

echo "$script_dir/server.py"

source "$script_dir/venv/bin/activate.fish"

python "$script_dir/server.py"
