# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
import queue
import subprocess
import importlib.util
from datetime import datetime
import webbrowser


class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BGTANK - Background Remover")
        self.root.geometry("700x550")

        # Lock window size - prevent resizing
        self.root.resizable(False, False)

        # Set color scheme
        self.bg_color = "#f5f5f5"
        self.accent_color = "#4a6ea9"
        self.text_color = "#333333"
        self.success_color = "#4caf50"
        self.error_color = "#f44336"

        # Configure root
        self.root.configure(bg=self.bg_color)

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Configure button style
        self.style.configure(
            "Accent.TButton",
            background=self.accent_color,
            foreground="white",
            padding=10,
            font=('Segoe UI', 10, 'bold')
        )

        # Configure label style
        self.style.configure(
            "TLabel",
            background=self.bg_color,
            foreground=self.text_color,
            font=('Segoe UI', 10)
        )

        # Configure heading style
        self.style.configure(
            "Heading.TLabel",
            background=self.bg_color,
            foreground=self.accent_color,
            font=('Segoe UI', 20, 'bold')
        )

        # Configure status frame
        self.style.configure(
            "TLabelframe",
            background=self.bg_color,
            foreground=self.text_color
        )

        self.style.configure(
            "TLabelframe.Label",
            background=self.bg_color,
            foreground=self.text_color,
            font=('Segoe UI', 10, 'bold')
        )

        # Configure progressbar
        self.style.configure(
            "TProgressbar",
            thickness=10,
            background=self.accent_color
        )

        # Configure link style
        self.style.configure(
            "Link.TLabel",
            background=self.bg_color,
            foreground="#0066cc",
            font=('Segoe UI', 9, 'underline')
        )

        # Main frame
        main_frame = ttk.Frame(root, padding="20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.style.configure("TFrame", background=self.bg_color)

        # App logo/title
        title_frame = ttk.Frame(main_frame, style="TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(title_frame, text="BGTANK", style="Heading.TLabel")
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(title_frame, text="Background Remover Tool",
                                   font=('Segoe UI', 12))
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))

        # GitHub link in title frame (more visible location)
        github_frame = ttk.Frame(title_frame, style="TFrame")
        github_frame.pack(side=tk.RIGHT, padx=(10, 0), pady=(8, 0))

        github_label = ttk.Label(
            github_frame,
            text="GitHub: ",
            font=('Segoe UI', 9),
            foreground="#666666"
        )
        github_label.pack(side=tk.LEFT)

        github_link = ttk.Label(
            github_frame,
            text="verlorengest",
            style="Link.TLabel",
            cursor="hand2"
        )
        github_link.pack(side=tk.LEFT)
        github_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/verlorengest"))

        # Info frame
        info_frame = ttk.Frame(main_frame, style="TFrame")
        info_frame.pack(fill=tk.X, pady=(0, 15))

        # Instructions
        instructions = ttk.Label(
            info_frame,
            text="Bulk background removal tool. Select images and process them to create transparent backgrounds.",
            wraplength=600
        )
        instructions.pack(side=tk.LEFT, pady=(0, 0))

        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings")
        settings_frame.pack(fill=tk.X, pady=(0, 15))

        # Output directory setting
        output_dir_frame = ttk.Frame(settings_frame, style="TFrame")
        output_dir_frame.pack(fill=tk.X, padx=10, pady=5)

        output_dir_label = ttk.Label(output_dir_frame, text="Output Folder:")
        output_dir_label.pack(side=tk.LEFT, padx=(0, 5))

        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(output_dir_frame, textvariable=self.output_dir_var, width=40)
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_browse_output = ttk.Button(
            output_dir_frame,
            text="Browse",
            command=self.select_output_dir,
            style="Accent.TButton",
            width=10
        )
        self.btn_browse_output.pack(side=tk.RIGHT)

        # File suffix setting
        suffix_frame = ttk.Frame(settings_frame, style="TFrame")
        suffix_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        suffix_label = ttk.Label(suffix_frame, text="Output File Suffix:")
        suffix_label.pack(side=tk.LEFT, padx=(0, 5))

        self.suffix_var = tk.StringVar(value="_no_bg")
        self.suffix_entry = ttk.Entry(suffix_frame, textvariable=self.suffix_var, width=15)
        self.suffix_entry.pack(side=tk.LEFT, padx=(0, 5))

        suffix_example = ttk.Label(suffix_frame, text="Example: image.jpg → image_no_bg.png", font=('Segoe UI', 8))
        suffix_example.pack(side=tk.LEFT, padx=(5, 0))

        # Save settings button
        self.btn_save_settings = ttk.Button(
            suffix_frame,
            text="Save Settings",
            command=self.save_settings,
            style="Accent.TButton",
            width=15
        )
        self.btn_save_settings.pack(side=tk.RIGHT)

        # Counter and status frame
        status_row = ttk.Frame(main_frame, style="TFrame")
        status_row.pack(fill=tk.X, pady=(0, 15))

        # Image counter
        self.counter_label = ttk.Label(status_row, text="Ready")
        self.counter_label.pack(side=tk.LEFT)

        # Time estimate
        self.time_label = ttk.Label(status_row, text="")
        self.time_label.pack(side=tk.RIGHT)

        # Progress frame
        progress_frame = ttk.Frame(main_frame, style="TFrame")
        progress_frame.pack(fill=tk.X, pady=(0, 20))

        # Progress bar
        self.progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=450,
            mode="determinate",
            style="TProgressbar"
        )
        self.progress.pack(fill=tk.X)

        # Progress percentage
        self.progress_percentage = ttk.Label(progress_frame, text="0%")
        self.progress_percentage.pack(pady=(5, 0), anchor=tk.E)

        # Buttons frame
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.pack(fill=tk.X, pady=(0, 20))

        # Select images button
        self.btn_select = ttk.Button(
            button_frame,
            text="Select Images",
            command=self.select_images,
            style="Accent.TButton"
        )
        self.btn_select.pack(side=tk.LEFT, padx=(0, 10))

        # Process button
        self.btn_process = ttk.Button(
            button_frame,
            text="Process Images",
            command=self.start_processing,
            state=tk.DISABLED,
            style="Accent.TButton"
        )
        self.btn_process.pack(side=tk.RIGHT)

        # Open output folder button
        self.btn_open_output = ttk.Button(
            button_frame,
            text="Open Output Folder",
            command=self.open_output_folder,
            state=tk.DISABLED,
            style="Accent.TButton"
        )
        self.btn_open_output.pack(side=tk.RIGHT, padx=(0, 10))

        # Install rembg button (initially hidden)
        self.btn_install = ttk.Button(
            button_frame,
            text="Install rembg",
            command=self.install_rembg,
            style="Accent.TButton"
        )
        self.btn_install.pack(side=tk.RIGHT, padx=(0, 10))
        self.btn_install.pack_forget()  # Hide initially

        # Status area
        self.status_frame = ttk.LabelFrame(main_frame, text="Status Log")
        self.status_frame.pack(fill=tk.BOTH, expand=True)

        # Create a frame for the status text and scrollbar
        status_text_frame = ttk.Frame(self.status_frame, style="TFrame")
        status_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Status text
        self.status_text = tk.Text(
            status_text_frame,
            height=8,
            width=60,
            wrap=tk.WORD,
            bg="white",
            fg=self.text_color,
            font=('Segoe UI', 9),
            borderwidth=1,
            relief=tk.SOLID
        )
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.status_text.config(state=tk.DISABLED)

        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(status_text_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Footer frame (copyright removed)
        footer_frame = ttk.Frame(main_frame, style="TFrame")
        footer_frame.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)

        # Initialize variables
        self.file_paths = []
        self.output_dir = ""
        self.suffix = "_no_bg"  # Default suffix
        self.queue = queue.Queue()
        self.is_processing = False
        self.session = None
        self.start_time = None
        self.processed_count = 0

        # Check if rembg is installed and initialize
        self.check_rembg()

    def check_rembg(self):
        """Check if rembg is installed and available"""
        has_rembg = importlib.util.find_spec("rembg") is not None

        if has_rembg:
            try:
                # Try to import and initialize
                from rembg import remove, new_session
                self.remove_bg = remove
                self.session = new_session()
                self.update_status("System ready. Please select images to process.")
                self.btn_select.config(state=tk.NORMAL)
                self.btn_install.pack_forget()  # Hide install button
            except Exception as e:
                self.update_status(f"rembg package is installed but encountered an issue: {str(e)}", is_error=True)
                self.show_install_button()
        else:
            self.update_status("'rembg' package not found! Installation required.", is_error=True)
            self.show_install_button()

    def show_install_button(self):
        """Show the install button and disable select button"""
        self.btn_select.config(state=tk.DISABLED)
        self.btn_install.pack(side=tk.RIGHT, padx=(0, 10))

    def install_rembg(self):
        """Install rembg package and dependencies"""
        self.update_status("Installing rembg package and dependencies... This may take a few minutes.")
        self.btn_install.config(state=tk.DISABLED, text="Installing...")

        # Start installation in a separate thread
        threading.Thread(target=self._install_rembg_thread, daemon=True).start()

    def _install_rembg_thread(self):
        """Thread for installing rembg and dependencies"""
        try:
            # Get the Python executable path
            python_exe = sys.executable

            # First, try to install onnxruntime
            self.queue.put(("status", "Installing onnxruntime dependency..."))
            process = subprocess.Popen(
                [python_exe, '-m', 'pip', 'install', 'onnxruntime'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            stdout, stderr = process.communicate()

            # Then install rembg (even if onnxruntime had issues)
            self.queue.put(("status", "Installing rembg package..."))
            process = subprocess.Popen(
                [python_exe, '-m', 'pip', 'install', 'rembg'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            stdout, stderr = process.communicate()

            if process.returncode == 0:
                # Check if both packages are properly installed
                try:
                    import onnxruntime
                    import rembg
                    self.queue.put(("install_success", None))
                except ImportError as e:
                    # Missing dependency even after installation
                    missing_module = str(e).split("'")[1] if "'" in str(e) else str(e)
                    self.queue.put(("install_error", f"Package installed but missing dependency: {missing_module}"))
                    # Update button text to install the missing dependency
                    self.queue.put(("update_button", f"Install {missing_module}"))
            else:
                self.queue.put(("install_error", stderr))

        except Exception as e:
            self.queue.put(("install_error", str(e)))

        # Check queue for updates
        self.root.after(100, self.check_queue)

    def update_status(self, message, is_error=False, is_success=False):
        """Update status text widget with the provided message"""
        self.status_text.config(state=tk.NORMAL)

        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Set text color based on message type
        if is_error:
            tag = "error"
            self.status_text.tag_config(tag, foreground=self.error_color)
        elif is_success:
            tag = "success"
            self.status_text.tag_config(tag, foreground=self.success_color)
        else:
            tag = "normal"
            self.status_text.tag_config(tag, foreground=self.text_color)

        self.status_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.status_text.tag_config("timestamp", foreground="#666666")
        self.status_text.insert(tk.END, f"{message}\n", tag)

        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def select_images(self):
        """Open dialog to select images"""
        self.file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )

        if not self.file_paths:
            self.update_status("No images selected.")
            return

        self.counter_label.config(text=f"{len(self.file_paths)} images selected")
        self.update_status(f"{len(self.file_paths)} images selected", is_success=True)

        # Show file names in status
        if len(self.file_paths) <= 10:  # Only show if there are 10 or fewer files
            for path in self.file_paths:
                self.update_status(f"- {os.path.basename(path)}")
        else:
            self.update_status(f"First few files: {', '.join([os.path.basename(p) for p in self.file_paths[:3]])}...")

        # Enable process button if output directory is set
        if self.output_dir:
            self.btn_process.config(state=tk.NORMAL)

    def select_output_dir(self):
        """Open dialog to select output directory"""
        output_dir = filedialog.askdirectory(title="Select output folder")
        if output_dir:
            self.output_dir = output_dir
            self.output_dir_var.set(output_dir)
            self.update_status(f"Output directory set to: {output_dir}")

            # Enable open output folder button
            self.btn_open_output.config(state=tk.NORMAL)

            # Enable process button if images are selected
            if self.file_paths:
                self.btn_process.config(state=tk.NORMAL)

    def save_settings(self):
        """Save the current settings"""
        # Update suffix
        new_suffix = self.suffix_var.get()
        if new_suffix:
            self.suffix = new_suffix
            self.update_status(f"File suffix set to: '{new_suffix}'", is_success=True)
        else:
            self.suffix = "_no_bg"  # Default if empty
            self.suffix_var.set("_no_bg")
            self.update_status("File suffix reset to default: '_no_bg'")

        # Update output directory
        output_dir = self.output_dir_var.get()
        if output_dir and output_dir != self.output_dir:
            if os.path.exists(output_dir) or self.create_directory(output_dir):
                self.output_dir = output_dir
                self.update_status(f"Output directory set to: {output_dir}", is_success=True)
                self.btn_open_output.config(state=tk.NORMAL)
            else:
                self.update_status(f"Invalid output directory: {output_dir}", is_error=True)
                self.output_dir_var.set(self.output_dir)  # Reset to previous

    def create_directory(self, dir_path):
        """Create a directory if it doesn't exist"""
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            return True
        except Exception as e:
            self.update_status(f"Failed to create directory: {str(e)}", is_error=True)
            return False

    def open_output_folder(self):
        """Open the output folder in file explorer"""
        if not self.output_dir:
            self.update_status("No output directory set", is_error=True)
            return

        if not os.path.exists(self.output_dir):
            if not self.create_directory(self.output_dir):
                return

        try:
            # Open folder in file explorer (works on Windows, macOS, and most Linux)
            if sys.platform == 'win32':
                os.startfile(self.output_dir)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', self.output_dir])
            else:  # Linux
                subprocess.run(['xdg-open', self.output_dir])

            self.update_status(f"Opened output folder: {self.output_dir}")
        except Exception as e:
            self.update_status(f"Failed to open output folder: {str(e)}", is_error=True)

    def start_processing(self):
        """Start the background removal process"""
        if not self.file_paths:
            messagebox.showwarning("Warning", "Please select images first!")
            return

        if not self.output_dir:
            self.select_output_dir()  # Prompt to select output directory
            if not self.output_dir:
                self.update_status("No output directory selected. Process canceled.")
                return

        # Update the output directory variable with current entry value
        self.output_dir = self.output_dir_var.get()

        # Check if output directory exists and is writable
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
                self.update_status(f"Created output directory: {self.output_dir}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory:\n{str(e)}")
                return

        # Check if rembg is loaded properly
        if not hasattr(self, 'remove_bg') or not self.session:
            self.update_status("rembg package is not functioning properly. Please try reinstalling.", is_error=True)
            self.show_install_button()
            return

        # Reset progress bar
        self.progress["value"] = 0
        self.progress["maximum"] = len(self.file_paths)
        self.progress_percentage.config(text="0%")

        # Reset counter
        self.processed_count = 0

        # Disable buttons during processing
        self.btn_select.config(state=tk.DISABLED)
        self.btn_process.config(state=tk.DISABLED)
        self.btn_save_settings.config(state=tk.DISABLED)
        self.btn_browse_output.config(state=tk.DISABLED)
        self.suffix_entry.config(state=tk.DISABLED)
        self.output_dir_entry.config(state=tk.DISABLED)

        # Record start time
        self.start_time = datetime.now()

        # Update status
        self.update_status(f"Starting background removal for {len(self.file_paths)} images...", is_success=True)
        self.update_status(f"Output directory: {self.output_dir}")

        # Start processing thread
        self.is_processing = True
        threading.Thread(target=self.process_images, daemon=True).start()

        # Start checking queue for updates
        self.root.after(100, self.check_queue)

    def update_time_estimate(self):
        """Update the estimated time remaining"""
        if self.start_time and self.processed_count > 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            images_left = len(self.file_paths) - self.processed_count

            # Calculate time per image
            time_per_image = elapsed / self.processed_count

            # Estimate remaining time
            remaining_seconds = time_per_image * images_left

            # Format the remaining time
            if remaining_seconds < 60:
                time_str = f"~{int(remaining_seconds)}s remaining"
            elif remaining_seconds < 3600:
                time_str = f"~{int(remaining_seconds / 60)}m {int(remaining_seconds % 60)}s remaining"
            else:
                hours = int(remaining_seconds / 3600)
                minutes = int((remaining_seconds % 3600) / 60)
                time_str = f"~{hours}h {minutes}m remaining"

            self.time_label.config(text=time_str)

    def process_images(self):
        """Process images in a separate thread"""
        try:
            for i, input_path in enumerate(self.file_paths):
                try:
                    # Update status via queue
                    self.queue.put(("status", f"Processing: {os.path.basename(input_path)}"))

                    # Open image and remove background
                    with open(input_path, 'rb') as i_file:
                        input_data = i_file.read()
                        output_data = self.remove_bg(input_data, session=self.session)

                    # Save the result
                    filename = os.path.basename(input_path)
                    filename_no_ext = os.path.splitext(filename)[0]
                    output_path = os.path.join(self.output_dir, f"{filename_no_ext}{self.suffix}.png")

                    with open(output_path, 'wb') as o_file:
                        o_file.write(output_data)

                    # Update progress via queue
                    self.processed_count = i + 1
                    self.queue.put(("progress", self.processed_count))
                    self.queue.put(
                        ("success", f"Completed: {os.path.basename(input_path)} -> {os.path.basename(output_path)}"))

                    # Update time estimate
                    self.queue.put(("update_time", None))

                except Exception as e:
                    self.queue.put(("error", f"Error ({os.path.basename(input_path)}): {str(e)}"))

            # All done
            self.queue.put(("completed", None))

        except Exception as e:
            self.queue.put(("fatal_error", str(e)))

    def check_queue(self):
        """Check for updates from the processing thread"""
        try:
            while True:
                message_type, message = self.queue.get_nowait()

                if message_type == "status":
                    self.update_status(message)
                elif message_type == "success":
                    self.update_status(message, is_success=True)
                elif message_type == "error":
                    self.update_status(message, is_error=True)
                elif message_type == "progress":
                    self.progress["value"] = message
                    percentage = int((message / len(self.file_paths)) * 100)
                    self.progress_percentage.config(text=f"{percentage}%")
                    self.counter_label.config(text=f"Processing: {message}/{len(self.file_paths)}")
                elif message_type == "update_time":
                    self.update_time_estimate()
                elif message_type == "fatal_error":
                    messagebox.showerror("Critical Error", f"A critical error occurred during processing:\n{message}")
                    self.finish_processing()
                elif message_type == "completed":
                    # Calculate total time
                    total_time = datetime.now() - self.start_time
                    minutes, seconds = divmod(total_time.total_seconds(), 60)
                    time_str = f"{int(minutes)}m {int(seconds)}s" if minutes > 0 else f"{int(seconds)}s"

                    self.update_status(f"All tasks completed in {time_str}!", is_success=True)
                    result = messagebox.askquestion("Success",
                                                    f"All processing completed.\nOutput saved to: {self.output_dir}\n\nWould you like to open the output folder?")
                    self.finish_processing()

                    if result == "yes":
                        self.open_output_folder()
                elif message_type == "install_success":
                    self.update_status("rembg package installed successfully!", is_success=True)
                    self.btn_install.config(text="Install rembg")
                    self.check_rembg()  # Re-check rembg
                elif message_type == "install_error":
                    self.update_status(f"rembg installation failed: {message}", is_error=True)
                    self.btn_install.config(state=tk.NORMAL, text="Install rembg")
                    # Show manual installation instructions
                    self.update_status("For manual installation, run this command in terminal:", is_error=True)
                    self.update_status("pip install rembg", is_error=True)

                self.queue.task_done()

        except queue.Empty:
            if self.is_processing:
                self.root.after(100, self.check_queue)

    def finish_processing(self):
        """Reset the UI after processing is complete"""
        self.is_processing = False
        self.btn_select.config(state=tk.NORMAL)
        self.btn_process.config(state=tk.NORMAL if self.file_paths else tk.DISABLED)
        self.btn_save_settings.config(state=tk.NORMAL)
        self.btn_browse_output.config(state=tk.NORMAL)
        self.suffix_entry.config(state=tk.NORMAL)
        self.output_dir_entry.config(state=tk.NORMAL)
        self.counter_label.config(text="Ready")
        self.time_label.config(text="")
        self.update_status("Process completed.")


if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    app = BackgroundRemoverApp(root)

    # Set app icon for both window and taskbar in Windows
    try:
        # Path to your icon file
        icon_path = "icon.ico"  # Make sure this file exists in the same directory as your script

        # Set window icon
        root.iconbitmap(icon_path)

        # Set taskbar icon (Windows only)
        if sys.platform == 'win32':
            # This approach uses the Windows API through ctypes
            import ctypes

            myappid = 'verlorengest.bgtank.backgroundremover.1.0'  # Arbitrary string for Windows to identify your app
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

            # Alternative method for taskbar icon if the above doesn't work
            root.wm_iconbitmap(default=icon_path)
    except Exception as e:
        print(f"Could not load icon: {e}")  # This will handle missing icon gracefully

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Start the main loop
    root.mainloop()