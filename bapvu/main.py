from cmd import Cmd
import communications #handles all communication related functions.
import plotting #handles plotting
import fileHandling #file handling stuff


class MyPrompt(Cmd):

    intro = ' Welcome to BAPVu shell.\n This CLI allows for the control of data aqcuisition equipment. \n \n Type help or ? to list commands.\n'
    prompt = '(BAPVu) >'
    file = None

    def do_start(self, inp):
        """    Starts acquiring data.
        """
        global file
        #file = namefile()

        global start_time
        start_time = datetime.now()

        global sensors
        sensors = input('Input sensor names separated by spaces: ')

        global fieldnames
        fieldnames = ['systime', 'date', 'time_elapsed'] + sensors.split()

        filecreate(file, fieldnames)
        
        communications.start_acquisition(file)
        return

    def do_plot(self, inp):
        """starts plotting data.
        """
        return
    
    def do_devicelist(self, inp):
        print(communications.get_com_ports())
        return 


def main():
    
    MyPrompt().cmdloop()


if __name__ == '__main__':

    main()

