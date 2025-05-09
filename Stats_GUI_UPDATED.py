from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.messagebox
from PIL import ImageTk, Image
from tkinter import filedialog, Tk, Label, Frame
import os
import yaml
import cv2
import numpy as np
from executable import process_ultrasound_scans, load_yaml_config  # Importing the required functions
from test import compute_metrics
import time

#   --------------------CLASS DEFINITIONS--------------------

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


#   --------------------CLASS ENDS---------------------

#   --------------------MISCELLANEOUS DEFINITIONS--------------------

def optionCommand(event):
    if(optionDrop.get() == "Statistics View" or "Comparison View"):
        yamlSelect.grid(column = 1)
    else:
        yamlSelect.grid_remove()
        y.grid_remove()
        yamlFile.grid_remove()

def openDirectory():
    folder_selection = filedialog.askdirectory(initialdir="C:/Users/gugul/Documents/School/Capstone/imgFolder")
    folderPath.set(folder_selection)

def browse(pathVar):
    folder_selection = filedialog.askdirectory(initialdir="C:/Users/gugul/Documents/School/Capstone/imgFolder")
    pathVar.set(folder_selection)

#   ----------------------DISPLAY DEFINTIONS-------------------

def openAnalysisWindow():
    ### Added test.py code (START) 
    folder_path = filedialog.askdirectory(title="Select a Folder Containing Images")
    imgFolderName = os.path.basename(folder_path)

    valid_annotation_keywords = load_yaml_config("valid_annotation_keywords.yaml")
    vendor_inclusion_zones = load_yaml_config("vendor_inclusion_zones.yaml")
    ocr_settings = load_yaml_config("ocr_settings.yaml")

    true_results_yaml_path = os.path.join(folder_path, "RapidOCR_results.yaml")
    true_results = load_yaml_config(true_results_yaml_path)

    performance_metrics = {}
    try:
        if f"{imgFolderName}_results.yaml" not in os.listdir("C:/Users/gugul/Documents/School/Capstone/export"): ### change hard coded export directory
            for model in models:
                print(f"Running OCR with model: {model}")

                ocr_settings["ocr_engine"] = model

                start_time = time.time()
                ocr_results = process_ultrasound_scans(
                    input_directory_str=folder_path,
                    valid_annotation_keywords_dict=valid_annotation_keywords,
                    vendor_specific_zones_dict=vendor_inclusion_zones,
                    ocr_settings_dict=ocr_settings,
                )
                end_time = time.time() 

                time_taken = end_time - start_time
                num_images = len(true_results)

                performance_metrics[model] = compute_metrics(ocr_results, true_results, time_taken, num_images)

            output_file_path = os.path.join(
                "C:/Users/gugul/Documents/School/Capstone/export", f"{imgFolderName}_results.yaml"  ### change hard coded export directory
            )
            with open(output_file_path, "w") as output_file:
                yaml.dump(performance_metrics, output_file, default_flow_style=False)   

    except Exception as e:
        print(f"Error during OCR processing: {e}")
    ### Added test.py code (END)

    if not folder_path:
        return

    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff'))]
    
    if not image_files:
        return
    
    ### Changed labels (START)
    multi_analysis_window = Toplevel(root)
    multi_analysis_window.title("Analyze Images")
    # multi_analysis_window.geometry("800x800")

    img_label = Label(multi_analysis_window)
    img_label.pack(fill="both", expand=True)

    analysis_label = Label(multi_analysis_window, text="", anchor="center", pady=20)
    analysis_label.pack()
    
    labels_frame = Frame(multi_analysis_window)
    labels_frame.pack()

    model_labels = {}  

    for idx, model in enumerate(models):
        model_labels[model] = Label(labels_frame, text=f"{model}: Processing...", padx=10, pady=10, wraplength=800, anchor="center")
        model_labels[model].grid(row=0, column=idx, padx=10)
        labels_frame.grid_columnconfigure(idx, weight=1)

    button_frame = Frame(multi_analysis_window, padx=10, pady=10)
    button_frame.pack()
    ### Changed labels (END)

    current_index = [0]

    def get_image_size(image_path):
        try:
            with Image.open(image_path) as img:
                return img.size  
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None

    def update_image():
        try:
            folder_name = os.path.basename(folder_path)

            yaml_file_path = os.path.join(os.getcwd(), "vendor_inclusion_zones.yaml")

            if os.path.exists(yaml_file_path):
                with open(yaml_file_path, 'r') as yaml_file:
                    yaml_data = yaml.safe_load(yaml_file)

                matched_brand = None
                for brand in yaml_data:
                    if brand == folder_name:  
                        matched_brand = brand
                        break

                if matched_brand:
                    img = Image.open(image_files[current_index[0]])
                    img_cv = np.array(img)  
                    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR) 

                    original_size = get_image_size(image_files[current_index[0]])
                    if original_size:
                        width, height = original_size

                    for brand_info in yaml_data[matched_brand]:
                        image_size = brand_info['image_size']
                        if image_size == [width, height]: 
                            boxes = brand_info['boxes']  
                            for box in boxes:
                                x_min, y_min, x_max, y_max = box
                                cv2.rectangle(img_cv, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)  

                            img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
                            img_pil = img_pil.resize((400, 400)) 
                            photo = ImageTk.PhotoImage(img_pil)
                            img_label.config(image=photo)
                            img_label.image = photo

                            filename = os.path.basename(image_files[current_index[0]])

                            ### Display Stats on GUI Window (START)
                            yaml_path = f"C:/Users/gugul/Documents/School/Capstone/imgFolder/imgFolder/{imgFolderName}/RapidOCR_results.yaml" ### change hard coded import directory
                            with open(yaml_path, "r") as file:
                                true_results = yaml.safe_load(file) 

                            exact_keywords = true_results.get(filename, [])
                            analysis_output = f"Image {current_index[0] + 1} of {len(image_files)}\tFile Name: {filename}\t{(exact_keywords).join(', ') if exact_keywords else 'None'}"
                            analysis_label.config(text=analysis_output)

                            imgFolder_result_path = os.path.join(os.getcwd(), f"Export/{imgFolderName}_results.yaml")
                            with open(imgFolder_result_path, 'r') as img_results:
                                img_data = yaml.safe_load(img_results)

                            for model in models:
                                if model in img_data:
                                    output_text = f"{model}\n"
                                    if "images" in img_data[model] and filename in img_data[model]["images"]:
                                        keywords = img_data[model]["images"][filename].get("keywords", [])
                                        keywords_str = ", ".join(keywords) if keywords else []
                                        output_text += f"Extracted Keywords: {keywords_str}\n"
                                    avg_time = img_data[model]["average_time_per_image"]
                                    avg_false_pos = round(img_data[model]["avg_false_positives_count"], 3)
                                    avg_pos_percent = img_data[model]["avg_true_positives_percent"]
                                    output_text += f"Avg Time: {avg_time}\nAvg False Positive: {avg_false_pos}\nAvg Positive %: {avg_pos_percent}\n"
                                    
                                    model_labels[model].config(text=output_text)
        except Exception as e:
            for model in models:
                model_labels[model].config(text=f"Error loading image: {e}")
        ### Display Stats on GUI Window (END)

    def next_image():
        if current_index[0] < len(image_files) - 1:
            current_index[0] += 1
            update_image()

    def prev_image():
        if current_index[0] > 0:
            current_index[0] -= 1
            update_image()

    prev_button = Button(button_frame, text="Previous Image", command=prev_image)
    prev_button.pack(side=LEFT, padx=10)

    next_button = Button(button_frame, text="Next Image", command=next_image)
    next_button.pack(side=RIGHT, padx=10)

    update_image()

def openGridView():
    folder_path = filedialog.askdirectory(title="Select a Folder Containing Images")
    
    if not folder_path:
        return

    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff'))]
    
    if not image_files:
        return

    grid_window = Toplevel(root)
    grid_window.title("Image Grid View")
    grid_window.geometry("800x600")

    frame = Frame(grid_window)
    frame.pack(fill=BOTH, expand=True)

    row, col = 0, 0
    max_cols = 4  

    def openSingleImage(index):
        nonlocal image_files
        current_index = [index]  

        single_view_window = Toplevel(root)
        single_view_window.title("Single Image View")
        single_view_window.geometry("500x600")

        img_label = Label(single_view_window)
        img_label.pack()

        text_label = Label(single_view_window, text="", justify=LEFT, padx=10, pady=10, wraplength=400)
        text_label.pack()

        button_frame = Frame(single_view_window)
        button_frame.pack()

        def get_image_size(image_path):
            try:
                with Image.open(image_path) as img:
                    return img.size  
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                return None

        def update_image():
            try:
                folder_name = os.path.basename(folder_path)

                yaml_file_path = os.path.join(os.getcwd(), "vendor_inclusion_zones.yaml")

                if os.path.exists(yaml_file_path):
                    with open(yaml_file_path, 'r') as yaml_file:
                        yaml_data = yaml.safe_load(yaml_file)

                    matched_brand = None
                    for brand in yaml_data:
                        if brand == folder_name:  
                            matched_brand = brand
                            break

                    if matched_brand:
                        img = Image.open(image_files[current_index[0]])
                        img_cv = np.array(img)  
                        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR) 

                        original_size = get_image_size(image_files[current_index[0]])
                        if original_size:
                            width, height = original_size
                            print(f"Original image size: {width}x{height}")

                        for brand_info in yaml_data[matched_brand]:
                            image_size = brand_info['image_size']
                            if image_size == [width, height]: 
                                boxes = brand_info['boxes']  
                                for box in boxes:
                                    x_min, y_min, x_max, y_max = box
                                    cv2.rectangle(img_cv, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)  

                                img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
                                img_pil = img_pil.resize((400, 400)) 
                                photo = ImageTk.PhotoImage(img_pil)
                                img_label.config(image=photo)
                                img_label.image = photo

                                analysis_output = f"Image {current_index[0] + 1} of {len(image_files)}\nFile Path: {image_files[current_index[0]]}\nFurther analysis results would be displayed here."
                                text_label.config(text=analysis_output)
                                return

                        text_label.config(text="No matching size found for this image.")
                    else:
                        text_label.config(text=f"No coordinates found for brand: {folder_name}")
                else:
                    text_label.config(text="YAML file not found.")
            except Exception as e:
                text_label.config(text=f"Error loading image: {e}")

        def next_image():
            if current_index[0] < len(image_files) - 1:
                current_index[0] += 1
                update_image()

        def prev_image():
            if current_index[0] > 0:
                current_index[0] -= 1
                update_image()

        prev_button = Button(button_frame, text="Previous Image", command=prev_image)
        prev_button.pack(side=LEFT, padx=10)

        next_button = Button(button_frame, text="Next Image", command=next_image)
        next_button.pack(side=RIGHT, padx=10)

        update_image()

    for idx, file in enumerate(image_files):
        try:
            img = Image.open(file)
            img = img.resize((100, 100))  
            photo = ImageTk.PhotoImage(img)

            btn = Button(frame, image=photo, command=lambda i=idx: openSingleImage(i))
            btn.image = photo  
            btn.grid(row=row, column=col, padx=5, pady=5)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        except Exception as e:
            print(f"Error loading image {file}: {e}")

def analyze_images(*args):
    """Runs the correct function when dropdown selection changes."""
    selected_mode = optionDrop.get()
    #selected_mode = var.get()
    if selected_mode == "Single View":
        openAnalysisWindow()
    elif selected_mode == "Multiple Image View":
        openGridView()

def extract():
    # Collect input/output folder paths
    input_dir = pathVar.get()
    output_dir = pathVar2.get()

    if (output_dir == "" or output_dir == ""):
        tkinter.messagebox.showinfo("Error", "Please select an import/export directory.")
        return
    
    print("Import Directory: " + input_dir)
    print("Export Directory: " + output_dir)

    # Collect OCR settings from GUI options
    ocr_settings = {
        "ocr_engine": modelDrop.get(),
        "require_valid_keyword": False, # TODO: add buttons for these
        "use_inclusion_zones": False,
    }

    try:
        # Load required configuration files
        valid_annotation_keywords = load_yaml_config("valid_annotation_keywords.yaml")
        vendor_inclusion_zones = load_yaml_config("vendor_inclusion_zones.yaml")


        # Process the ultrasound scan images
        ocr_results = process_ultrasound_scans(
            input_directory_str=input_dir,
            valid_annotation_keywords_dict=valid_annotation_keywords,
            vendor_specific_zones_dict=vendor_inclusion_zones,
            ocr_settings_dict=ocr_settings,
        )

        print("OCR processing completed successfully!")

        # Save output to file
        output_file_path = os.path.join(output_dir, modelDrop.get() + "_results.yaml")
        with open(output_file_path, "w") as output_file:
            yaml.dump(ocr_results, output_file, default_flow_style=False)
            print(f"### OCR results written to {output_file_path}")

    except Exception as e:
        tkinter.messagebox.showerror("Error", f"An error occurred during processing:\n{e}")

def select_yaml():
    file_path = filedialog.askopenfilename(initialdir=".", filetypes=[("YAML files", "*.yaml")])
    if file_path:
        gallery = ImageGallery(root, file_path)
        gallery.open_directory()

#   ---------------------GUI CODE--------------------

root = Tk()
root.title("iMorgon Annotation Extraction")
root.geometry("640x600")

imageDesc_Frame = Frame(root, pady = 5)
dropDown_Frame = Frame(root, pady = 5)
impExp_Frame = Frame(root, pady = 5)
button_Frame = Frame(root, pady = 5)
option_Frame = Frame(root, pady = 5)
option_Dropdown = Frame(root, pady = 5)

root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

imageDesc_Frame.grid(row = 0, column = 1, sticky=NSEW)
dropDown_Frame.grid(row = 1, column = 1, sticky = NSEW)
impExp_Frame.grid(row = 2, column = 1)
option_Dropdown.grid(row = 3, column = 1)
button_Frame.grid(row = 4, column = 1, sticky=NSEW)

#IMAGE AND DESCRIPTION WIDGET
imageDesc_Frame.columnconfigure(0, weight=1)
imageDesc_Frame.columnconfigure(1, weight=1)
imageDesc_Frame.columnconfigure(2, weight=1)
logo = ImageTk.PhotoImage(Image.open("misc/logo.png"))
logo_label = Label(imageDesc_Frame, image=logo)
logo_label.grid(row = 0, column = 1, pady = (10, 5))
description = Label(imageDesc_Frame, text="Ultrasound Annotation Extraction Program")
description.grid(row = 1, column= 1)

#DROPDOWN
dropDown_Frame.columnconfigure(0, weight=1)
dropDown_Frame.columnconfigure(1, weight=1)
dropDown_Frame.columnconfigure(2, weight=1)
modelFrame = LabelFrame(dropDown_Frame,text="Models")
modelFrame.grid(row = 0, column = 1)
models = ["RapidOCR"]
#models = ["EasyOCR", "RapidOCR", "PaddleOCR", "DocTR", "Tesseract"]
modelDrop = ttk.Combobox(modelFrame, value=models)
modelDrop.current(0)
modelDrop.grid(row=0, pady = 5)

#IMPORT AND EXPORT BUTTON WDIGET
impExp_Frame.columnconfigure(0, weight=1)
impExp_Frame.columnconfigure(1, weight=1)
impExp_Frame.columnconfigure(2, weight=1)
impExp_Frame.columnconfigure(3, weight=1)
import_labelFrame = tk.LabelFrame(impExp_Frame, text = "Import Directory")
pathVar = tk.StringVar(import_labelFrame, "")
import_labelFrame.grid(row = 0, column = 0, padx = 10, pady = 5)
chosenDirectory = tk.Entry(import_labelFrame, textvariable=pathVar)
chosenDirectory.grid(row = 1, column = 0, pady = 5)
button_openFile = Button(import_labelFrame, text = "...", command = lambda: browse(pathVar))
button_openFile.grid(row = 1, column = 1, pady = 5)

folderPath = StringVar()

export_labelFrame = tk.LabelFrame(impExp_Frame, text = "Export Directory")
pathVar2 = tk.StringVar(export_labelFrame, "")
export_labelFrame.grid(row = 0, column = 1, padx = 10, pady = 5)
choseDirectory = tk.Entry(export_labelFrame, textvariable=pathVar2)
choseDirectory.grid(row = 1, column = 1, pady = 5)
button_openExp = Button(export_labelFrame, text = "...", command = lambda:browse(pathVar2))
button_openExp.grid(row = 1, column = 2, pady = 5)

button_extract = Button(impExp_Frame, text="Extract", command=extract)
button_extract.grid(row = 0, column = 3, pady=5)

#SELECTION OPTION DROPDOWN
option_Dropdown.columnconfigure(0, weight = 1)
option_Dropdown.columnconfigure(1, weight = 1)
option_Dropdown.columnconfigure(2, weight = 1)

imgSelect = tk.LabelFrame(option_Dropdown, text = "Select Image Folder")
imgSelVar = tk.StringVar(imgSelect, "")
imgSelect.grid(row = 1, column = 1, pady = 5)
button_viewImages = Button(option_Dropdown, text = "View Images", command = select_yaml)    #change this command yo
button_viewImages.grid(row = 1, column = 1, pady = 5)


yamlSelect = tk.LabelFrame(option_Dropdown, text = "Select .yaml file")
yamlVar = tk.StringVar(yamlSelect, "")
yamlSelect.grid(row = 2, column = 1, pady = 5)
button_analyze = Button(option_Dropdown, text="Analyze Images", command = analyze_images)
button_analyze.grid(row = 3, column = 1, pady=5)

#BUTTON FRAME
button_Frame.columnconfigure(0, weight=1)
button_Frame.columnconfigure(1, weight=1)
button_Frame.columnconfigure(2, weight=1)
button_close = Button(button_Frame, text="Close", command=root.quit)
button_close.grid(row = 0, column = 1, pady = 5)

root.mainloop()
