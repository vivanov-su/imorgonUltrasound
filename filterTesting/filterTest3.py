import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import yaml
from PIL import Image, ImageTk

# Initialize root Tk instance
root = tk.Tk()
root.title("Image Gallery")
root.geometry("640x480")


class ImageGallery:
    def __init__(self, master, yaml_file):
        self.master = master
        self.result = {}  # Dictionary mapping image filenames to keywords
        self.load_yaml(yaml_file)
        self.imgFolder = ""
        self.image_files = []

        # Extract and sort keywords
        kws = []
        for keywords in self.result.values():
            kws.extend(keywords)
        self.full_keyword_list = sorted(set(kws))

    def load_yaml(self, yaml_file):
        """Loads keywords from a YAML file."""
        with open(yaml_file, 'r') as f:
            self.result = yaml.safe_load(f)

    def open_directory(self):
        """Asks the user to select an image directory and displays images in a grid."""
        self.imgFolder = filedialog.askdirectory(title="Select a Folder Containing Images")
        if not self.imgFolder:
            return

        self.image_files = [os.path.join(self.imgFolder, f) for f in os.listdir(self.imgFolder)
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff'))]
        if not self.image_files:
            messagebox.showinfo("No Images", "No image files found in the selected folder.")
            return

        self.display_grid(self.image_files, title="Gallery")

    def display_grid(self, image_list, title="Gallery"):
        """Displays images in a grid with keyword search and an 'Add' button."""
        self.grid_window = tk.Toplevel(self.master)
        self.grid_window.title(title)
        self.grid_window.geometry("600x480")

        # Top frame for search and filter
        top_frame = tk.Frame(self.grid_window)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.keyword_var = tk.StringVar()
        self.combobox = ttk.Combobox(top_frame, textvariable=self.keyword_var, values=self.full_keyword_list)
        self.combobox.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.combobox.bind('<KeyRelease>', self.update_combobox_values)
        self.combobox.bind('<Return>', lambda event: self.add_new_keyword(self.keyword_var.get()))  # Enter key adds keyword

        # "Add to List" button (Initially Hidden)
        self.add_button = tk.Button(top_frame, text="Add to List", command=lambda: self.add_new_keyword(self.keyword_var.get()))
        self.add_button.pack_forget()

        # Filter button
        filter_button = tk.Button(top_frame, text="Filter", command=self.apply_filter)
        filter_button.pack(side=tk.LEFT, padx=5)

        # Exit button
        exit_button = tk.Button(top_frame, text="Exit", command=self.grid_window.destroy)
        exit_button.pack(side=tk.LEFT, padx=5)

        # Scrollable frame for images
        grid_frame = tk.Frame(self.grid_window)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(grid_frame)
        scrollbar = tk.Scrollbar(grid_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.content_frame = tk.Frame(canvas)
        self.content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        # Load images into the grid
        self.photo_images = []
        row, col = 0, 0
        max_cols = 3
        for file in image_list:
            try:
                img = Image.open(file)
                img = img.resize((100, 100))
                photo = ImageTk.PhotoImage(img)
                self.photo_images.append(photo)

                btn = tk.Button(self.content_frame, image=photo,
                                command=lambda f=file: self.display_single_view(f, image_list))
                btn.grid(row=row, column=col, padx=5, pady=5)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            except Exception as e:
                print(f"Error loading image {file}: {e}")

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

    def update_combobox_values(self, event):
        """Filters dropdown and shows 'Add' button if the keyword is missing."""
        typed = self.keyword_var.get().strip().lower()

        if typed == "":
            filtered_data = self.full_keyword_list  # Show full list when empty
            self.add_button.pack_forget()  # Hide "Add" button when not needed
        else:
            filtered_data = [kw for kw in self.full_keyword_list if typed in kw.lower()]

            if typed not in (kw.lower() for kw in self.full_keyword_list):  # If the word is missing
                self.add_button.config(text=f'Add "{typed}" to List', command=lambda: self.add_new_keyword(typed))
                self.add_button.pack(side=tk.LEFT, padx=5)  # Show the "Add" button
            else:
                self.add_button.pack_forget()  # Hide the "Add" button if the word exists

        self.combobox['values'] = sorted(filtered_data)  # Update dropdown list

    def add_new_keyword(self, new_keyword):
        """Adds the new keyword to the list and updates the dropdown."""
        if new_keyword and new_keyword not in self.full_keyword_list:
            self.full_keyword_list.append(new_keyword)
            self.full_keyword_list.sort()  # Keep list alphabetized
            self.combobox['values'] = self.full_keyword_list  # Update dropdown
            messagebox.showinfo("Keyword Added", f'"{new_keyword}" has been added!')
            self.add_button.pack_forget()  # Hide the "Add" button after adding

    def apply_filter(self):
        """Filters images by keyword."""
        filter_word = self.keyword_var.get().strip()
        if not filter_word:
            return

        self.filtered_images = [file for file in self.image_files if filter_word in self.result.get(os.path.basename(file), [])]
        if self.filtered_images:
            self.display_grid(self.filtered_images, title=f"Filtered: {filter_word}")
        else:
            messagebox.showinfo("No Results", f"No images found for keyword: {filter_word}")

    def display_single_view(self, selected_file, image_list):
        """Opens a single image with next/previous navigation."""
        self.current_list = image_list
        self.current_index = image_list.index(selected_file)

        self.single_view_window = tk.Toplevel(self.master)
        self.single_view_window.title("Image Viewer")
        self.single_view_window.geometry("600x480")

        self.single_canvas = tk.Canvas(self.single_view_window)
        self.single_canvas.pack(expand=True, fill=tk.BOTH)

        self.show_image()

        btn_frame = tk.Frame(self.single_view_window)
        btn_frame.pack(side=tk.BOTTOM, pady=5)
        prev_btn = tk.Button(btn_frame, text="Previous", command=self.show_previous)
        prev_btn.pack(side=tk.LEFT, padx=5)
        next_btn = tk.Button(btn_frame, text="Next", command=self.show_next)
        next_btn.pack(side=tk.LEFT, padx=5)
        exit_btn = tk.Button(btn_frame, text="Exit", command=self.single_view_window.destroy)
        exit_btn.pack(side=tk.LEFT, padx=5)

    def show_image(self):
        """Displays the current image."""
        file = self.current_list[self.current_index]
        img = Image.open(file)
        img.thumbnail((500, 400))
        self.single_photo = ImageTk.PhotoImage(img)
        self.single_canvas.delete("all")
        self.single_canvas.create_image(300, 240, image=self.single_photo)

# UI Elements
def select_yaml():
    file_path = filedialog.askopenfilename(initialdir=".", filetypes=[("YAML files", "*.yaml")])
    if file_path:
        gallery = ImageGallery(root, file_path)
        gallery.open_directory()

tk.Button(root, text="Select .yaml File", command=select_yaml).pack()
root.mainloop()
