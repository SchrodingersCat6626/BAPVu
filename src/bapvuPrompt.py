from cmd import Cmd
import communications #handles all communication related functions.
import fileHandling #file handling stuff 
from sys import exit
from datetime import datetime
import multiprocessing as mp
import subprocess
import plotting #handles plotting
#from interactiveShell import interactiveShell # This will be used for the do_spawnShell function.

"""
To-do: I should add a table with all information during acquisition in cli as a function which updates periodically.


There is a bug that if the file name already exists the program crashes. Add extra check to do_start function. Also defining a bunch of global variables looks kind of stupid.
"""

class bapvuPrompt(Cmd):

    intro = ' Welcome to BAPVu shell.\n This CLI allows for the control of data aqcuisition equipment. \n \n Type help or ? to list commands.\n'
    prompt = '(BAPVu) >'
    file = None
    
    global filepath
    filepath=fileHandling.namefile() # must select filename before starting program.
    sensors = input('Input sensor names separated by spaces: ')
    fieldnames = ['systime', 'date', 'time_elapsed'] + sensors.split()
    fileHandling.filecreate(filepath, fieldnames) # taking above input to generate file.


    def do_start(self,inp):

        if not communications.get_com_ports():
            print("No eDAQ device connected.")
            return
        
        start_time = datetime.now()

        #global data_aq_process
        data_aq_process=mp.Process(target=communications.start_acquisition, args=(filepath,)) # creates process to do data aqcquisition

        if data_aq_process.is_alive():
            print("Run initiated.")
        
        return


    def do_stats(self, inp):
        """Outputs current configuration in table form (in an organized way) and run status. Allows user to ensure that the DAQ is configured correctly.
        """

        return


    def do_plot(self, inp,file):
        """starts plotting data.
        """

        # checks if data_aq_process if running exits if running

        print(data_aq_process.is_alive())
        
        try:


            if data_aq_process.is_alive():

                plotting_process = mp.Process(target=plotting.plot,
                        args=(file,)
                        )

                plotting_process.start()

                if plotting_process.is_alive():

                    print("Plotting initiated.")

                else:

                    print("Failed to initiate plotting process.")

            else:

                print("Data acquisition process not running. Run start to start acquiring data.")

                return
            

        except NameError:

            print("Data acquisition process not running. Run start to start acquiring data.")

            return
 
    
    def do_devicelist(self, inp):
        """ Outputs a list of devices. Lets the user know if no devices are found.
        """

        if not communications.get_com_ports():
            print("No eDAQ device found."
                    )
        else:
            print(
                    communications.get_com_ports()
                    )

    def do_exit(self, inp):
        """Exits the program
        """

        # closing child processes
        try:

            if plotting_process.is_alive():

                plotting_process.terminate() # sends sigterm to process
                

                plotting_process.join() # waits for program to terminate.

            if data_aq_process.is_alive(): 

                data_aq_process.kill() # sends sigterm to process
                
                data_aq_process.join() # waits for program to terminate.
        
        except NameError: # if this exception is raised either of the above processes were never defined so the program will simply exit

            exit()

        return 1 #Returning True exits the program


    def do_stop(self, inp):
        """Stops data acquisition by terminating data_aq_process process. Does not exit the program.
        """   

        print(data_aq_process)     

        #try:
            
            #data_aq_process.terminate() # sends sigterm to process
            
            #data_aq_process.join() # waits for program to terminate.
            
        #except NameError: # if this exception the process was never defined.

        #    print("Data acquisition process does not exist.")

        #    return

        return


    #def do_spawnShell(self, inp):
    #    """ Spawns a shell to directly send commands to the eDAQ device.
    #    """
    #
    #    I should just use the minishell submodule of the serial module instead of designing my own.
    #    However, the current code in that module needs to run in the main thread. I need to figure that part out..
     #   subprocess.run(interactiveShell.cmdloop())


    #  return

    

    # plotting_process.join() # I think this is required in case the plotting is exited in gui? remove if not required.

