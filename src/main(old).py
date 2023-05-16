#!/usr/bin/python3
#sudo chmod 666 /dev/ttyACM0
from encodings import utf_8

import multiprocessing as mp
import subprocess
from cmd import Cmd
from time import sleep
from datetime import datetime
#from tkinter import Y, Tk




class file_write_error(Exception):
    """Exception raised when program is unable to write to file
    """



class MyPrompt(Cmd):

    intro = ' Welcome to the Bonrne again pod shell.\n This CLI allows for the control of data aqcuisition equipment. \n \n Type help or ? to list commands.\n'
    prompt = '(Borne again pod) >'
    file = None



    #def do_setup(self, args):
    ##this is how you add descriptions for help (function) in cmd module.
    #    'sets up edaqs \n Here are the arguments: '

    #    args = args.split('-')
    #    for arg in args:
    #        if arg == '':
    #            args.remove(arg)
        
    #    options = {}
        
    #    for arg in args:
    #        arg = arg.split()
    #        option_values = arg[1:]
    #        options[arg[0]] =  option_values

    #    if len(options['c']) != len(options['f']):
    #        print ("The number of specified channels does not match specified functions! \n Setup not changed.")
    #        return

    #    print(options)

    #    #need to finish by using options to properly configure edaqs.

    #    return


    def do_start(self, inp):
    #creates a file name and stores it under file. data will be decoded into this file.
        global file
        #file = namefile()

        global start_time
        start_time = datetime.now()

        global sensors
        sensors = input('Input sensor names separated by spaces: ')

        global fieldnames
        fieldnames = ['systime', 'date', 'time_elapsed'] + sensors.split()

        filecreate(file, fieldnames)

        p.start()

        if p.is_alive():
            print("Run initiated.")
            response = False
        else:
            print("The program encountered and error initiating run... \n The program will now exit.")
            response = True

        return response

    def do_plot(self, inp):

        p2.start()

        p3.start()

        if p2.is_alive():
            print("Run initiated.")
            response = False
        else:
            print("The program encountered and error initiating run... \n The program will now exit.")
            response = True

        return response

    def do_ls(self, inp):

        if inp == '':
            print('Here is a list of avaliable eDAQ devices: ')

            list_edaq=subprocess.Popen("/home/thomas/Dropbox/B.A.Vu/./list_edaqs.sh", stdout=subprocess.PIPE)
            output= list_edaq.stdout.read()
            output = bytes.decode(output)
            edaq_list = output.split('\n')

            for edaq in edaq_list:
                if edaq == '':
                    edaq_list.remove(edaq)
                    
            if len(edaq_list)==0:
                edaq_list = '(None)'

        print(edaq_list)

        return



    def do_exit(self, inp):

        if p.is_alive():

            while True:

                end_run=input("Run currently in progress. \n Are you sure you would like to end run? \n (y/n) > ")
                end_run_lower = end_run.lower()

                if end_run_lower=="y":
                    response=True
                    break
                #ask if the user wants to save results before exiting
                #if yes, save results
                elif end_run_lower=="n":
                    response=False
                    print("Continuing to acquire data...")
                    break
                else:
                    print("Invalid response. Try again")

        else:
            response = True

        return response



    def do_spawn_shell(self, inp):

        """
        Generates interactive shell. Accepts stdin and passes to the write() command from pyserial.

        """
        if inp == '':
            print('Here is a list of avaliable eDAQ devices: ')

            list_edaq=subprocess.Popen("/home/thomas/Dropbox/B.A.Vu/./list_edaqs.sh", stdout=subprocess.PIPE)
            output= list_edaq.stdout.read()
            output = bytes.decode(output)
            edaq_list = output.split('\n')

            for edaq in edaq_list:
                if edaq == '':
                    edaq_list.remove(edaq)
                    
            if len(edaq_list)==0:
                edaq_list = '(None)'

            print(edaq_list)

            edaq = input("Input a the selected device: ")

            if edaq in edaq_list:
                print('eDAQ selection is valid.')
                
            else:
                print("selected eDAQ not found. Try again.")
                return


        edaq_path = ''.join(['/dev/'+edaq])

        with serial.Serial() as ser: 
            ser.timeout=0
            ser.baudrate = 115200
            ser.bytesize=8
            ser.parity='N'
            ser.stopbits=1
            ser.port = edaq_path
            ser.close()
            ser.open()
            while (ser.isOpen()):
                stdin = input('EPU452 >>> ')
                #To add: if command is exit then exit function
                stdin = ''.join([stdin+'\n'])
                stdin = stdin.encode()
                ser.write(stdin)
                sleep(0.5)
                ser.readline()
            ser.close
            
        return

    def do_test(self, inp):

        print('this is a test!')
        while True:
            print('initializing test.')
            sleep(0.5)
            print('initializing test..')
            sleep(0.5)
            print('initializing test...')
            sleep(0.5)






    
def main():

    list_edaq=subprocess.Popen("/home/thomas/Dropbox/B.A.Vu/./list_edaqs.sh", stdout=subprocess.PIPE)
    output= list_edaq.stdout.read()
    output = bytes.decode(output)
    edaq_list = output.split('\n')
        
    for edaq in edaq_list:
        if edaq == '':
            edaq_list.remove(edaq)
            
            
    if edaq_list == []:
        print("eDAQ device not found... \n Please connect device and try again.")
        
        
                
    p = mp.Process(target=start_acquisition, name='start_acquisition')

    p3 = mp.Process(target=plot, name='plotting')


    MyPrompt().cmdloop()

    if p.is_alive():
        p.terminate()
        p.join()

    if p2.is_alive():
        p2.terminate()
        p2.join()

    if p3.is_alive():
        p3.terminate()
        p3.join()


if __name__ == '__main__':

    main()

