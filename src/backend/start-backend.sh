#!/bin/sh

set -e # Exit on error

# Get script dir portably
script_dir=$(cd "$(dirname -- "$0")" && pwd)
current_dir=$(pwd)

# Cleanup function
cleanup() {
	echo
	echo "Changing back to original directory: $current_dir"
	cd "$current_dir"
}

# Trap to ensure cleanup runs
trap cleanup EXIT INT TERM

# Change to script dir
echo "Changing to script directory: $script_dir"
cd "$script_dir"

# Activate venv portably and safely
activate_script="./venv/bin/activate"
if [ -f "$activate_script" ]; then
	echo "Activating virtual environment: $activate_script"
	. "$activate_script" # Use '.' (dot), not 'source'
else
	echo "Error: Virtual environment activation script not found at $script_dir/$activate_script" >&2
	exit 1
fi

# Run the server
echo "Starting uvicorn server..."
uvicorn --reload "server:app" --log-config "./log_config.yaml"

# No need for explicit cd here, trap handles it on exit
