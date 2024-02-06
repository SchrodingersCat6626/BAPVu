#!/usr/bin/python3 
import serial
import serial.tools.list_ports
from time import sleep
from time import time
import itertools
import csv

"""
To do:

    - add basic features.
    - Channel names should be default to number of channels and there should be a funct to name channels.
    - Need to add exception if x number of rows have been discarded (I should try to reset DAQ if that happens.)
    - If it can't find devices anymore it should throw error or get rid of unresponding eDAQ or if none are responding then throw error.
    - Add threading to reading serial ports.

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
    output = output.split()
    #removing prompt. specific to podvu
    try:
        output.remove("EPU452")
        output.remove("Readings")
    except:
        pass


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
        write_data(serial_obj, 'i 1')
        
    buffer = [] # to save data to file in chunks
    chunk_size=30
    wait_time = 1
    daq_num = len(get_com_ports())
    dev_channel_num = 4
    data_expected_per_channel = 2 # number or 'off' and a unit.
    data_len_per_device = dev_channel_num*data_expected_per_channel
    expected_rowsize = data_len_per_device*daq_num
    
    while True:
        sleep(wait_time)

        data = []
        for serial_obj in ser:
            new_data = read_data(serial_obj)
            data.extend(new_data)

        #reads data and concatenates with current time
        #data = [read_data(serial_obj) for serial_obj in ser]
        # Format:
        # ['7.261632 nA     2.6340 nA      -66.2 nA       Off -', '-118.544 nA     99.959 nA     52.587 nA     21.281 nA']

        #if len(data) != daq_num:
        #    print('Warning: Data not received for one or more DAQ devices. Discarding datapoint.')
        #    continue

        time_received = time()

        if len(data) != expected_rowsize:
            print('Warning: Unexpected row size. Row discarded.')
            continue

        data.insert(0, str(time_received))

        print(data)

        buffer.append(data)

        if len(buffer) == chunk_size:
            write_to_file(buffer,filepath)
            buffer = [] # clears buffer
        else:
            continue
        

    
    for serial_obj in ser:

        serial_obj.close()
    
    
    return

start_acquisition("test_data_bug.txt")