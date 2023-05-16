#/usr/bin/python3
from cmd import Cmd
import communications #handles all communication related functions.
import plotting #handles plotting
import fileHandling #file handling stuff
import multiprocessing as mp 


class MyPrompt(Cmd):

    intro = ' Welcome to BAPVu shell.\n This CLI allows for the control of data aqcuisition equipment. \n \n Type help or ? to list commands.\n'
    prompt = '(BAPVu) >'
    file = None

    def do_start(self, inp):
        """    Starts a new process which is used for data acquisition. This continues until exit or stop command is issued..
        """

        #check if data collection process already exists
       if p.is_alive():
            print("Run already started")
            return
        else:
            # exporting some global variables

            global file
            #file = namefile()

            global start_time
            start_time = datetime.now()

            global sensors
            sensors = input('Input sensor names separated by spaces: ')

            global fieldnames
            fieldnames = ['systime', 'date', 'time_elapsed'] + sensors.split()

            filecreate(file, fieldnames)
            
            p = mp(target="communications.start_acquisition",
                    args=('file',)
                    ) # creates process to do data aqcquisition

            p.start() # starts process

        # checking if process was started sucessfully.
           if p.is_alive():
                print("Run initiated.")
            else:
                print(
                        "The program encountered and error initiating run... \n The program will now exit."
                        )

        return

    def do_plot(self, inp):
        """starts plotting data.
        """

        if p.is_a

        if p2.is_alive():
            print("Run initiated.")
            response = False
        else:
            print("The program encountered and error initiating run... \n The program will now exit.")
            response = True

        return response
        
        return
    
    def do_devicelist(self, inp):
        print(communications.get_com_ports())
        return

    def do_exit(self, inp)

    

    def do_spawn_shell(self, inp):

def main():
    
    MyPrompt().cmdloop()


if __name__ == '__main__':

    main()

