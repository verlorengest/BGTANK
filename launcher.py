import os
import subprocess
import sys
import platform
import time
import colorama
from colorama import Fore, Style, Back

# Initialize colorama
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