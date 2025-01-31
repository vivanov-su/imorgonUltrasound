import tkinter as tk
from tkinter import filedialog, messagebox
import os
from executable import process_ultrasound_scans, load_yaml_config  # Import from main.py

def on_run_ocr():
    """
    Event handler tied to the "Run OCR" button. Collects input/output paths and triggers processing.
    """
    input_dir = input_dir_entry.get()
    output_dir = output_dir_entry.get()

    # Validate input/output directories
    if not os.path.isdir(input_dir):
        messagebox.showerror("Input Error", "The input directory does not exist.")
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Load required configuration files
        valid_annotation_keywords = load_yaml_config("valid_annotation_keywords.yaml")
        vendor_inclusion_zones = load_yaml_config("vendor_inclusion_zones.yaml")
        ocr_settings = load_yaml_config("ocr_settings.yaml")

        # Abort if any of the configuration files fail to load
        if not all([valid_annotation_keywords, vendor_inclusion_zones, ocr_settings]):
            return

        # Process the ultrasound scan images
        process_ultrasound_scans(input_dir, output_dir, valid_annotation_keywords, vendor_inclusion_zones, ocr_settings)
        messagebox.showinfo("Success", "OCR processing completed successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during processing:\n{e}")

# GUI Application Code
app = tk.Tk()
app.title("Ultrasound OCR Processor")

# Configure input directory
tk.Label(app, text="Input Directory:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
input_dir_entry = tk.Entry(app, width=50)
input_dir_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(app, text="Browse", 
          command=lambda: input_dir_entry.insert(0, filedialog.askdirectory())).grid(row=0, column=2, padx=10, pady=5)

# Configure output directory
tk.Label(app, text="Output Directory:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_dir_entry = tk.Entry(app, width=50)
output_dir_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(app, text="Browse", 
          command=lambda: output_dir_entry.insert(0, filedialog.askdirectory())).grid(row=1, column=2, padx=10, pady=5)

# Run OCR button
run_button = tk.Button(app, text="Run OCR", command=on_run_ocr, bg="green", fg="white")
run_button.grid(row=2, column=1, pady=20)

# Start the GUI loop
app.mainloop()
