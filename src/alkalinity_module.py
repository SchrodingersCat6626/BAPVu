import communications
import csv
import fileHandling
import serial
from time import sleep
from time import time
from plotting import remove_every_nth
import pygaps as pg
import pygaps.modelling as pgm
import pandas as pd
import matplotlib.pyplot as plt
import pygaps.graphing as pgg
from math import log10
from math import isclose
from plotting import select

""" Groups of functions used when alkalinity mode is active in BaPvu """

def fit_to_langmuir(file='calibration_data.csv', adsorbate='H+', sensor_material='SWCNT', temp=298):
    """ Takes a file path for calibration data 
    Returns a three site langmuir isotherm fit.
    If it fails to fit to three site langmuir, it will try to guess the model to use for fitting.
    pygaps documentation: https://pygaps.readthedocs.io/en/master/examples/modelling.html
    """

    df = pd.read_csv(file)
    log_concentration = df['pH'].to_list()
    concentration = [10**((-1)*pH) for pH in log_concentration] # convert to molar
    sensor_current = df['sensor_current'].to_list()
    
    try:
        model = pg.ModelIsotherm(
            material=sensor_material,
            adsorbate=adsorbate,
            temperature=temp,
            pressure=concentration,
            loading=sensor_current,
            model='TSLangmuir',
            #optimization_params=dict(max_nfev=1e7),
            verbose=True
            )

    except Exception as e:
        print(e)


    #ax = pgg.plot_iso(
    # model,
    # branch = 'all',
    # color=False
    # )
    # #plt.show()
    return model

def convert_curent_to_pH(sensor_current, isotherm):
    """ Takes in sensor current and converts to pH. Uses langmuir fit of sensor response for a given pH calibration """

    pH = log10(isotherm.pressure_at(loading=sensor_current))*(-1) # to interpolate pH

    return pH


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

def get_channel_current(serial_obj, channel):

    command = 'r'
    communications.write_data(serial_obj, command)

    response = []

    while len(response) != 5: # wait for respones of correct len
        response = communications.read_data(serial_obj) # returns list.
        #Ex. ['Channel' '1', 'Vex', '10.0', 'mV']


    response_cleaned = remove_every_nth(response,2,skip_first_element=False) # removes units
    
    current = response_cleaned[channel-1]


    return current


def autorange_current(serial_obj, old_range, channel, current_voltage, next_voltage):

    available_ranges = [20, 200, 2000, 20000, 200000, 2000000] # nA
    # documentation: https://www.edaq.com/wiki/EPU452_Manual

    # get current for channel.
    current = get_channel_current(serial_obj, channel)

    # get potential 
    # use ohm's law to calculate resistance
    resistance = current_voltage/current
    predicted_next_current = next_voltage/resistance
    # make adjust range if next voltage is over 85% of max of range.
    
    if predicted_next_current > 0.85*old_range:
        new_range = next(x for x in available_ranges if x > predicted_next_current)
        # find to next value within that range.

    command = 'set channel {} range {}'.format(channel,new_range)
    communications.write_data(serial_obj, command)
    
    return new_range


def check_sensor_drift():
    """ Takes sensor data and returns sensor drift in nA/h """


    return



def convert_electrolyzer_current_to_alkalinity():


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


    buffer = []
    
    for serial_obj in ser:
        electrolyzer_setpoint = set_electrolyzer_potential(serial_obj, min_voltage, electrolyzer_channel)
    
    while electrolyzer_setpoint <= max_voltage:

        for serial_obj in ser:
            electrolyzer_setpoint = set_electrolyzer_potential(serial_obj, potential=(electrolyzer_setpoint), channel=electrolyzer_channel)
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

            counter = counter + 1

            if len(buffer) == datapoints_per_potential: # write to file before each potential increment.
                communications.write_to_file(buffer,new_filepath)
                buffer = [] # clears buffer
            else:
                continue
        
        electrolyzer_setpoint = electrolyzer_setpoint+volt_step_size

    for serial_obj in ser:
        serial_obj.close()
    
    print("Sweep complete.")

    return


def titrate(data, electrolyzer_channel, volt_step_size_initial=100, target_pH=4.5, tol=0.1):
    """

    """

    volt_step_size = volt_step_size_initial
    
    while not isclose(mean_pH_of_all_sens, target_pH, abs_tol=tol): # if the pH is not within this tolerance, continue running loop

        if electrolyzer_setpoint >= max_voltage:
            print("Error: Attempting to exceed rated voltage.")
                return

            for serial_obj in ser:
                electrolyzer_setpoint = set_electrolyzer_potential(serial_obj, potential=(electrolyzer_setpoint), channel=electrolyzer_channel)
                communications.write_data(serial_obj, 'i 1')

            counter = 0 # counts the number of lines appended to dictionary

            while counter != datapoints_per_potential: ### change to datapoints for stabilization

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

                counter = counter + 1

                if len(buffer) == datapoints_per_potential: 
                    # calculating current mean pH for the last number of 'datapoint_per_potential' before clearing buffer and writing to file
                    pHs = []
                    for idx, channel in enumerate(sensor_channels):
                        sensor_current_data = select(buffer, index=idx, dtype=float) # need to modify to specify the specific eDAQ.
                        sensor_current_mean = sum(sensor_data)/len(sensor_data)
                        # interpolating pH
                        """
                        Source: https://pygaps.readthedocs.io/en/master/manual/isotherm.html
                        "Interpolation can be dangerous. pyGAPS does not implicitly allow interpolation outside the bounds of the data, 
                        although the user can force it to by passing an interp_fill parameter to the interpolating functions, 
                        usually if the isotherm is known to have reached the maximum adsorption plateau. 
                        Otherwise, the user is responsible for making sure the data is fit for purpose."
                        """
                        pH = convert_curent_to_pH(sensor_current_mean, isomodels[idx])
                        pHs.append(pH)

                    # Update latest current reading
                    electrolyzer_current_data = select(buffer,index=electrolyzer_channel, dtype=float)
                    electrolyzer_current_mean = sum(electrolyzer_current_data)/len(electrolyzer_current_data)

                    communications.write_to_file(buffer,new_filepath) # write to file before incrementing potential and returning to outerloop.
                    buffer = [] # clears buffer
                else:
                    continue

            volt_step_size = volt_step_size*(1.01**(counter*(-1))) # using an exponential decay to decrease step size

            mean_pH_of_all_sens = sum(pHs)/len(pHs) # ensuring all sensors are in agreement

            if mean_pH_of_all_sens > target_pH:
                electrolyzer_setpoint = electrolyzer_setpoint+volt_step_size
            elif mean_pH_of_all_sens < target_pH:
                electrolyzer_setpoint = electrolyzer_setpoint-volt_step_size
            else:
                continue # I guess if this condition is met then we are at 4.5?

        return electrolyzer_current_mean



def alkalinity_test():

    """
    Read values using communication library.
    Take entire chunk.
    Chunksize can be set in alkalinity mode.
    take mean for each channel for a given chunk.
    return this mean as 'data'

    To do:
        I should really be storing titration data as a class.

    """

    # Sensor pH calibration
    # Fits pH data to langmuir 
    # Calibration must be manually performed
    # Could be automated in the future




    ####################################################################################################

    daq_num=1
    dev_channel_num = 4
    data_expected_per_channel = 2 # number or 'off' and a unit.
    data_len_per_device = dev_channel_num*data_expected_per_channel
    expected_rowsize = data_len_per_device*daq_num

    datapoints_for_stabilization = 1*time_per_step # since each step is 1 second


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


    buffer = []

    #########################################################################################################################

    # Titrate a solution of known alkalinity to get initial total alkalinity

    print("Please replace solution with a solution of standard alkalinity.")
    print("Before proceeding, ensure that the solution has fully primed the tubing and the sensors have been conditionned.")

    while True:
        anwser = input("Are you ready to proceed(y/n): ")
        if anwser == y:
            break
        elif anwser == n:
            return (print("Cancelling..."))
        else:
            print("Please enter valid input.")

    print("Measuring sensor drift.")
    print("Please wait...")

    # start data acquisition

    for serial_obj in ser:
        electrolyzer_setpoint = set_electrolyzer_potential(serial_obj, 0, channel=electrolyzer_channel) # setting electrolyzer to 0mV
        communications.write_data(serial_obj, 'i 1')

    # Checking drift

    #while counter != datapoints_for_stabilization:
        
    #    sleep(1)
    #    data = []
    #    
    #    for serial_obj in ser:
    #        new_data = communications.read_data(serial_obj)
    #        data.extend(new_data)
        
    #    if len(data) != expected_rowsize:
    #        print('Warning: Unexpected row size. Row discarded.')
    #        continue

    #    time_received = time()
    #    data.insert(0, str(time_received))
    #    data.extend([str(electrolyzer_setpoint),'mV'])

    #    buffer.append(data)

    #    counter = counter + 1

    #    if len(buffer) == datapoints_per_potential: # write to file before each potential increment.
    #        communications.write_to_file(buffer,new_filepath)
    #        buffer = [] # clears buffer
    #    else:
    #        continue

    #drift = check_sensor_drift(buffer)

    #print("Drift (nA/h): {}".format(drift))
    #input("Would you like to proceed? (y/n): ")

    volt_step_size = 100
    list_of_sensor_channels = [1,2,3]
    # Storing the calibration data for each sensor
    """
    To do: Need to update file format to handle multiple sensors
    The code below will not work in its current form.
    """
    isomodels = [fit_to_langmuir(channel) for channel in list_of_sensor_channels] # All args left as default, reads data from file in root of program.

    init_electrolyzer_current = titrate()

    while True:

        new_electrolyzer_current = titrate()

        diff = init_electrolyzer_current

        while counter != datapoints_for_stabilization:
           
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
        
            counter = counter + 1
        
            if len(buffer) == datapoints_per_potential: # write to file before each potential increment.
                communications.write_to_file(buffer,new_filepath)
                buffer = [] # clears buffer
            else:
                continue

    for serial_obj in ser:
        serial_obj.close()


        return 0 # if successfully completed. Set to return 1 if error since it shouldn't block the main process if it fails for some reason.
