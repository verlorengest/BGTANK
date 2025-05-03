#!/usr/bin/env python3
"""
BGTANK.py - A simplified launcher that runs launcher.py from the same directory
"""

import os
import sys
import subprocess
import platform
import time
import logging
import traceback

# Configure logging
log_dir = os.path.join(os.path.expanduser("~"), ".bgtank")
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "bgtank_launcher.log")
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def log_message(message, error=False):
    """Log a message and print it to console"""
    print(message)
    if error:
        logging.error(message)
    else:
        logging.info(message)


def get_executable_dir():
    """Get the directory where the executable is located"""
    if getattr(sys, 'frozen', False):
        # Running as executable
        exe_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    log_message(f"Executable directory: {exe_dir}")
    return exe_dir


def list_files(directory):
    """List files in a directory for debugging"""
    try:
        log_message(f"Files in {directory}:")
        if os.path.exists(directory):
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    log_message(f"  - {item} ({size} bytes)")
                else:
                    log_message(f"  - {item}/ (directory)")
        else:
            log_message(f"Directory not found: {directory}", error=True)
    except Exception as e:
        log_message(f"Error listing directory contents: {e}", error=True)


def launch_script_with_python(script_path):
    """Launch a Python script using the correct Python interpreter with visible terminal"""
    try:
        # When frozen as exe, we need to use the actual Python interpreter
        if getattr(sys, 'frozen', False):
            # For PyInstaller, we should use the system's Python
            # Try to find Python in the PATH
            if platform.system().lower() == "windows":
                python_exec = "python"  # Windows usually has 'python' in PATH
            else:
                python_exec = "python3"  # Unix-like systems usually use python3
        else:
            # When running as script, use the current interpreter
            python_exec = sys.executable

        cmd = [python_exec, script_path]
        log_message(f"Attempting to run: {' '.join(cmd)}")

        if platform.system().lower() == "windows":
            # Windows: show console window
            process = subprocess.Popen(
                cmd
                # Removed creationflags=subprocess.CREATE_NO_WINDOW to show the terminal
            )
            log_message(f"Started process with PID: {process.pid}")
        else:
            # Unix: show terminal
            process = subprocess.Popen(
                cmd,
                start_new_session=True
                # Removed stdout/stderr redirection to show output
            )
            log_message(f"Started process with PID: {process.pid}")

        # Give it a moment to start
        time.sleep(0.5)

        # Check if process is still running (simple check)
        if process.poll() is None:
            log_message("Process started successfully")
            return True
        else:
            log_message(f"Process exited with code: {process.returncode}", error=True)
            return False
    except Exception as e:
        log_message(f"Error launching script: {e}", error=True)
        traceback.print_exc()
        logging.exception("Exception details")
        return False


def main():
    """Main function"""
    try:
        log_message(f"BGTANK Launcher starting on {platform.system()}")
        log_message(f"Python: {sys.version}")
        log_message(f"Executable: {sys.executable}")

        # Get directory of the executable
        exe_dir = get_executable_dir()

        # List files in the directory (for debugging)
        list_files(exe_dir)

        # IMPORTANT: Change to the executable directory
        os.chdir(exe_dir)
        log_message(f"Changed working directory to: {os.getcwd()}")

        # Path to launcher.py (should be in the same directory)
        launcher_path = os.path.join(exe_dir, "launcher.py")

        # Check if launcher.py exists
        if not os.path.isfile(launcher_path):
            log_message(f"ERROR: launcher.py not found at: {launcher_path}", error=True)
            log_message("Make sure launcher.py is in the same directory as this executable.", error=True)

            # Wait for user input if running as executable
            if getattr(sys, 'frozen', False):
                input("Press Enter to exit...")
            return 1

        log_message(f"Found launcher.py: {launcher_path} ({os.path.getsize(launcher_path)} bytes)")

        # Launch launcher.py
        if launch_script_with_python(launcher_path):
            log_message("Successfully launched launcher.py")
            return 0
        else:
            log_message("Failed to launch launcher.py", error=True)

            # Wait for user input if running as executable
            if getattr(sys, 'frozen', False):
                input("Press Enter to exit...")
            return 1

    except Exception as e:
        log_message(f"Unexpected error: {e}", error=True)
        traceback.print_exc()
        logging.exception("Exception details")

        # Wait for user input if running as executable
        if getattr(sys, 'frozen', False):
            input("Press Enter to exit...")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)