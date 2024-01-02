#/usr/bin/python3
import communications #handles all communication related functions.
import fileHandling #file handling stuff 
from sys import exit
from datetime import datetime
import multiprocessing as mp
import subprocess
import plotting #handles plotting
#from interactiveShell import interactiveShell # This will be used for the do_spawnShell function.
from bapvuPrompt import bapvuPrompt


def main(): 
    #check if at least one edaq device is connected. get_com_ports returns a list of serial devices. checks if list is empty
    if not communications.get_com_ports():
        print("No eDAQ device connected.")
        return

    file = fileHandling.namefile()
    start_time = datetime.now()
    sensors = input('Input sensor names separated by spaces: ')
    fieldnames = ['systime', 'date', 'time_elapsed'] + sensors.split()
    fileHandling.filecreate(file, fieldnames) # taking above input to generate file.


    data_aq_process=mp.Process(target=communications.start_acquisition, args=(file,)) # creates process to do data aqcquisition

    data_aq_process.start() # starts child process
    # checking if process was started sucessfully.
    if data_aq_process.is_alive():
        print("Run initiated.")

    bapvuPrompt().cmdloop()

    # terminates processes if the prompt is closed and they are still active


    if data_aq_process.is_alive():

        data_aq_process.terminate()

        data_aq_process.join()

    if plotting_process.is_alive():

        plotting_process.terminate()

        plotting_process.join()

if __name__ == '__main__':

    main()

