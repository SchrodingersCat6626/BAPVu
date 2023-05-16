#/usr/bin/python3
from cmd import Cmd
from sys import exit
import communications #handles all communication related functions.
import plotting #handles plotting
import fileHandling #file handling stuff
import multiprocessing as mp 


class MyPrompt(Cmd):

    intro = ' Welcome to BAPVu shell.\n This CLI allows for the control of data aqcuisition equipment. \n \n Type help or ? to list commands.\n'
    prompt = '(BAPVu) >'
    file = None

    def do_start(self, inp):
        """    
        Starts a new process which is used for data acquisition. 
        This continues until exit or stop command is issued. If
        the data is already being acquired, then it will exit the function.
        """
        try:
            #check if data collection process already exist
            if data_aq_process.is_alive():

                print("Data acquisition process already running!")

                return

        except NameError: # if NameError exception is raised than process was not defined. aka doesn't exist.
            # if the data_aq process doesn't exists the function will continue.

        #check if at least one edaq device is connected. get_com_ports returns a list of serial devices. checks if list is empty
            if not communications.get_com_ports():

                print("No eDAQ device connected.")

                return

            # exporting some global variables
            global file
            file = fileHandling.namefile()

            global start_time
            start_time = datetime.now()

            global sensors
            sensors = input('Input sensor names separated by spaces: ')

            global fieldnames
            fieldnames = ['systime', 'date', 'time_elapsed'] + sensors.split()

            fileHandling.filecreate(file, fieldnames) # taking above input to generate file.
            
            data_aq_process = mp(target="communications.start_acquisition",
                    args=('file',)
                    ) # creates process to do data aqcquisition

            data_aq_process.start() # starts child process

        # checking if process was started sucessfully.
            if data_aq_process.is_alive():

                print("Run initiated.")

            else:

                print(
                        "The program encountered and error initiating run... \n The program will now exit."
                        )

        return

    def do_plot(self, inp):
        """starts plotting data.
        """

        # checks if data_aq_process if running exits if running
        try:

            data_aq_process.is_alive()

            if not data_aq_process.is_alive(): 

                print(
                        "Data acquisition process not running. Run start to start acquiring data."
                        )

                return
            
            else:

                plotting_process = mp(target="plotting.plot",
                        args=('file',)
                        )

                plotting_process.start()

                if plotting_process.is_alive():

                    print("Plotting initiated.")

                else:

                    print("Plotting error.")

                return

        except NameError:

            print("Data acquisition process not running. Run start to start acquiring data.")

            return
 
    
    def do_devicelist(self, inp):

        print(communications.get_com_ports())

        return

 

    def do_exit(self, inp):

        # closing child processes


        exit() # exits the program if no other threads are running?

        return

    

    def do_spawn_shell(self, inp):

        return


def main():
    
    MyPrompt().cmdloop()


if __name__ == '__main__':

    main()

