#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform
import time
import tempfile
import shutil

# Original BGTANK constants
REPO_URL = "https://github.com/verlorengest/BGTANK.git"
FILES = ["launcher.py", "main.py", "requirements.txt", "icon.ico"]


def ensure_colorama():
    """Check if colorama is installed, and install it if not."""
    try:
        import colorama
        return True
    except ImportError:
        print("Colorama not found. Attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
            print("Colorama installed successfully.")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install colorama. Will continue without color formatting.")
            return False


# Initialize colorama if available
has_colorama = ensure_colorama()
if has_colorama:
    import colorama
    from colorama import Fore, Style

    colorama.init(autoreset=True)


def print_centered(message, width=80, padding_char="="):
    """Print a centered message with padding"""
    if len(message) > width - 4:
        print(f"{padding_char} {message} {padding_char}")
    else:
        padding = (width - len(message) - 2) // 2
        print(f"{padding_char * padding} {message} {padding_char * padding}")


def print_status(message, status_type="INFO", show_time=True):
    """Print formatted status message"""
    if has_colorama:
        colors = {
            "INFO": Fore.CYAN,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "STEP": Fore.MAGENTA
        }
        timestamp = ""
        if show_time:
            timestamp = f"{time.strftime('%H:%M:%S')} "

        color = colors.get(status_type, Fore.WHITE)
        status_display = f"[{status_type}]"

        print(f"{color}{timestamp}{status_display}{Style.RESET_ALL} {message}")
    else:
        # Fallback to non-colored output
        timestamp = ""
        if show_time:
            timestamp = f"{time.strftime('%H:%M:%S')} "
        print(f"{timestamp}[{status_type}] {message}")


def run_command(command, silent=False):
    """Run a shell command and return the exit code"""
    result = subprocess.run(command, shell=True, capture_output=silent)
    return result.returncode


def check_internet():
    """Check if internet connection is available"""
    print_status("Checking internet connection...", "STEP")
    try:
        ping_command = "ping -n 1 google.com" if platform.system() == "Windows" else "ping -c 1 google.com"
        subprocess.check_output(ping_command, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get_base_dir():
    """Get the base directory of the application"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def clone_and_copy(base_dir):
    """Clone the BGTANK repository and copy required files"""
    temp_dir = tempfile.mkdtemp(prefix="bgtank_clone_")
    try:
        print_status("Cloning BGTANK repository...", "STEP")
        subprocess.check_call(["git", "clone", REPO_URL, temp_dir], stdout=subprocess.DEVNULL)
        for fname in FILES:
            src = os.path.join(temp_dir, fname)
            dst = os.path.join(base_dir, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
        print_status("Files synced successfully", "SUCCESS")
    except Exception as e:
        print_status(f"Error during clone or copy: {e}", "ERROR")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def ensure_files(base_dir):
    """Ensure all required files are present"""
    missing = [f for f in FILES if not os.path.exists(os.path.join(base_dir, f))]
    if missing:
        print_status(f"Missing files: {', '.join(missing)}", "WARNING")
        clone_and_copy(base_dir)


def create_venv():
    """Create a virtual environment"""
    print_status("Creating virtual environment...", "STEP")
    try:
        # Create .venv directory
        if run_command(f"{sys.executable} -m venv .venv", silent=True) != 0:
            print_status("Failed to create virtual environment.", "ERROR")
            return False
        print_status("Virtual environment created successfully.", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Exception creating virtual environment: {str(e)}", "ERROR")
        return False


def get_venv_activate_path():
    """Get the path to the activate script based on the platform"""
    if platform.system() == "Windows":
        return os.path.join(".venv", "Scripts", "activate.bat")
    else:  # Unix-like (Linux, macOS)
        return os.path.join(".venv", "bin", "activate")


def install_requirements(use_venv=True):
    """Install requirements from requirements.txt"""
    print_status("Installing requirements...", "STEP")

    if use_venv:
        if platform.system() == "Windows":
            cmd = f"call {get_venv_activate_path()} && pip install -r requirements.txt"
        else:
            cmd = f"source {get_venv_activate_path()} && pip install -r requirements.txt"
    else:
        cmd = f"{sys.executable} -m pip install -r requirements.txt"

    if run_command(cmd) != 0:
        print_status("Failed to install requirements.", "ERROR")
        return False

    print_status("Requirements installed successfully.", "SUCCESS")
    return True


def run_main(use_venv=True):
    """Run the main.py script"""
    print_centered("LAUNCHING APPLICATION")
    print_status("Starting application...", "STEP")

    if use_venv:
        if platform.system() == "Windows":
            cmd = f"call {get_venv_activate_path()} && python main.py"
        else:
            cmd = f"source {get_venv_activate_path()} && python main.py"
    else:
        cmd = f"{sys.executable} main.py"

    return run_command(cmd)


def main():
    """Main function combining functionality from both original scripts"""
    # Change to the base directory to ensure relative paths work correctly
    base_dir = get_base_dir()
    os.chdir(base_dir)

    # Ensure all required files are present
    ensure_files(base_dir)

    # Clear screen and show launcher info
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    print_centered("BGTANK LAUNCHER", width=60)
    print_status(f"System: {platform.system()} {platform.release()}")
    print_status(f"Python: {platform.python_version()}")
    print("")

    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print_status("requirements.txt not found. Continuing without installing dependencies.", "WARNING")
        has_requirements = False
    else:
        has_requirements = True

    # Check for virtual environment
    venv_activate = get_venv_activate_path()
    venv_exists = os.path.exists(venv_activate)

    # Try to use venv if exists or create one
    use_venv = True
    if not venv_exists:
        print_status("Virtual environment not found.", "INFO")
        try:
            if create_venv():
                print_status("Will use the newly created virtual environment.", "INFO")
            else:
                print_status("Could not create virtual environment. Will attempt to run directly.", "WARNING")
                use_venv = False
        except Exception as e:
            print_status(f"Exception when creating venv: {str(e)}. Will attempt to run directly.", "WARNING")
            use_venv = False
    else:
        print_status("Virtual environment found.", "SUCCESS")

    # Check internet connection
    online = check_internet()

    # Install requirements if they exist and we have internet
    if has_requirements:
        if online:
            print_status("Internet connection detected.", "SUCCESS")
            if not install_requirements(use_venv):
                print_status("Failed to install with venv. Trying system Python...", "WARNING")
                if not install_requirements(use_venv=False):
                    print_status("Could not install requirements. Attempting to run anyway.", "WARNING")
        else:
            print_status("No internet connection. Skipping dependency installation.", "WARNING")
            print_status("Application may not work properly without required dependencies.", "WARNING")

    # Run the main application
    print("")
    exit_code = run_main(use_venv)

    if exit_code == 0:
        print_status("Application exited normally.", "SUCCESS")
    else:
        print_status(f"Application exited with code: {exit_code}", "ERROR")

    print_centered("FINISHED", width=60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()