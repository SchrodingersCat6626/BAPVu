import subprocess
import sys
import importlib
import re
from os import name

#1. Installs all required dependencies. (Assumes user has already installed python 3.11)

#To do:
#
#    1. Copy the program to the program directory.
#    2. Create shortcut to program on desktop.



def is_installed(package):
    try:
        #importlib.import_module(package.split('==')[0]) ### This doesn't check the version. Only package name
        importlib.import_module(
                re.sub(
                    "[^a-zA-Z]",
                    "", # removes any chars that are not a-z or A-Z sub. with nothing.
                    package
                    )
                )
        return True
    
    except:
        
        return False


def install(package):
    """ Requires that pip and python be in the users path """
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def install_depends():
    f = open('requirements.txt','r')
    for line in f:
        package = line
        if is_installed(package)==False: ## if false it will not run
            install(package)
        else:
            print('Installed')
            continue



install_depends()

### Creating desktop shortcut for the windows users.
### I may need to install pywin32 or something to get win32com?
if name == 'nt':
    import shutil
    import os, winshell
    
    desktop = winshell.desktop()
    ## Copying files to program folder.
    shutil.copytree(os.getcwd(), 'C:'+'\\'+'Program Files'+'\\'+'BAPVu')

    from win32com.client import Dispatch
    
    desktop = winshell.desktop()
    path = os.path.join(desktop, "BAPVu.lnk")
    target = 'C:'+'\\'+'Program Files'+'\\'+'BAPVu'+'\\'+'src'+'\\'+'main.py'
    wDir = 'C:'+'\\'+'Program Files'+'\\'+'BAPVu'+'\\'+'src'
    #icon =
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    #shortcut.IconLocation = icon
    shortcut.save()

            
# for mac and linux(here, os.name is 'posix')

else:
    
    print('Not adding to binaries yet.')

