#!/usr/bin/python3 
import serial
import serial.tools.list_ports
from time import sleep
from time import time
import itertools
import csv

"""
To do:

    Better data formatting (check if data that will be written to file is correct len)
    Bug where one of the devices stops sending data. I should check if both devices are sending data.
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

    #### Weird hacky solution to a bug where if it seems that the device will sometimes not clear the number 10 from the last command... I should probably fix this ###
    # Basically this fix just sends a newline to the device which will run whatever command is saved
    # which, if it is leftover nonsense will error durring the 2 second sleep and won't affect the next command
    ser.write("\r\n".encode('ascii'))

    #####

    sleep(2)
    # formating arguments
    args = ''.join([args+' \r\n'])
    #encoding arguments
    ser.write(args.encode('ascii'))
    sleep(2)
    # clearing output buffer
    ser.reset_output_buffer()
    return 

def format_output(output):
    """ 
    formats output to remove newlines and prompt.
    Accepts a str object as arg. Also adds posix time at index 0. Returns a list.

    """
    #removing newline and other whitespace char
    output = output.strip()
    #removing prompt. specific to podvu
    output = output.strip("EPU452 Readings")

    return output


def write_to_file(data, filepath):
    """ Takes a list of list as input and writes it to file
    """
    with open(filepath, 'a',newline='') as f:
        wr=csv.writer(f, delimiter=',')
        wr.writerows(data)
        f.close()

def read_data(ser):
    """
    Reads data from device. Accepts a serial device as argument and returns a list which includes all the data for each channel with posix time on index 0.

    """
    try:
        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes.decode()
        output = format_output(decoded_bytes)

        return output

    except:
        ser.close()

        return

def start_acquisition(filepath):
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
            timeout=None, #Waits indefinitely for data to be returned.
            baudrate = 115200,
            bytesize=8,
            parity='N',
            stopbits=1
            )

            for port in ports
    ]


    for serial_obj in ser:
    # setting averaging to period to 0.1 seconds
        write_data(serial_obj, 'set averaging 0.1')
    # setting acquisition rate to 100/s
        write_data(serial_obj, 's 100')
        
    buffer = [] # to save data to file in chunks
    chunk_size=500
    wait_time = 0.01
    
    while True:
        sleep(wait_time)

        #reads data and concatenates with current time
        data = [read_data(serial_obj) for serial_obj in ser]
        # Format:
        # ['7.261632 nA     2.6340 nA      -66.2 nA      Off -', '-118.544 nA     99.959 nA     52.587 nA     21.281 nA']

        time_received = time()

        # iterating over all the strings in the multiple lists of data and splitting at all the spaces. ex. "0.738 nA" -> "0.738","nA". then flattening multiple list into one list which could be written to file.
        data = list(
            itertools.chain(*
            [string.split() if string is not None else '' for string in data]
            )
            )
        # Output format:
        # ['-1.822826', 'nA', '1.6527', 'nA', '-70.4', 'nA', 'Off', '-', '-118.548', 'nA', '99.967', 'nA', '52.572', 'nA', '21.279', 'nA']

        #inserting time into list. Note time need to be a string since write requires string.
        data.insert(0, str(time_received))

        buffer.append(data)

        if len(buffer) == chunk_size:
            write_to_file(buffer,filepath)
            buffer = [] # clears buffer
        else:
            continue
        

    
    for serial_obj in ser:

        serial_obj.close()
    
    
    return
