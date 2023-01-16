#!/home/thomas/Dropbox/B.A.Vu/.venv/bin/python3 
import serial
import serial.tools.list_ports
from time import sleep
from time import time

"""
To do:

    At the moment I am using the standard pyserial library which doesn't support parallel ports. I am just looping through the different ports. There is a pyParallel library which provides this feature. However, it is still experimental (https://github.com/pyserial/pyparalle). If this library becomes stable in the future I can explore implementing it in this project.

"""

def get_com_ports():
    """ 
    Returns list object of names of current com devices (in /dev/... format for linux)
    """
    ports = serial.tools.list_ports.comports()
    
    ports_list = []
    
    for port, desc, hwid in sorted(ports):
        #"{}: {} [{}]".format(port, desc, hwid)
       ports_list.append("{}".format(port))
    
    return ports_list


def write_data(ser, args):
    """
    accepts serial object and argument. Passes arguments into pyserial write() 
    """
    #clearing input buffer
    ser.reset_input_buffer()
    # formating arguments
    stdin = args
    stdin = ''.join([stdin+'\n'])
    stdin = stdin.encode()
    #writing arguments
    ser.write(stdin)
    sleep(1)
    # clearing output buffer
    ser.reset_output_buffer()
    return

def read_data(ser):
    """
    Reads data from device. Accepts a serial device as argument and returns a list which includes all the data for each channel with posix time on index 0.

    """
    try:
        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes.decode()
        output = format_output(decoded_bytes)

    except:
        ser.close()

    return output


def format_output(output):
    """ 
    formats output to remove newlines and prompt.
    Accepts a str object as arg. Also adds posix time at index 0. Returns a list.

    """
    #removing newline and other whitespace char
    output = output.strip()
    #removing prompt. specific to podvu
    output = output.strip("EPU452 Readings")
    output.insert(0, time.time())

    return output


def write_to_file(data, file):
    with open(file, 'a') as f:
        f.write(data)



def start_acquisition(file):
    """


    """
    # Reading a list of com ports
    ports = get_com_ports()

    if len(ports) > 4:
        
        print("Warning, reading from more than 4 eDAQ's at a time is not recommended...")

        while True:

            anwser = input("Would you like to proceed(y/n): ")
            
            if anwser == y:

                break

            elif anwser == n:

                return (print("Cancelling..."))
            else:

                print("Please enter valid input.")

    """
    I should also limit the number of eDAQ's to 3-4 per session. To run more one can always run the program twice.... 
    """

    #creating a list of serial objects.
    ser = [
            serial.Serial(
            port = port,
            timeout=0,
            baudrate = 115200,
            bytesize=8,
            parity='N',
            stopbits=1
            )

    for port in ports
    ]


    for serial_obj in ser:
        write_data(serial_obj, 's 10')

    while True:

        data = [read_data(serial_obj) for serial_obj in ser]
        write_to_file(data, file)
        sleep(0.1)

