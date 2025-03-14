from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.ttk import *
import yaml
from PIL import ImageTk, Image
import os

def openDirectory():
    file_selection = filedialog.askopenfilename(initialdir="C:/Users/gugul/Documents/School/Capstone/imgFolder", filetypes=[("Data Files", "*.yaml")])
    folderPath.set(file_selection)
    createDict(file_selection)
    openWindow()

def createDict(file_selection):
    with open(file_selection) as y:
        res = yaml.safe_load(y)
    result.update(res)

def openWindow():
    folder_path = filedialog.askdirectory(title="Select a Folder Containing Images")
    imgFolder.set(folder_path)

    if not folder_path:
        return

    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff'))]
    if not image_files:
        return
    
    newWindow = Toplevel(root)
    newWindow.title("Gallery")
    newWindow.geometry("600x480")

    print_Dict = Button(newWindow, text="Exit", command=root.quit)  #can be used to print dictionary
    print_Dict.grid(row=0, column=0)

    keywordList = list(result.values())
    kList = []
    for li in keywordList:
        for item in li:
            kList.append(item)

    filter_Box = Combobox(newWindow, value=kList)
    filter_Box.set('Filter')
    filter_Box.grid(row=0, column=1, padx=5, pady=5)

    filter_Button = Button(master=newWindow, text="Filter", command=lambda: Filter(filter_Box.get()))
    filter_Button.grid(row=0, column=2, padx=5, pady=5)

    grid_Frame = Frame(newWindow)
    grid_Frame.grid(row=1, column=1, sticky="nsew")
    
    row, col = 0, 0
    max_cols = 3  

    canvas = Canvas(grid_Frame)
    scrollbar = Scrollbar(grid_Frame, orient="vertical", command=canvas.yview)
    
    canvas.configure(yscrollcommand=scrollbar.set)

    content_Frame = Frame(canvas)
    content_Frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=content_Frame, anchor="nw")
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    for idx, file in enumerate(image_files):
        try:
            img = Image.open(file)
            img = img.resize((100, 100))  
            photo = ImageTk.PhotoImage(img)

            btn = Button(content_Frame, image=photo)
            btn.image = photo  
            btn.grid(row=row, column=col, padx=5, pady=5)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        except Exception as e:
            print(f"Error loading image {file}: {e}")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

def Filter(filterWord):
    image_files = [os.path.join(imgFolder.get(), f) for f in os.listdir(imgFolder.get()) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff'))]

    filterWindow = Toplevel(root)
    filterWindow.title("Filter Results")
    filterWindow.geometry("600x480")
    exit_button = Button(filterWindow, text="Exit", command=filterWindow.quit)
    exit_button.grid(row=0, column=0)
    desc = Label(filterWindow, text="Filtered Images")
    desc.grid(row=0, column = 1, padx = 5, pady = 5)

    selectedWord = Label(filterWindow, text=filterWord)
    selectedWord.grid(row = 0, column = 2, padx = 5, pady = 5)

    g_Frame = Frame(filterWindow)
    g_Frame.grid(row = 1, column = 1, sticky = "nsew")

    row, col = 0, 0
    max_cols = 3

    canvas = Canvas(g_Frame)
    scrollbar = Scrollbar(g_Frame, orient="vertical", command=canvas.yview)
    
    canvas.configure(yscrollcommand=scrollbar.set)

    content_Frame = Frame(canvas)
    content_Frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=content_Frame, anchor="nw")
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    for idx, file in enumerate(image_files):
        try:
            if(filterWord in result[os.path.basename(file)]):
                #print(os.path.basename(file))
                img = Image.open(file)
                img = img.resize((100, 100))  
                photo = ImageTk.PhotoImage(img)

                btn = Button(content_Frame, image=photo)
                btn.image = photo  
                btn.grid(row=row, column=col, padx=5, pady=5)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

        except Exception as e:
            print(f"Error loading image {file}: {e}")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)


root = Tk()
root.title("Keyword Filter Test")
root.geometry("680x480")

folderPath = StringVar()
yaml_File = ""
imgFolder = StringVar()
result = {}

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
desc = Label(root, text="Search for a valid keyword")
desc.grid(row=0, column=1)

select_Dir = Button(root, text="Select .yaml File", command=openDirectory)
select_Dir.grid(row=1, column=1)

root.mainloop()