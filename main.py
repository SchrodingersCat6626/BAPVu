#!/home/thomas/Dropbox/B.A.Vu/.venv/bin/python3
# bash: source /home/thomas/Dropbox/B.A.Vu/.venv/bin/activate
#sudo chmod 666 /dev/ttyACM0
from encodings import utf_8
import os
import serial
import multiprocessing as mp
import subprocess
from cmd import Cmd
import csv
from time import sleep
from datetime import datetime
from tkinter import Y, Tk
from tkinter.filedialog import askdirectory
from tkinter import messagebox
import serial.tools.list_ports


#add this to get names of edaqss


class file_write_error(Exception):
    """Exception raised when program is unable to write to file
    """


def list_devices():
    """ This function returns a list of serial devices.
    """
    ports = serial.tools.list_ports.comports()
    ports_list = []

    for port, desc, hwid in sorted(ports):
        #"{}: {} [{}]".format(port, desc, hwid)
        ports_list.append("{}".format(port))

    return(ports_list)


def namefile():
    
    #Stupid function to name file. Should rewrite to remove gui components
    
    while True:
        path = askdirectory(title='Select folder')
        filename = input("What would you like to name the file (no extensions): ")
        file = path+"/"+filename+".csv"
        if os.path.isfile(file) == True:
            messagebox.showerror("Filename conflict", "File already exists. Choose another filename.")
        elif os.path.isfile(file) == False:
            break
        else:
            messagebox.showerror("Error", "Unknown error!")
    return str(file)


def filecreate(file, fieldnames):
    try:
        with open(file, 'x', encoding='UTF8') as f:
            csv_object = csv.writer(f)
            csv_object.writerow(fieldnames)
    except     file_write_error:
        messagebox.showerror("File creation error", "Unable to create file.")

def data_decode():
    #decoding the data
    with open('data_test.dat', 'rb') as data_decoded:
        data1=data_decoded.readlines()
        for line in data1:
            line.decode('ascii')
    return data_decoded


def plot():
    i=0
    x=list()
    y=list()
    i=0
    while True:
        data = ser.readline()
        print(data.decode())
        x.append(i)
        y.append(data.decode())
    
        plt.scatter(i, float(data.decode()))
        i += 1
        plt.show()
        plt.pause(0.0001)  # Note this correction

def read_signal():

    dat_file= '/home/thomas/edaq_datafiles/'+str(datetime.now())+'.dat'

#I need to pass in active channels, function (ex.biosensor,pH), #of decimal places

#how to deal with multiple edaqs?

#calibration can be handled during decoding 

#ask for all paths to edaq by calling external script.


#outputs a list of edaqs while removing blank elements

#would it be better to have a for loops inside the main functions? I think it would be better because it can ask for info on each edaq then open each channel or something.
    with serial.Serial() as ser: 
        ser.timeout=0
        ser.baudrate = 115200
        ser.bytesize=8
        ser.parity='N'
        ser.stopbits=1
        ser.port = '/dev/ttyACM0'
        ser.close()
        ser.open()
       # #sample rate set to 10Hz since this is the max for Biosensor mode.
        ser.write(b'beep\n')
        sleep(1)
        ser.write(b'set c 4 func mv \n')
        sleep(1)
        ser.write(b's 10\n')
        sleep(1)

        with open(dat_file, 'wb') as f:

            while True:
                start_time = datetime.now()
                response = ser.readlines(255)
                f.writelines(response)
                end_time = datetime.now()
                print(end_time - start_time)
                sleep(0.01)
    
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
        
        
        #return commented out for debugging purposes. Uncomment in final product to exit main function if edaq is not connected.
        
        #return
        
                
    p = mp.Process(target=read_signal, name='read_signal')

    p2 = mp.Process(target=data_decode, name='data_decode')

    p3 = mp.Process(target=plot, name='plotting')




#def set_channels_type():
    """ Sets channel types"""

#def set_channel_rate():
    """ Set to a default rate of 1/sec"""








    class MyPrompt(Cmd):
        intro = ' Welcome to the Bonrne again pod shell.\n This CLI allows for the control of data aqcuisition equipment. \n \n Type help or ? to list commands.\n'
        prompt = '(Borne again pod) >'
        file = None

        def do_setup(self, args):
        #this is how you add descriptions for help (function) in cmd module.
            'sets up edaqs \n Here are the arguments: '

            args = args.split('-')
            for arg in args:
                if arg == '':
                    args.remove(arg)
            
            options = {}
            
            for arg in args:
                arg = arg.split()
                option_values = arg[1:]
                options[arg[0]] =  option_values

            if len(options['c']) != len(options['f']):
                print ("The number of specified channels does not match specified functions! \n Setup not changed.")
                return

            
            print(options)

            #need to finish by using options to properly configure edaqs.

            return


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

        def do_list_edaqs(self, inp):
            print(list_devices())




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

#do you want to save comments. The comments are stored with timestamps in a sep. file. Then if yes. Merger according to timestamp with data.
#experimental conditions can be one class of comments (repet.) Single event class which is in a sep. column.

#once sequence feat. added merge with data in a sep. column

#needs to be a way to change the voltage...etc. add a command for that.
if __name__ == '__main__':

    main()

