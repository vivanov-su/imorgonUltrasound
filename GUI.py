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

#--------------------------------------MODELS LIST--------------------------------------

models = ["RapidOCR", "EasyOCR", "DocTR", "PaddleOCR", "Tesseract"]

#--------------------------------------Primary Functions--------------------------------------

#Formatted as a grid with searchable keywords
def open_grid_view(imageFolder, exportFolder):       
    images = [os.path.join(imageFolder, f) for f in os.listdir(imageFolder) if f.lower().endswith((".jpg", ".tiff", ".png", ".jpeg"))]
    row, col = 0, 0
    max_cols = 4

    grid_window = Toplevel(root)
    grid_window.title("Image Grid View")
    grid_window.geometry("800x600")
    grid_window.resizable(True, True)
    grid_window.grid_rowconfigure(0, weight = 1)
    grid_window.grid_columnconfigure(0, weight = 1)

    gallery_frame = Frame(grid_window)
    test_text = Label(gallery_frame, text="hello")
    test_text.grid(row = 0, column = 0)

    for idx, image in enumerate(images):
        try:
            img = Image.open(image)
            img = img.resize((100, 100))
            photo = ImageTk.PhotoImage(img)

            img_button = Button(gallery_frame, image=photo, command=lambda i=idx: open_single_view(i, imageFolder, exportFolder))
            img_button.image = photo
            img_button.grid(row = row, column = col, padx = 5, pady = 5)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        except Exception as e:
            print(f"Error loading image {img}: {e}")
            
    gallery_frame.grid(row = 0, column = 0)


#Formatted as 'Andy's Favorite Image'
def open_single_view(index, imageFolder, exportFolder):     
    print("Open Andy's favorite image")

    image_files = [os.path.join(imageFolder, f) for f in os.listdir(imageFolder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff'))]
    
    if not image_files:
        return
    
    current_index = [index]  

    single_view_window = Toplevel(root)
    single_view_window.title("Single Image View")
    single_view_window.geometry("500x600")

    img_label = Label(single_view_window)
    img_label.pack(fill="both", expand=True)

    text_label = Label(single_view_window, text="", anchor="center", pady=20)
    text_label.pack()

    labels_frame = Frame(single_view_window)
    labels_frame.pack()

    model_labels = {}  

    for idx, model in enumerate(models):
        model_labels[model] = Label(labels_frame, text=f"{model}: Processing...", padx=10, pady=10, wraplength=800, anchor="center")
        model_labels[model].grid(row=0, column=idx, padx=10)
        labels_frame.grid_columnconfigure(idx, weight=1)

    button_frame = Frame(single_view_window, padx=10, pady=10)
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
            folderName = os.path.basename(imageFolder)

            yaml_file_path = os.path.join(os.getcwd(), "vendor_inclusion_zones.yaml")

            if os.path.exists(yaml_file_path):
                with open(yaml_file_path, 'r') as yaml_file:
                    yaml_data = yaml.safe_load(yaml_file)

                matched_brand = None
                for brand in yaml_data:
                    if brand == folderName:  
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

                            yaml_path = f"{imageFolder}/true_results.yaml" 
                            with open(yaml_path, "r") as file:
                                true_results = yaml.safe_load(file) 

                            exact_keywords = true_results.get(filename, [])
                            analysis_output = f"Image {current_index[0] + 1} of {len(image_files)}\tFile Name: {filename}\tExact Keywords: {', '.join(exact_keywords) if exact_keywords else 'None'}"
                            text_label.config(text=analysis_output)

                            imgFolder_result_path = os.path.join(os.getcwd(), f"{exportFolder}/{folderName}_results.yaml")
                            with open(imgFolder_result_path, 'r') as img_results:
                                img_data = yaml.safe_load(img_results)

                            for model in models:
                                if model in img_data:
                                    output_text = f"{model}\n"
                                    if "images" in img_data[model] and filename in img_data[model]["images"]:
                                        detected_keywords = img_data[model]["images"][filename].get("detected_keywords", [])
                                        avg_time = img_data[model]["average_time_per_image"]
                                        output_text += f"{detected_keywords}\n"
                                        output_text += f"Avg Time: {avg_time}"
                                    model_labels[model].config(text=output_text)

        except Exception as e:
                for model in models:
                    model_labels[model].config(text=f"Error loading image: {e}")

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

#Extracts keywords if .yaml file doesn't exist yet, then calls 'open_grid_view'
def analyze():              
    if pathVar.get() == "" or pathVarTwo.get() == "":
        tkinter.messagebox.showinfo("Error", "Please select an import/export directory.")
        return

    imageFolder = pathVar.get()
    folderName =  os.path.basename(pathVar.get())
    exportFolder = pathVarTwo.get()

    valid_annotation_keywords = load_yaml_config("valid_annotation_keywords.yaml")
    vendor_inclusion_zones = load_yaml_config("vendor_inclusion_zones.yaml")
    ocr_settings = load_yaml_config("ocr_settings.yaml")

    true_results_yaml_path = os.path.join(imageFolder, "true_results.yaml")
    true_results = load_yaml_config(true_results_yaml_path)
    
    performance_metrics = {}
    try:
        if f"{folderName}_results.yaml" not in os.listdir(exportFolder):
            for model in models:
                print(f"Running OCR with model: {model}")
                ocr_settings["ocr_engine"] = model

                start_time = time.time()
                ocr_results = process_ultrasound_scans(
                    input_directory_str=imageFolder,
                    valid_annotation_keywords_dict=valid_annotation_keywords,
                    vendor_inclusion_zones_dict=vendor_inclusion_zones,
                    ocr_settings_dict=ocr_settings,
                )
                end_time = time.time()

                time_taken = end_time - start_time
                num_images = len(true_results)

                performance_metrics[model] = compute_metrics(ocr_results, true_results, time_taken, num_images)

                output_file_path = os.path.join(exportFolder, f"{folderName}_results.yaml")
                with open(output_file_path, "w") as output_file:
                            yaml.dump(performance_metrics, output_file, default_flow_style=False)   

    except Exception as e:
        print(f"Error 1 during OCR processing: {e}")

    open_grid_view(imageFolder, exportFolder)

#--------------------------------------Misc Definitions--------------------------------------

def browse(pathVariable):
    folder_selection = filedialog.askdirectory(mustexist=True)
    pathVariable.set(folder_selection)

#--------------------------------------GUI Code--------------------------------------

root = Tk()
root.title("iMorgon Extraction")
root.geometry("640x600")

image_desc_frame = Frame(root)
image_desc_frame.grid(row = 0, column = 0)
image_desc_frame.rowconfigure(0, weight = 1)
image_desc_frame.columnconfigure(0, weight = 1)
logo = ImageTk.PhotoImage(Image.open("misc/logo.png"))
logo_label = Label(image_desc_frame, image = logo)
logo_label.grid(row = 0, column = 0, pady = 5)
description = Label(image_desc_frame, text="Ultrasound Annotation Extraction Program")
description.grid(row = 1, column = 0, pady = 5)

folderPath = StringVar()

import_export_frame = Frame(root)
import_export_frame.grid(row = 1, column = 0)
import_export_frame.rowconfigure(0, weight = 3)
import_export_frame.columnconfigure(0, weight = 1)
import_labelFrame = tk.LabelFrame(import_export_frame, text = "Import Directory")
pathVar = tk.StringVar(import_labelFrame, "")
chosenDirectory = tk.Entry(import_labelFrame, textvariable=pathVar)
button_open = Button(import_labelFrame, text = "...", command = lambda:browse(pathVar))
import_labelFrame.grid(row = 0, column = 0, padx = 10)
chosenDirectory.grid(row = 1, column = 0)
button_open.grid(row = 1, column = 1)

export_labelFrame = tk.LabelFrame(import_export_frame, text = "Export Directory")
pathVarTwo = tk.StringVar(export_labelFrame, "")
chosenDirectoryTwo = tk.Entry(export_labelFrame, textvariable=pathVarTwo)
button_openTwo = Button(export_labelFrame, text = "...", command=lambda:browse(pathVarTwo))
export_labelFrame.grid(row = 0, column = 1, padx = 10)
chosenDirectoryTwo.grid(row = 1, column = 0)
button_openTwo.grid(row = 1, column = 1)

button_analyze = Button(import_export_frame, text="Analyze", command=analyze)
button_analyze.grid(row = 0, column = 2, padx = 10)

button_testGrid  = Button(root, text="Test Grid View", command=lambda:open_grid_view(pathVar.get()))
button_testGrid.grid(row = 2, column = 0, pady=5)

root.grid_rowconfigure(0, weight = 1, minsize=100)
root.grid_rowconfigure(1, weight = 1, minsize=100)
root.grid_columnconfigure(0, weight = 1)

root.resizable(True, True)

root.mainloop()