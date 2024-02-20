import communications
import csv
import fileHandling
import serial
from time import sleep
from time import time
#import pygaps.modelling as pgm

""" Groups of functions used when alkalinity mode is active in BaPvu """

def which_electrolyzer():
    """  Reads a config file which has the electrolyzer channel number written on line one """




    return

def which_sensors():
    """  Reads a config file which has the sensor channel number written on line 2 for first eDAQ, line 3 for second eDAQ....etc 
    configuration should be in order of com value. Ex. COM3 will come before COM4 in the file...etc.
     """
    


    return

def read_calibration_table():
    """ calibration should be stored in a file """




    return

def fit_to_langmuir():
    ### https://pygaps.readthedocs.io/en/master/examples/modelling.html
    isotherm = next(i for i in isotherms_H+_298k if i.material == 'CNT')
    try:
        model = pgm.model_iso(
            isotherm,
            model='DSLangmuir',
            verbose=True,
            optimization_params=dict(max_nfev=1e3),
        )
    except Exception as e:
        print(e)





def convert_curent_to_pH():
    """ Takes in sensor current and converts to pH. Uses langmuir fit of sensor response for a given pH calibration """




    return


def set_electrolyzer_potential(serial_obj, potential, channel):
    """ Potential in milivolt 
    Note: setting potential will end data acquision.
    Returns electrolyzer potential.
    """

    # beep to indicate that potential has been set 
    communications.write_data(serial_obj, 'beep')

    command = 'set channel {} Vex {}'.format(channel,potential)
    communications.write_data(serial_obj, command)

    response = []

    while len(response) != 5: # wait for respones of correct len
        response = communications.read_data(serial_obj) # returns list.
        #Ex. ['Channel' '1', 'Vex', '10.0', 'mV']

    new_potential = float(response[3])

    return new_potential


def convert_electrolyzer_current_to_alkalinity():


    return



def storeData():
    """ Will write the alkalinity data in a separate file from the raw data 
    key parameters: 
    - pH according to each sensor.

    """

    return

def compare_pH():
    """ Compares current pH reading to last reading in file 
    Returns true if pH is same (within tolerance)
    Returns flase if pH is different (within tolerance)
    Returns None type if file is empty
    """


    return


def voltage_sweep(filepath, fieldnames, electrolyzer_channel, min_voltage, max_voltage, volt_step_size, volt_limit, time_per_step, daq_num):
    """ Sweeps electrolyzer voltage and records voltage, current and time in a separate file
    This data can be combined with sensing data to examine the relationship between electrolyzer current/voltage and pH.
    The pH can be calibrated separately.
    Time_per_step in seconds.
    """
    daq_num=1
    dev_channel_num = 4
    data_expected_per_channel = 2 # number or 'off' and a unit.
    data_len_per_device = dev_channel_num*data_expected_per_channel
    expected_rowsize = data_len_per_device*daq_num

    datapoints_per_potential = 1*time_per_step # since each step is 1 second


    new_filepath = filepath+"_sweep.csv" ### change filename to include sweep
    new_fieldnames = fieldnames # creating a local copy of fieldnames
    new_fieldnames.append('electrolyzer_potential')
    new_fieldnames.append('unit')
    #### New fields: systime, ch1, ch2, ch3, ch4...etc., electrolyzer_potential
    fileHandling.filecreate(new_filepath, new_fieldnames)

     # Reading a list of com ports
    ports = communications.get_com_ports()

    if len(ports) > 3:
        
        print("Reading more than 3 eDAQ's is currently unsuported!")

        return
    
    if max_voltage > volt_limit:

        print("Error: given voltage range exceeds device limit.")

        return
    
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


    buffer = [] # save buffer as dictionary. All data is written to the file once the sweep is completed.
    
    for serial_obj in ser:
        electrolyzer_setpoint = set_electrolyzer_potential(serial_obj, min_voltage, electrolyzer_channel)
    
    while electrolyzer_setpoint <= max_voltage:

        for serial_obj in ser:
            electrolyzer_setpoint = set_electrolyzer_potential(serial_obj, potential=(electrolyzer_setpoint+volt_step_size), channel=electrolyzer_channel)
            communications.write_data(serial_obj, 'i 1')
        
        counter = 0 # counts the number of lines appended to dictionary
        
        while counter != datapoints_per_potential:
            
            sleep(1)
            data = []
            
            for serial_obj in ser:
                new_data = communications.read_data(serial_obj)
                data.extend(new_data)
                
            if len(data) != expected_rowsize:
                print('Warning: Unexpected row size. Row discarded.')
                continue

            time_received = time()
            data.insert(0, str(time_received))
            data.extend([str(electrolyzer_setpoint),'mV'])

            buffer.append(data)

            print('buffer updated...')
            counter = counter + 1

    for serial_obj in ser:
        serial_obj.close()

    communications.write_to_file(buffer,new_filepath)
    
    print("Sweep complete.")

    return


def alkalinity_test():

    electrolyzer_channel = which_electrolyzer()
    sensor_channels = which_sensors()

    """
    Read values using communication library.
    Take entire chunk.
    Chunksize can be set in alkalinity mode.
    take mean for each channel for a given chunk.
    return this mean as 'data'
    """
    
    data = None

    new_pH = convert_curent_to_pH(data, sensor_channels) # returns a list of pH's for all three sensors on each eDAQ

    if compare_pH(file, new_pH, tolerance) is True:

        storeData()

    elif compare_pH(file, new_pH, tolerance) is False:
        
        while compare_pH(file, new_pH, tolerance) is False:

            set_electrolyzer_potential()

            sleep(time_delay) # should be a delay based on the size of the channel.

        # recalculate alkalinity


    else: ## if None type is returned due to empty file

        storeData()


    return 0 # if successfully completed. Set to return 1 if error since it shouldn't block the main process if it fails for some reason.
