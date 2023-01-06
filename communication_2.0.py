#!/home/thomas/Dropbox/B.A.Vu/.venv/bin/python3

import csv 
import serial.tools.list_ports
from time import sleep

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
    """for some reason (i think it is hardware), one of the edaqs won't read at 10/s. This is the same edaq
with the different firmware (the one from the other lab). The problem seems to go away when I set rate at 10 on edaq and only read every 1 second (will the buffer overflow?)
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
    Accepts a str object as arg. Returns a list.

    """
    #removing newline and other whitespace char
    output = output.strip()
    #removing prompt. specific to podvu
    output = output.strip("EPU452 Readings") 

    return output

# Reading a list of com ports
ports = get_com_ports()


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
    #write_data(serial_obj, 'beep')
    write_data(serial_obj, 'set c 1 func bio')
    write_data(serial_obj, 'set c 2 func bio')
    write_data(serial_obj, 'set c 3 func bio')
    write_data(serial_obj, 'set c 4 func bio')
    write_data(serial_obj, 'set channel 1 Vex 10')
    write_data(serial_obj, 'set channel 2 Vex 10')
    write_data(serial_obj, 'set channel 3 Vex 10')
    write_data(serial_obj, 'set channel 4 Vex 10')
    write_data(serial_obj, 's 10')

while True:

    # to do this more efficiently and simultaneously, I should acquire raw data in a list comprehension quickly. use the output_formatting function to format the data once it is saved in the list. Basically do what I did below and simplify the read_data function to only get the bytes.
    data = [read_data(serial_obj) for serial_obj in ser]
    print(data)
    sleep(0.1)
mobile = [['samsung'], [5], ['oneplus !']] 
file = open('f6.csv', 'w+', newline ='') 
with file:     
    write = csv.writer(file) 
    write.writerows(mobile) 
file.close()
