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
import torch
import numpy as np
from rembg.bg import download_models


class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BGTANK - Background Remover")
        self.root.geometry("700x750")

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

        model_frame = ttk.Frame(settings_frame, style="TFrame")
        model_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        model_label = ttk.Label(model_frame, text="Background Removal Model:")
        model_label.pack(side=tk.LEFT, padx=(0, 5))

        self.model_var = tk.StringVar(value="birefnet")

        # Create radio buttons for model selection
        self.rb_birefnet = ttk.Radiobutton(
            model_frame,
            text="BiRefNet (High accuracy, slower)",
            variable=self.model_var,
            value="birefnet"
        )
        self.rb_birefnet.pack(side=tk.LEFT, padx=(0, 10))

        self.rb_u2net = ttk.Radiobutton(
            model_frame,
            text="U2Net (Faster, lower accuracy)",
            variable=self.model_var,
            value="u2net"
        )
        self.rb_u2net.pack(side=tk.LEFT)

        # Add tooltip or helper text
        model_tooltip = ttk.Label(
            settings_frame,
            text="• BiRefNet: High-quality results with better edge detection but slower processing.\n• U2Net: Faster processing with good results for simple backgrounds.",
            font=('Segoe UI', 8),
            foreground="#666666"
        )
        model_tooltip.pack(fill=tk.X, padx=15, pady=(0, 10))

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

        # Install dependencies button (initially hidden)
        self.btn_install = ttk.Button(
            button_frame,
            text="Install Dependencies",
            command=self.install_dependencies,
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
        self.model_name = "birefnet"  # Default model
        self.session = None
        self.start_time = None
        self.processed_count = 0

        # Check required dependencies and initialize
        self.check_dependencies()

    def check_dependencies(self):
        """Check if required dependencies are installed and available"""
        dependencies_ok = True
        missing_deps = []

        # Check for rembg
        if importlib.util.find_spec("rembg") is None:
            dependencies_ok = False
            missing_deps.append("rembg")

        # Check for torch
        if importlib.util.find_spec("torch") is None:
            dependencies_ok = False
            missing_deps.append("torch")

        # Check for numpy
        if importlib.util.find_spec("numpy") is None:
            dependencies_ok = False
            missing_deps.append("numpy")

        if dependencies_ok:
            try:
                # Initialize model
                self.init_model()
                self.update_status("System ready. Models loaded successfully.", is_success=True)
                self.btn_select.config(state=tk.NORMAL)
                self.btn_install.pack_forget()  # Hide install button
            except Exception as e:
                self.update_status(f"Error initializing models: {str(e)}", is_error=True)
                self.show_install_button()
        else:
            missing_str = ", ".join(missing_deps)
            self.update_status(f"Missing dependencies: {missing_str}. Installation required.", is_error=True)
            self.show_install_button()

    def remove_bg_with_model(self, input_data, session=None):
        """Remove background using the selected model"""
        try:
            # Use the default rembg remove function with the selected model session
            from rembg import remove
            return remove(
                input_data,
                session=self.session,
                only_mask=False,
                alpha_matting=True if self.model_name == "birefnet" else False
            )
        except Exception as e:
            self.update_status(f"Error in model processing: {str(e)}", is_error=True)
            raise e


    def init_model(self):
        """Initialize the selected background removal model"""
        try:
            # Import necessary modules from rembg
            from rembg.session_factory import new_session

            # Handle the download_models with correct parameters
            try:
                from rembg.bg import download_models, MODELS
                # Pass the required models parameter
                download_models(MODELS)
            except (ImportError, TypeError):
                # Alternative approach if the above fails
                try:
                    # Try alternative import path
                    from rembg import download_models
                    # Try with all available models including BiRefNet and U2Net
                    download_models([
                        "u2net", "u2net_human_seg", "u2netp", "silueta",
                        "isnet", "isnet-general-use", "sam", "birefnet_resnet50"
                    ])
                except Exception:
                    # Skip download if it's not working - the model may already be downloaded
                    self.update_status("Skipping model download - using existing models if available", is_success=True)

            # Get the selected model name
            self.model_name = self.model_var.get()

            # Create a session with the selected model
            self.session = new_session(self.model_name)

            # Define remove_bg function that uses the selected model
            self.remove_bg = self.remove_bg_with_model

            self.update_status(f"Model '{self.model_name}' initialized successfully", is_success=True)
        except Exception as e:
            self.update_status(f"Failed to initialize model: {str(e)}", is_error=True)
            raise e


    def init_birefnet_model(self):
        """Initialize the BiRefNet model"""
        try:
            # Import necessary modules from rembg
            from rembg.session_factory import new_session

            # Handle the download_models with correct parameters
            try:
                from rembg.bg import download_models, MODELS
                # Pass the required models parameter
                download_models(MODELS)
            except (ImportError, TypeError):
                # Alternative approach if the above fails
                try:
                    # Try alternative import path
                    from rembg import download_models
                    # Try with u2net_human_seg which is usually required for BiRefNet
                    download_models(
                        ["u2net", "u2net_human_seg", "u2netp", "silueta", "isnet", "isnet-general-use", "sam",
                         "birefnet_resnet50"])
                except Exception:
                    # Skip download if it's not working - the model may already be downloaded
                    self.update_status("Skipping model download - using existing models if available", is_success=True)

            # Create a session with BiRefNet model
            self.session = new_session("birefnet")

            # Define remove_bg function that uses the BiRefNet model
            self.remove_bg = self.remove_bg_with_birefnet

            self.update_status("BiRefNet model initialized successfully", is_success=True)
        except Exception as e:
            self.update_status(f"Failed to initialize BiRefNet model: {str(e)}", is_error=True)
            raise e

    def remove_bg_with_birefnet(self, input_data, session=None):
        """Remove background using BiRefNet model"""
        try:
            # Use the default rembg remove function but ensure BiRefNet model is used
            from rembg import remove
            return remove(input_data, session=self.session, only_mask=False, alpha_matting=True)
        except Exception as e:
            self.update_status(f"Error in BiRefNet processing: {str(e)}", is_error=True)
            raise e

    def show_install_button(self):
        """Show the install button and disable select button"""
        self.btn_select.config(state=tk.DISABLED)
        self.btn_install.pack(side=tk.RIGHT, padx=(0, 10))

    def install_dependencies(self):
        """Install required packages and dependencies"""
        self.update_status("Installing required dependencies... This may take a few minutes.")
        self.btn_install.config(state=tk.DISABLED, text="Installing...")

        # Start installation in a separate thread
        threading.Thread(target=self._install_dependencies_thread, daemon=True).start()

    def _install_dependencies_thread(self):
        """Thread for installing dependencies"""
        try:
            # Get the Python executable path
            python_exe = sys.executable

            # Install dependencies
            dependencies = ["torch", "numpy", "rembg", "onnxruntime"]

            for dep in dependencies:
                self.queue.put(("status", f"Installing {dep}..."))
                process = subprocess.Popen(
                    [python_exe, '-m', 'pip', 'install', dep],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    self.queue.put(("error", f"Failed to install {dep}: {stderr}"))

            # Check if dependencies are installed
            missing_deps = []
            for dep in dependencies:
                try:
                    __import__(dep)
                except ImportError:
                    missing_deps.append(dep)

            if missing_deps:
                self.queue.put(("install_error", f"Failed to install: {', '.join(missing_deps)}"))
            else:
                self.queue.put(("install_success", None))
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

        # Update model selection
        new_model = self.model_var.get()
        if new_model != self.model_name:
            self.model_name = new_model
            self.update_status(f"Model changed to {new_model}. Initializing...", is_success=True)
            try:
                self.init_model()
            except Exception as e:
                self.update_status(f"Error changing model: {str(e)}", is_error=True)
                # Revert to previous model if failed
                self.model_var.set(self.model_name)

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

        # Update model selection if changed
        if self.model_var.get() != self.model_name:
            self.model_name = self.model_var.get()
            try:
                self.init_model()
            except Exception as e:
                self.update_status(f"Error initializing model: {str(e)}", is_error=True)
                return

        # Check if output directory exists and is writable
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
                self.update_status(f"Created output directory: {self.output_dir}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output directory:\n{str(e)}")
                return

        # Check if model is loaded properly
        if not hasattr(self, 'remove_bg') or not self.session:
            self.update_status("Model is not functioning properly. Please try reinstalling.", is_error=True)
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
        self.rb_birefnet.config(state=tk.DISABLED)
        self.rb_u2net.config(state=tk.DISABLED)

        # Record start time
        self.start_time = datetime.now()

        # Update status
        model_name_display = "BiRefNet" if self.model_name == "birefnet" else "U2Net"
        self.update_status(
            f"Starting background removal with {model_name_display} for {len(self.file_paths)} images...",
            is_success=True)
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
                    self.queue.put(("status", f"Processing with BiRefNet: {os.path.basename(input_path)}"))

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
                                                    f"All processing completed with BiRefNet.\nOutput saved to: {self.output_dir}\n\nWould you like to open the output folder?")
                    self.finish_processing()

                    if result == "yes":
                        self.open_output_folder()
                elif message_type == "install_success":
                    self.update_status("Dependencies installed successfully!", is_success=True)
                    self.btn_install.config(text="Install Dependencies")
                    self.check_dependencies()  # Re-check dependencies
                elif message_type == "install_error":
                    self.update_status(f"Installation failed: {message}", is_error=True)
                    self.btn_install.config(state=tk.NORMAL, text="Install Dependencies")
                    # Show manual installation instructions
                    self.update_status("For manual installation, run these commands in terminal:", is_error=True)
                    self.update_status("pip install torch numpy rembg onnxruntime", is_error=True)

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
        self.rb_birefnet.config(state=tk.NORMAL)
        self.rb_u2net.config(state=tk.NORMAL)
        self.counter_label.config(text="Ready")
        self.time_label.config(text="")

        # Get model name for display
        model_name_display = "BiRefNet" if self.model_name == "birefnet" else "U2Net"
        self.update_status(f"Process completed with {model_name_display} model.")


if __name__ == "__main__":
    # Check and install required dependencies before launching the app
    import sys
    import subprocess
    import importlib.util
    import tkinter as tk
    from tkinter import messagebox


    def check_and_install_dependencies():
        required_packages = ["torch", "numpy", "rembg", "onnxruntime", "Pillow"]
        missing_packages = []

        # Check which packages are missing
        for package in required_packages:
            if importlib.util.find_spec(package) is None:
                # Special case for Pillow which is imported as PIL
                if package == "Pillow" and importlib.util.find_spec("PIL") is not None:
                    continue
                missing_packages.append(package)

        # If packages are missing, install them
        if missing_packages:
            print(f"Installing missing dependencies: {', '.join(missing_packages)}")
            try:
                # Create a simple splash window to show installation progress
                splash = tk.Tk()
                splash.title("Installing Dependencies")
                splash.geometry("400x150")
                splash.resizable(False, False)

                # Center the window
                splash.update_idletasks()
                width = splash.winfo_width()
                height = splash.winfo_height()
                x = (splash.winfo_screenwidth() // 2) - (width // 2)
                y = (splash.winfo_screenheight() // 2) - (height // 2)
                splash.geometry(f'{width}x{height}+{x}+{y}')

                label = tk.Label(splash,
                                 text=f"Installing required dependencies...\n{', '.join(missing_packages)}\n\nPlease wait, this might take a few minutes.",
                                 pady=20, padx=20)
                label.pack()

                progress = tk.Label(splash, text="")
                progress.pack()

                splash.update()

                # Install each missing package
                for i, package in enumerate(missing_packages):
                    progress.config(text=f"Installing {package}... ({i + 1}/{len(missing_packages)})")
                    splash.update()
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

                # Close splash window after installation
                splash.destroy()
                return True

            except Exception as e:
                messagebox.showerror("Installation Error",
                                     f"Failed to install dependencies: {str(e)}\n\n"
                                     f"Please manually install the following packages:\n"
                                     f"{', '.join(missing_packages)}\n\n"
                                     f"Run these commands in your terminal:\n"
                                     f"pip install {' '.join(missing_packages)}")
                return False

        return True


    # Run dependency check and installation
    if check_and_install_dependencies():
        # Create the main window
        root = tk.Tk()
        app = BackgroundRemoverApp(root)

        # Center window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        # Start the main loop
        root.mainloop()