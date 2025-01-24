from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from tkinter import filedialog

def openDirectory():
    folder_selection = filedialog.askdirectory(initialdir="C:/Users/gugul/Documents/School/Capstone/imgFolder")
    folderPath = set(folder_selection)

def browse(pathVar):
    folder_selection = filedialog.askdirectory(initialdir="C:/Users/gugul/Documents/School/Capstone/imgFolder")
    pathVar.set(folder_selection)

class Description:
    def __init__(self, master):
        T = Text(root, height = 5, width = 30, wrap = WORD)
        T.tag_configure("tag_name", justify='center')
        desc = "Welcome to iMorgon's ultrasound annotation extraction program."
        T.insert(tk.END, desc)
        T.tag_add("tag_name", "1.0", "end")
        T.columnconfigure(0, weight=1)
        T.grid(row = 1, column = 1, padx = (5, 10))
        T.columnconfigure(2, weight=1)
        
class Dropdown:
    def __init__(self, master):
            modelFrame = LabelFrame(root,text="Models")
            modelFrame.columnconfigure(0, weight=1)
            modelFrame.grid(row = 2, column = 1, pady = 5)
            modelFrame.columnconfigure(2, weight=1)
            models = ["EasyOCR", "RapidOCR", "PaddleOCR", "Tesseract"]
            modelDrop = ttk.Combobox(modelFrame, value=models)
            modelDrop.current(0)

            modelDrop.grid(row = 1, column = 1, pady = 5)
            info1 = Label(modelFrame, text="EasyOCR: Information about OCR model", justify='left')
            info2 = Label(modelFrame, text="RapidOCR: Information about OCR model", justify='left')
            info3 = Label(modelFrame, text="PaddleOCR: Information about OCR model", justify='left')
            info4 = Label(modelFrame, text="Tesseract: Information about OCR model", justify='left')
            info1.grid(row = 2, column = 1)
            info2.grid(row = 3, column = 1)
            info3.grid(row = 4, column = 1)
            info4.grid(row = 5, column = 1)
            modelDrop.columnconfigure(2, weight=1)
            pass

class ImportDirectory:
    def __init__(self, master):
        import_labelFrame = tk.LabelFrame(root, text = "Import Directory")
        pathVar = tk.StringVar(import_labelFrame, "")
        import_labelFrame.grid(row=6, column=0, padx = 5)
        chosenDirectory = tk.Entry(import_labelFrame, textvariable=pathVar)
        chosenDirectory.grid(row = 6, column = 0, padx = 5)
        button_openFile = Button(import_labelFrame, text = "...", command = lambda: browse(pathVar))
        button_openFile.grid(row = 6, column = 1, padx = 5)

class ExportDirectory:
    def __init__(self, master):
        export_labelFrame = tk.LabelFrame(root, text = "Export Directory")
        pathVar2 = tk.StringVar(export_labelFrame, "")
        export_labelFrame.grid(row=6, column=1, padx = 5)
        chosenDirectory = tk.Entry(export_labelFrame, textvariable=pathVar2)
        chosenDirectory.grid(row = 6, column = 0, padx = 5)
        button_openFile = Button(export_labelFrame, text = "...", command = lambda: browse(pathVar2))
        button_openFile.grid(row = 6, column = 1, padx = 5)

class Buttons:
    def __init__(self, master):
        button_close = Button(root, text="Close", command=root.quit)
        button_extract = Button(root, text="Extract")
        button_close.grid(row = 7, column = 0, padx = (5, 50), pady = 10)
        button_extract.grid(row = 7, column = 1, padx = (50, 5), pady = 10)

root = Tk()
root.title("iMorgon Annotation Extraction")
root.geometry("640x480")

description = Description(root)
drop = Dropdown(root)

#Logo display - Not in its own method because of referencing oddities
root.columnconfigure(0, weight=1)
logo = ImageTk.PhotoImage(Image.open("misc/logo.png"))
logo_label = Label(image=logo)
logo_label.grid(row = 0, column = 1, pady = (10, 5))
root.columnconfigure(2, weight=1)

imp = ImportDirectory(root)
exp = ExportDirectory(root)

cmdButtons = Buttons(root)

root.mainloop()