
from tkinter.filedialog import askdirectory
import os

def namefile():
    """
Asks user to select directory and filename for the data output file where the data will be output. Returns the filename in the form of a string.

    """
    while True:
        path = askdirectory(title='Select folder')
        filename = input("What would you like to name the file (no extensions): ")
        file = path+"/"+filename+".csv"
        if os.path.isfile(file) == True:
            print("Filename conflict", "File already exists. Choose another filename.")
        elif os.path.isfile(file) == False:
            break
        else:
            messagebox.showerror("Error", "Unknown error!")
    return str(file)


def filecreate(file, fieldnames):
    try:
        with open(file, 'x', encoding='UTF8') as f:
            f.write()
    except     file_write_error:
        messagebox.showerror("File creation error", "Unable to create file.")

