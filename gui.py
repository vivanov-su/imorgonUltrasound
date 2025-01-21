from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog

def openDirectory():
    folder_selection = filedialog.askdirectory(initialdir="C:/Users/gugul/Documents/School/Capstone/imgFolder")
    folderPath = set(folder_selection)

root = Tk()
root.title("iMorgon Annotation Extraction")
root.geometry("640x480")

desc_frame = LabelFrame(root, text="Description")
desc_frame.pack()

description = Label(desc_frame, text="Welcome to iMorgon Medical's annotation extraction program! (From here would be generic instructions on how to use the program)")
description.pack()

logo = ImageTk.PhotoImage(Image.open("misc/logo.png"))
logo_label = Label(image=logo)
logo_label.pack()


folderPath = StringVar()
button_openFile = Button(root, text="Import Directory", command=openDirectory)
button_openFile.pack()

button_openDirectory = Button(root, text="Extract Directory", command=openDirectory)
button_openDirectory.pack()

button_close = Button(root, text="Close", command=root.quit)
button_extract = Button(root, text="Extract")
button_close.pack()
button_extract.pack()

root.mainloop()