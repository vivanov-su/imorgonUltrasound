import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from functools import partial
from PIL import Image, ImageTk
import os
from executable import process_ultrasound_scans, load_yaml_config  # Importing the required functions

class MedicalAnnotationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Annotation Extraction")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)

        self.setup_main_screen()

    def setup_main_screen(self):
        ### Logo ###
        logo = tk.PhotoImage(file="./misc/logo.png")  # Load logo image
        logo_label = tk.Label(self.root, image=logo)
        logo_label.image = logo  # Keep reference to avoid garbage collection
        logo_label.pack(pady=10)

        ### Title Text ###
        title_label = tk.Label(
            self.root,
            text="iMorgon Medical Annotation Extraction Interface",
            font=("Arial", 14),
        )
        title_label.pack()

        ### Central Config Region ###
        control_panel_frame = tk.Frame(self.root)
        control_panel_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        ### Folder Selection Panel ###
        folder_frame = tk.LabelFrame(control_panel_frame, text="Folder Selection", padx=10, pady=10)
        folder_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.add_folder_selection_options(folder_frame)

        ### OCR Options Panel ###
        ocr_frame = tk.LabelFrame(control_panel_frame, text="OCR Options", padx=10, pady=10)
        ocr_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.add_ocr_options(ocr_frame)

        ### Buttons ###
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        close_button = tk.Button(button_frame, text="Close", fg="white", bg="red", command=self.root.quit)
        close_button.pack(side=tk.LEFT, padx=10)

        run_button = tk.Button(button_frame, text="Run", fg="white", bg="green", command=self.run_process)
        run_button.pack(side=tk.RIGHT, padx=10)

    def add_folder_selection_options(self, parent):
        # Add folder selection inputs
        self.folder_vars = {}

        folders = ["Ultrasound image files", "Program output location", "Expected human results"]
        for folder in folders:
            label = tk.Label(parent, text=folder)
            label.pack(anchor=tk.W, pady=(5, 0))

            entry_frame = tk.Frame(parent)  # Horizontal frame for Entry and Browse button
            entry_frame.pack(anchor=tk.W, pady=(0, 5), fill=tk.X)

            entry = tk.Entry(entry_frame, width=35)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            browse_button = tk.Button(entry_frame, text="Browse", command=lambda e=entry: self.browse_folder(e))
            browse_button.pack(side=tk.LEFT, padx=5)

            self.folder_vars[folder] = entry

    def add_ocr_options(self, parent):
        # OCR Engine Dropdown Menu
        ocr_label = tk.Label(parent, text="OCR Engine")
        ocr_label.pack(anchor=tk.W)

        self.ocr_engine = ttk.Combobox(parent, values=["RapidOCR", "PaddleOCR"])
        self.ocr_engine.set("RapidOCR")  # Set a default value
        self.ocr_engine.pack(anchor=tk.W, pady=(0, 10))

        # Require Valid Keywords Checkbox
        self.require_keywords = tk.BooleanVar(value=True)
        keywords_check = tk.Checkbutton(
            parent, text="Require valid keywords", variable=self.require_keywords
        )
        keywords_check.pack(anchor=tk.W)

        # Use Inclusion Zones Checkbox
        self.use_zones = tk.BooleanVar(value=True)
        inclusion_zones_check = tk.Checkbutton(
            parent, text="Use inclusion zones", variable=self.use_zones
        )
        inclusion_zones_check.pack(anchor=tk.W)

    def browse_folder(self, entry):
        # Open a folder selection dialog and set the chosen folder path to the entry box
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            entry.delete(0, tk.END)
            entry.insert(0, folder_selected)

    def run_process(self):
        # Collect input/output folder paths
        input_dir = self.folder_vars["Ultrasound image files"].get()
        output_dir = self.folder_vars["Program output location"].get()

        if not input_dir or not output_dir:
            messagebox.showerror("Error", "Please specify both the input and output folders.")
            return

        # Collect OCR settings from GUI options
        ocr_settings = {
            "ocr_engine": self.ocr_engine.get(),
            "require_valid_keyword": self.require_keywords.get(),
            "use_inclusion_zones": self.use_zones.get(),
        }

        try:
            # Load required configuration files
            valid_annotation_keywords = load_yaml_config("valid_annotation_keywords.yaml")
            vendor_inclusion_zones = load_yaml_config("vendor_inclusion_zones.yaml")

            # Process the ultrasound scan images
            image_results = process_ultrasound_scans(
                input_directory_str=input_dir,
                output_directory_str=output_dir,
                valid_annotation_keywords_dict=valid_annotation_keywords,
                vendor_specific_zones_dict=vendor_inclusion_zones,
                ocr_settings_dict=ocr_settings,
            )

            print("OCR processing completed successfully!")

            # Call the outcome window and display results
            outcome_window = RunOutcomeWindow(self.root, self.ocr_engine.get(), image_results, input_dir)
            outcome_window.display_run_results()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing:\n{e}")

class RunOutcomeWindow:
    def __init__(self, parent, engine, image_results, input_dir):
        self.top_level = tk.Toplevel(parent)
        self.top_level.title(f"{engine} Results")
        self.top_level.geometry("800x1000")
        self.top_level.resizable(True, True)
        self.image_results = image_results  # Pass in the results for display
        self.input_dir = input_dir  # Base directory to locate images

    def display_run_results(self):
        # Clear the top-level window (to remove any leftover widgets from previous views)
        self.clear_window()

        # Save references to result_frame and stats_frame
        self.result_frame = tk.Frame(self.top_level)
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add a scrollable frame
        canvas = tk.Canvas(self.result_frame)
        scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Enable mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda event: self._on_mouse_wheel(canvas, event))

        # Display image results
        for filename, extracted_text in self.image_results.items():  # Results are now in key-value pairs
            image_path = os.path.join(self.input_dir, filename)  # Full path to the image
            self.add_image_result(scrollable_frame, filename, extracted_text, image_path)

        # Overall Statistics Panel
        self.stats_frame = tk.LabelFrame(self.top_level, text="Overall Statistics", padx=10, pady=10)
        self.stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Example overall stats (you would replace this with actual calculations)
        total_images_label = tk.Label(self.stats_frame, text=f"Total Images: {len(self.image_results)}")
        total_images_label.pack(anchor=tk.W)

        # Placeholder statistic. Replace with actual overall accuracy if available.
        accuracy_label = tk.Label(self.stats_frame, text="Overall Accuracy: Coming Soon Next Update")
        accuracy_label.pack(anchor=tk.W)

    def _on_mouse_wheel(self, canvas, event):
        """Handle mouse wheel scrolling."""
        canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    def add_image_result(self, parent, image_title, extracted_text, image_path):
        try:
            # Create a medium-sized thumbnail
            pil_image = Image.open(image_path)
            pil_image.thumbnail((150, 150))  # Resize to thumbnail
            thumbnail = ImageTk.PhotoImage(pil_image)
        except Exception as e:
            thumbnail = None  # If image loading fails, we still proceed

        # Frame for each image result
        result_frame = tk.Frame(parent, relief=tk.RAISED, borderwidth=1, padx=5, pady=5, bg="#f0f0f0")
        result_frame.pack(fill=tk.X, pady=5)

        # Thumbnail on the left
        if thumbnail:
            thumbnail_label = tk.Label(result_frame, image=thumbnail, bg="#f0f0f0")
            thumbnail_label.image = thumbnail  # Keep a reference to the image to avoid garbage collection
            thumbnail_label.pack(side=tk.LEFT, padx=5)

        # Information on the right
        info_frame = tk.Frame(result_frame, bg="#f0f0f0")
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        title_label = tk.Label(info_frame, text=image_title, font=("Arial", 10, "bold"), bg="#f0f0f0")
        title_label.pack(anchor=tk.W)

        snippet_label = tk.Label(info_frame, text= "Accuracy: X%", bg="#f0f0f0")
        snippet_label.pack(anchor=tk.W)  # Show the first few lines of extracted text as a preview

        # Bind a click event to open the enlarged view
        result_frame.bind("<Button-1>", partial(self.show_enlarged_view, image_title, extracted_text, image_path))

        # Bind all child widgets within the frame to the same click event
        for widget in [thumbnail_label, info_frame, title_label, snippet_label]:
            widget.bind("<Button-1>", partial(self.show_enlarged_view, image_title, extracted_text, image_path))

    def show_enlarged_view(self, image_title, extracted_text, image_path, event=None):
        # Clear the current view
        self.clear_window()

        # Display the image title (filename)
        title_label = tk.Label(self.top_level, text=f"File: {image_title}", font=("Arial", 12, "bold"), fg="blue")
        title_label.pack(anchor=tk.N, padx=20, pady=(10, 5))  # Add some padding for spacing

        # Enlarged image view
        try:
            pil_image = Image.open(image_path)
            pil_image = pil_image.resize((600, 600))  # Resize to larger dimensions
            enlarged_image = ImageTk.PhotoImage(pil_image)
            image_label = tk.Label(self.top_level, image=enlarged_image)
            image_label.image = enlarged_image  # Keep a reference to the image to avoid garbage collection
            image_label.pack(pady=10)
        except Exception as e:
            # If image can't be loaded, display a placeholder text
            image_label = tk.Label(self.top_level, text=f"[Unable to load image]{e}", font=("Arial", 14), fg="red")
            image_label.pack(pady=10)

        # Extracted text view
        text_label = tk.Label(self.top_level, text="Extracted Text:", font=("Arial", 12, "bold"))
        text_label.pack(anchor=tk.CENTER, padx=20)
        text_box = tk.Text(self.top_level, wrap=tk.WORD, height=15, width=80)
        text_box.insert(tk.END, "\n".join(extracted_text))  # Display the full list of extracted text
        text_box.config(state=tk.DISABLED)  # Make the text box read-only
        text_box.pack(padx=20, pady=10)

        # Back button to regenerate the original view
        back_button = tk.Button(self.top_level, text="Back", command=self.display_run_results, bg="white")
        back_button.pack(side=tk.BOTTOM, pady=5)

    def clear_window(self):
        # Helper method to clear all widgets from the top-level window
        for widget in self.top_level.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalAnnotationGUI(root)
    root.mainloop()