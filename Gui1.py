from tkinter import *
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from PIL import ImageTk, Image
from tkinter import filedialog
import os
import src.easyO, src.paddleO, src.rapidO, src.tess

def openDirectory():
    folder_selection = filedialog.askdirectory(initialdir="C:/Users/gugul/Documents/School/Capstone/imgFolder")
    folderPath.set(folder_selection)

def browse(pathVar):
    folder_selection = filedialog.askdirectory(initialdir="C:/Users/gugul/Documents/School/Capstone/imgFolder")
    pathVar.set(folder_selection)

def openAnalysisWindow():
    folder_path = filedialog.askdirectory(title="Select a Folder Containing Images")
    
    if not folder_path:
        return

    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        return
    
    multi_analysis_window = Toplevel(root)
    multi_analysis_window.title("Analyze Images")
    multi_analysis_window.geometry("500x600")

    img_label = Label(multi_analysis_window)
    img_label.pack()

    text_label = Label(multi_analysis_window, text="", justify=LEFT, padx=10, pady=10, wraplength=400)
    text_label.pack()

    button_frame = Frame(multi_analysis_window)
    button_frame.pack()

    current_index = [0]  

    def update_image():
        try:
            img = Image.open(image_files[current_index[0]])
            img = img.resize((400, 400))
            photo = ImageTk.PhotoImage(img)
            img_label.config(image=photo)
            img_label.image = photo
            
            analysis_output = f"Image {current_index[0] + 1} of {len(image_files)}\nFile Path: {image_files[current_index[0]]}\nFurther analysis results would be displayed here."
            text_label.config(text=analysis_output)
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

def openGridView():
    folder_path = filedialog.askdirectory(title="Select a Folder Containing Images")
    
    if not folder_path:
        return

    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
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

        def update_image():
            try:
                img = Image.open(image_files[current_index[0]])
                img = img.resize((400, 400))
                photo = ImageTk.PhotoImage(img)
                img_label.config(image=photo)
                img_label.image = photo
                
                analysis_output = f"Image {current_index[0] + 1} of {len(image_files)}\nFile Path: {image_files[current_index[0]]}\nFurther analysis results would be displayed here."
                text_label.config(text=analysis_output)
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
    if (pathVar.get() == "" or pathVar2.get() == ""):
        tkinter.messagebox.showinfo("Error", "Please select an import/export directory.")
        return
    if (modelDrop.get() == "EasyOCR"):
        src.easyO.printUsage(pathVar.get(), pathVar2.get())
    elif (modelDrop.get() == "RapidOCR"):
        src.rapidO.printUsage(pathVar.get(), pathVar2.get())
    elif (modelDrop.get() == "PaddleOCR"):
        src.paddleO.printUsage(pathVar.get(), pathVar2.get())
    elif (modelDrop.get() == "Tesseract"):
        src.tess.printUsage(pathVar.get(), pathVar2.get())

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
models = ["EasyOCR", "RapidOCR", "PaddleOCR", "Tesseract"]
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
