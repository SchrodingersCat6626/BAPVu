from cmd import Cmd
import communications #handles all communication related functions.
import alkalinity_module
from sys import exit
from os import system, name
from datetime import datetime
import multiprocessing as mp
import subprocess
import plotting #handles plotting
import fileHandling #file handling stuff 
#from interactiveShell import interactiveShell # This will be used for the do_spawnShell function.
import tabulate

"""
To-do: I should add a table with all information during acquisition in cli as a function which updates periodically.


There is a bug that if the file name already exists the program crashes. Add extra check to do_start function. Also defining a bunch of global variables looks kind of stupid.
"""

class bapvuPrompt(Cmd):

    intro = ' Welcome to BAPVu shell.\n This CLI allows for the control of data aqcuisition equipment. \n \n Type help or ? to list commands.\n'
    prompt = '(BAPVu) >'
    file = None
    
    def preloop(self):

        global filepath

        filepath=fileHandling.namefile() # must select filename before starting program.

        print(filepath)

        sensors = input('Input sensor names separated by spaces: ')


        global fieldnames

        fieldnames = sensors.split()
        fieldnames = ',units,'.join(fieldnames)
        fieldnames = fieldnames.split(',')
        fieldnames.insert(0,'systime')
        fieldnames.append('unit')

        fileHandling.filecreate(filepath, fieldnames) # taking above input to generate file.


    def emptyline(self):
        """Overwriting behaviour of repeating last command
        """
        return
    
    def do_start(self,inp):

        match inp:

            case None | '':

                if 'data_aq_process' in globals():
                    print('Data acquisition process already running!')
                    return

                if not communications.get_com_ports():
                    print("No eDAQ device connected.")
                    return
                
                #global data_aq_process
                
                global data_aq_process
                data_aq_process=mp.Process(target=communications.start_acquisition, 
                args=(filepath,),name='data_acquisition') # creates process to do data aqcquisition

                
                start_time = datetime.now()
                data_aq_process.start()

                if data_aq_process.is_alive():
                    print("Run initiated.")

                print(data_aq_process)

                return

            case '--titration':
                ## runs default titration experiment
                # ## Returns and the experiment runs while returning to prompt
                print("placeholder")
                
                return

            case 'sweep':
                # do not return until sweep is completed and saved to file.

                daq_num = 1
                print("The number of eDAQ's set to 1. (Only supported option)")

                electrolyzer_channel = int(input("Which channel is the electrolyzer set up on (1,2,3, or 4): "))
                min_voltage = float(input("Min voltage (mV): "))
                max_voltage = float(input("Max voltage (mV): "))
                step_size = float(input("Step size (mV): "))
                time_per_step = float(input("Time per step (sec) (example:1200 is 20 mins): "))

                print("Volage limit set to 2000 mV by default.")


                alkalinity_module.voltage_sweep(filepath=filepath, electrolyzer_channel=electrolyzer_channel, 
                fieldnames=fieldnames,
                min_voltage=min_voltage, max_voltage=max_voltage,
                volt_step_size=step_size, volt_limit=2000,
                time_per_step=time_per_step, daq_num=daq_num)
                
                return



    def do_stats(self, inp):
        """Outputs current configuration in table form (in an organized way) and run status. Allows user to ensure that the DAQ is configured correctly.
        """

        global fieldnames

        if inp=='':

            ################# Maybe these shouldn't be in the plotting library if they are used here like this #################

            table_data = plot.readNewChunk ## Use a function to read 
            table_data = table_data.plot.decode_chunk(table_data)

            print(tabulate.tabulate(table_data, headers=fieldnames,tablefmt="pretty"))

        elif inp=='--monitor':

            ################# Maybe these shouldn't be in the plotting library if they are used here like this #################

            while True:

                table_data = plot.readNewChunk ## Use a function to read 
                table_data = table_data.plot.decode_chunk(table_data)

                print(tabulate.tabulate(table_data, headers=fieldnames,tablefmt="pretty"))

                sleep(5)

                #### Add exception for keyinterupt? How to exit this gracefully.



        return


    def do_plot(self, inp):
        """starts plotting data.
        """

        # checks if data_aq_process if running exits if running

        print(data_aq_process.is_alive())
        
        try:


            if data_aq_process.is_alive():

                ## To do: Add check to see if plotting process exists. If exists, check if alive.
                ## If not alive then create process and start process.


                plotting_process = mp.Process(target=plotting.plot,
                        args=(filepath,), name='plotting'
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

            if data_aq_process.is_alive(): 

                data_aq_process.kill() # sends sigterm to process
                
                data_aq_process.join() # waits for program to terminate.
        
        except NameError: # if this exception is raised either of the above processes were never defined so the program will simply exit

            exit()

        return 1 #Returning True exits the program


    def do_stop(self, inp):
        """Stops data acquisition by terminating data_aq_process process. Does not exit the program.
        """      
        try:

            ### For some reason it always gives a name error.
            ### Fix this bug.
            data_aq_process.kill() # sends sigterm to process
            
            data_aq_process.join() # waits for program to terminate.

            print(data_aq_process)

            del data_aq_process

            
        except NameError: # if this exception the process was never defined.

            print("Data acquisition process does not exist.")

            return

        return

        # define our clear functio
        # 
    def do_clear(self,inp):
        # for windows
        if name == 'nt':
            _ = system('cls')
            
        # for mac and linux(here, os.name is 'posix')
        
        else:
            _ = system('clear')


    #def do_spawnShell(self, inp):
    #    """ Spawns a shell to directly send commands to the eDAQ device.
    #    """
    #
    #    I should just use the minishell submodule of the serial module instead of designing my own.
    #    However, the current code in that module needs to run in the main thread. I need to figure that part out..
     #   subprocess.run(interactiveShell.cmdloop())


    #  return

    

    # plotting_process.join() # I think this is required in case the plotting is exited in gui? remove if not required.

