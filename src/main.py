#/usr/bin/python3

from bapvuPrompt import bapvuPrompt
from os import name
from ctypes import *


if __name__ == '__main__':

    if name == 'nt':
        from ctypes import *
        retval = windll.user32.ShutdownBlockReasonCreate(
            'BAPVu',
            c_wchar_p("BAPVu is currently running!")
            )   
        if retval != 0:
                print('test')
    
    bapvuPrompt(completekey='tab', stdin=None, stdout=None).cmdloop()