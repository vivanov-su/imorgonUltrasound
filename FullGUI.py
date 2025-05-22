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

#--------------------------------------HARD-CODED DIRECTORIES AND MODELS LIST--------------------------------------

exportDirectory = "C:/Users/gugul/Documents/School/Capstone/export"
imgFolder = "C:/Users/gugul/Documents/School/Capstone/imgFolder/imgFolder"

models = ["RapidOCR", "EasyOCR", "DocTR", "PaddleOCR", "Tesseract"]

#--------------------------------------Primary Functions--------------------------------------

#Formatted as a grid with searchable keywords
def open_grid_view(imageFolder):       
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

            img_button = Button(gallery_frame, image=photo, command=open_single_view)
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
def open_single_view():     
    print("Open Andy's favorite image")

#Extracts keywords if .yaml file doesn't exist yet, then calls 'open_grid_view'
def analyze():              
    if pathVar.get() == "" or pathVarTwo.get() == "":
        tkinter.messagebox.showinfo("Error", "Please select an import/export directory.")
        return

    imageFolder = pathVar.get()
    exportFolder = pathVarTwo.get()

    valid_annotation_keywords = load_yaml_config("valid_annotation_keywords.yaml")
    vendor_inclusion_zones = load_yaml_config("vendor_inclusion_zones.yaml")
    ocr_settings = load_yaml_config("ocr_settings.yaml")

    true_results_yaml_path = os.path.join(imageFolder, "true_results.yaml")
    true_results = load_yaml_config(true_results_yaml_path)
    
    performance_metrics = {}
    try:
        if f"{imageFolder}_results.yaml" not in os.listdir(exportFolder):
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

                output_file_path = os.path.join(exportFolder, f"{imageFolder}_results.yaml")
                with open(output_file_path, "w") as output_file:
                    yaml.dump(performance_metrics, output_file, default_flow_style=False)   

    except Exception as e:
        print(f"Error 1 during OCR processing: {e}")

    open_grid_view(imageFolder)

#--------------------------------------Misc Definitions--------------------------------------

def browse(pathVariable):
    folder_selection = filedialog.askdirectory(initialdir=imgFolder)
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