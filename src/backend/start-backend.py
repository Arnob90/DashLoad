import os
import sys
import subprocess
from pathlib import Path


def get_venv_python(venv_dir: Path) -> Path:
    """
    Return the path to the venv's python executable in a cross‑platform way.
    """
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    else:
        return venv_dir / "bin" / "python"


def main():
    # Resolve paths
    script_file = Path(__file__).resolve()
    project_root = script_file.parent
    venv_dir = project_root / "venv"
    log_cfg = project_root / "log_config.yaml"

    # Make sure we run from project root
    original_cwd = Path.cwd()
    os.chdir(project_root)

    # Locate python in venv
    python_exe = get_venv_python(venv_dir)
    if not python_exe.exists():
        sys.exit(
            f"❌ Virtualenv python not found at {python_exe}\n"
            "   Did you create your venv? e.g. `python -m venv venv`"
        )

    # If you want to use the uvicorn script directly, you could locate it similarly:
    # uvicorn_bin = venv_dir / ("Scripts" if os.name=="nt" else "bin") / "uvicorn"
    # and call [str(uvicorn_bin), "--reload", "server:app", "--log-config", str(log_cfg)]

    # But using `python -m uvicorn` ensures it's the one installed in your venv:
    cmd = [
        str(python_exe),
        "-m",
        "uvicorn",
        "server:app",
        "--reload",
        "--log-config",
        str(log_cfg),
    ]

    print(f"🚀 Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # Restore original working directory
    os.chdir(original_cwd)


if __name__ == "__main__":
    main()
