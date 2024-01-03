#!/usr/bin/python3
#import os
from tkinter.filedialog import asksaveasfilename

def namefile():
    """
    """
    file = asksaveasfilename() # Returns a filename with the full path. Note: does not create the file. If the file already exists they ask the user if 
    return file
 
 
def filecreate(file, fieldnames):
    # maybe I should check if the file has content if it exists and ask for another confirmation?
    try:
        with open(file, 'w', encoding='UTF8') as f:
            f.write(','.join(fieldnames))

    except OSError:
        print("File creation error", "Unable to create file.")


