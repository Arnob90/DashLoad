# build.py
import subprocess
import sys
from pathlib import Path
import shlex


def main():
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir
    server_path = project_root / "src" / "server.py"
    dist_path = project_root / "dist"
    venv_path = project_root / "venv"
    venv_pyinstaller: str = ""
    if sys.platform == "win32":
        venv_pyinstaller = str(venv_path / "Scripts" / "pyinstaller")
    else:
        venv_pyinstaller = str(venv_path / "bin" / "pyinstaller")
    cmd = shlex.split(
        f"{venv_pyinstaller} --onefile --distpath {dist_path} {server_path}"
    )
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
