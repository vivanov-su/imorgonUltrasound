from tkinter import *
import tkinter as tk
from tkinter import ttk
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


def openDirectory():
    folder_selection = filedialog.askdirectory(initialdir="C:/Users/gugul/Documents/School/Capstone/imgFolder")
    folderPath.set(folder_selection)

def browse(pathVar):
    folder_selection = filedialog.askdirectory(initialdir="C:/Users/gugul/Documents/School/Capstone/imgFolder")
    pathVar.set(folder_selection)

def openAnalysisWindow():
    ### Added test.py code (START)
    folder_path = filedialog.askdirectory(title="Select a Folder Containing Images")
    imgFolderName = os.path.basename(folder_path)

    valid_annotation_keywords = load_yaml_config("valid_annotation_keywords.yaml")
    vendor_inclusion_zones = load_yaml_config("vendor_inclusion_zones.yaml")
    ocr_settings = load_yaml_config("ocr_settings.yaml")

    true_results_yaml_path = os.path.join(folder_path, "true_results.yaml")
    true_results = load_yaml_config(true_results_yaml_path)

    performance_metrics = {}
    try:
        if f"{imgFolderName}_results.yaml" not in os.listdir("C:/dev/capstone/imorgonUltrasound/Export"):
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
                "C:/dev/capstone/imorgonUltrasound/Export", f"{imgFolderName}_results.yaml"
            )
            with open(output_file_path, "w") as output_file:
                yaml.dump(performance_metrics, output_file, default_flow_style=False)   
            ### Added test.py code (END)

    except Exception as e:
        print(f"Error during OCR processing: {e}")
    
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
                            yaml_path = f"C:/dev/capstone/imorgonUltrasound/imgFolder/{imgFolderName}/true_results.yaml"
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
    selected_mode = var.get()
    if selected_mode == 1:
        openAnalysisWindow()
    elif selected_mode == 2:
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


root = Tk()
root.title("iMorgon Annotation Extraction")
root.geometry("640x480")

imageDesc_Frame = Frame(root, pady = 5)
dropDown_Frame = Frame(root, pady = 5)
impExp_Frame = Frame(root, pady = 5)
button_Frame = Frame(root, pady = 5)
option_Frame = Frame(root, pady = 5)

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
option_Frame.grid(row = 3, column = 1)
button_Frame.grid(row = 4, column = 1, sticky=NSEW)

#IMAGE AND DESCRIPTION WIDGET
imageDesc_Frame.columnconfigure(0, weight=1)
imageDesc_Frame.columnconfigure(1, weight=1)
imageDesc_Frame.columnconfigure(2, weight=1)
logo = ImageTk.PhotoImage(Image.open("misc/logo.png"))
logo_label = Label(imageDesc_Frame, image=logo)
logo_label.grid(row = 0, column = 1, pady = (10, 5))
T = Text(imageDesc_Frame, height = 5, width = 30, wrap = WORD)
T.tag_configure("tag_name", justify='center')
desc = "Welcome to iMorgon's ultrasound annotation extraction program."
T.insert(tk.END, desc)
T.tag_add("tag_name", "1.0", "end")
T.grid(row = 1, column = 1, padx = (5, 10))

#DROPDOWN
dropDown_Frame.columnconfigure(0, weight=1)
dropDown_Frame.columnconfigure(1, weight=1)
dropDown_Frame.columnconfigure(2, weight=1)
modelFrame = LabelFrame(dropDown_Frame,text="Models")
modelFrame.grid(row = 0, column = 1, pady = 5)
models = ["EasyOCR", "RapidOCR", "PaddleOCR", "DocTR", "Tesseract"]
modelDrop = ttk.Combobox(modelFrame, value=models)
modelDrop.current(0)
modelDrop.grid(row=0, pady = 5)

#IMPORT AND EXPORT BUTTON WDIGET
impExp_Frame.columnconfigure(0, weight=1)
impExp_Frame.columnconfigure(1, weight=1)
impExp_Frame.columnconfigure(2, weight=1)
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

#CHECKBOX OPTION FRAME
option_Frame.columnconfigure(0, weight=1)
option_Frame.columnconfigure(1, weight=1)
option_Frame.columnconfigure(2, weight=1)
view_labelFrame = tk.LabelFrame(option_Frame, text="View Mode")
var = IntVar()
singleCheck = Checkbutton(option_Frame, text="Single View", variable=var, onvalue=1, offvalue=0)
multiCheck = Checkbutton(option_Frame, text="Multiple Image View", variable=var, onvalue=2, offvalue=0)
singleCheck.grid(row = 0, column = 1, pady = 5)
multiCheck.grid(row = 1, column = 1, pady = 5)

#BUTTON FRAME
button_Frame.columnconfigure(0, weight=1)
button_Frame.columnconfigure(1, weight=1)
button_Frame.columnconfigure(2, weight=1)
button_close = Button(button_Frame, text="Close", command=root.quit)
button_extract = Button(button_Frame, text="Extract", command=extract)
button_analyze = Button(button_Frame, text="Analyze Images", command = analyze_images)
button_close.grid(row = 0, column = 0, pady = 5)
button_analyze.grid(row = 0, column = 1, pady=5)
button_extract.grid(row = 0, column = 2, pady=5)

root.mainloop()
