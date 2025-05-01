#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import tempfile
import shutil

# Repo to pull from if anything's missing
REPO_URL = "https://github.com/verlorengest/BGTANK.git"
# Files we want side-by-side with this stub
FILES = ["launcher.py", "main.py", "requirements.txt", "icon.ico"]

def get_base_dir():
    # When frozen, __file__ lives in a temp _MEI… folder, so use sys.executable
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def clone_and_copy(base_dir):
    temp_dir = tempfile.mkdtemp(prefix="bgtank_clone_")
    try:
        print("Cloning BGTANK…")
        subprocess.check_call(["git", "clone", REPO_URL, temp_dir], stdout=subprocess.DEVNULL)
        for fname in FILES:
            src = os.path.join(temp_dir, fname)
            dst = os.path.join(base_dir, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
        print("✔ Files synced")
    except Exception as e:
        print("Error during clone or copy:", e)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def ensure_files(base_dir):
    missing = [f for f in FILES if not os.path.exists(os.path.join(base_dir, f))]
    if missing:
        print("Missing:", ", ".join(missing))
        clone_and_copy(base_dir)

def launch_launcher(base_dir):
    launcher = os.path.join(base_dir, "launcher.py")
    if not os.path.exists(launcher):
        print(f"Can't find launcher.py at {launcher}")
        input("Press Enter to exit…")
        return 1

    try:
        if os.name == "nt":
            # Let Windows use its .py file‐association
            os.startfile(launcher)
        else:
            # Fallback for non‐Windows
            subprocess.Popen([sys.executable, launcher], close_fds=True)
    except Exception as e:
        print("Error launching launcher.py:", e)
        input("Press Enter to exit…")
        return 1

    return 0

def main():
    base_dir = get_base_dir()
    ensure_files(base_dir)
    sys.exit(launch_launcher(base_dir))

if __name__ == "__main__":
    main()
