import importlib.util
import communications
import csv
import fileHandling
import serial
import pygaps as pg
import pygaps.modelling as pgm
import pandas as pd
import matplotlib.pyplot as plt
import pygaps.graphing as pgg
from time import sleep
from time import time
from plotting import remove_every_nth
from math import log10
from math import isclose
from plotting import select
from scipy.stats import linregress
from simple_pid import PID
from time import sleep
from os.path import exists
from plotting import readNewChunk
from plotting import decode_chunk
from plotting import select
from statistics import fmean
from plotting import remove_every_nth
from numpy import poly1d
from numpy import polyfit

""" Groups of functions used when alkalinity mode is active in BaPvu 

To do: 
- remove regeneration of object appearing multiple times. For example, the list of serial objects. Some variables can be declared as global.
- Implement autoranging
- Clean code up.

- Refactor code. Use functions like open all ports

"""

def fit_to_langmuir(channel, file='calibration_data.csv', adsorbate='H+', sensor_material='SWCNT', temp=298, plot=False):
    """ Takes a file path for calibration data 
    Returns a three site langmuir isotherm fit.
    If it fails to fit to three site langmuir, it will try to guess the model to use for fitting.
    pygaps documentation: https://pygaps.readthedocs.io/en/master/examples/modelling.html
    """

    df = pd.read_csv(file)
    log_concentration = df['pH'].to_list()
    concentration = [10**((-1)*pH) for pH in log_concentration] # convert to molar
    sensor_current = df['sensor_current{}'.format(channel)].to_list()
    
    try:

        x, y = concentration, sensor_current
        model = linregress(x=x, y=y)
        print(model)



        #model = pg.ModelIsotherm(
        #    material=sensor_material,
        #    adsorbate=adsorbate,
        #    temperature=temp,
        #    pressure=concentration,
        #    loading=sensor_current,
        #    model='TemkinApprox',
        #    optimization_params=dict(max_nfev=1e7),
        #    verbose=True
        #    )

    except Exception as e:
        print(e)

    #if plot is True:

    #    ax = pgg.plot_iso(
    #    model,
    #    branch = 'all',
    #    color=False
    #    )
    # 
    #    plt.show()

    return model


def convert_curent_to_pH(sensor_current, isotherm, use_lm = False):
    """ Takes in sensor current and converts to pH. Uses langmuir fit of sensor response for a given pH calibration """
    try:
        if use_lm is False:
            pH = log10(isotherm.pressure_at(loading=sensor_current))*(-1) # to interpolate pH
        elif use_lm is True:
            pH = log10((sensor_current-isotherm.intercept)/isotherm.slope)*(-1)
        
        else:
            print('Invalid argument for use_lm.')
            return

    except ValueError:
        print('The pH cannot be computed for one of the sensors.')
        print('Skipped.')
        return None

    return pH


def set_electrolyzer_potential(serial_obj, potential, channel, beep=True, close_port=False):
    """ Potential in milivolt 
    Note: setting potential will end data acquision.
    Returns electrolyzer potential.
    """

    # beep to indicate that potential has been set
    if beep is True:
        communications.write_data(serial_obj, 'beep')

    command = 'set channel {} Vex {}'.format(channel,potential)
    communications.write_data(serial_obj, command)

    response = []

    while len(response) != 5: # wait for respones of correct len
        response = communications.read_data(serial_obj) # returns list.
        #Ex. ['Channel' '1', 'Vex', '10.0', 'mV']

    new_potential = float(response[3])

    if close_port is True:
        serial_obj.close()

    return new_potential

def get_channel_current(serial_obj, channel, close_port=False) -> float:
    
    serial_obj.flush()
    serial_obj.reset_output_buffer() # discarding data in output buffer to get most recent reading.
    serial_obj.reset_input_buffer()
    command = 'r'
    communications.write_data(serial_obj, command)

    response = []

    while len(response) != 8: # wait for respones of correct len
        response = communications.read_data(serial_obj) # returns list.
        #Ex. ['ch1', 'units', 'ch2', 'units', 'ch3', 'units', 'ch4', 'units']


    response_cleaned = remove_every_nth(response,2,skip_first_element=False) # removes units
    
    current = response_cleaned[channel-1]

    if close_port is True:
        serial_obj.close()


    return float(current)

def get_channel_voltage(serial_obj, channel, close_port=False) -> float:
    
    serial_obj.flush()
    serial_obj.reset_output_buffer() # discarding data in output buffer to get most recent reading.
    serial_obj.reset_input_buffer()
    command = 'get channel {} Vex'.format(channel)
    communications.write_data(serial_obj, command)

    response = []
    
    while len(response) != 5: # wait for respones of correct len
        response = communications.read_data(serial_obj) # returns list

        try:
            response.remove('EPU452>')
        except ValueError:
            continue
    
    voltage = response[3]

    if close_port is True:
        serial_obj.close()


    return float(voltage)


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

def conv_current_to_protons(current,flow_rate):
    """ Function which takes in electrolyzer current in amps and flow_rate (ml/min) as args. Returns change in proton concentration. """

    coulomb_conv_fact = 6.24150975*(10**18) # to electron per coulomb
    avogadro_num = 6.022141527*(10**23)

    flow_rate = flow_rate/1000 # to convert ml/min to L/min

    flow_rate = flow_rate/60 # convert L/min to L/sec
    
    conc_protons = ((current*coulomb_conv_fact)/(flow_rate*avogadro_num)) # ((C/s)(-e/C)((atoms)/e))/((L/s)(atoms/mol)) = moles/L = M

    return conc_protons ## In molars

def conv_protons_to_current(protons,flow_rate):
    """ Function takes in a change in proton concentration at the sensor and flow rate. Solves for change in current to generate change in proton concentration. """

    coulomb_conv_fact = 6.24150975*(10**18) # to electron per coulomb
    avogadro_num = 6.022141527*(10**23)

    flow_rate = flow_rate/1000 # to convert ml/min to L/min

    flow_rate = flow_rate/60 # convert L/min to L/sec
    
    current = (protons*flow_rate*avogadro_num)/coulomb_conv_fact # Ampere = (C/s) = (moles/L*((L/s)(atoms/mol)))/((-e/C)((atoms)/e))
    current_nA = current*10**(9) ## nano ampere

    return current_nA


def find_closest_index(lst, target):

    return min(range(len(lst)), key=lambda i: abs(lst[i] - target))


def predict_voltage(targetCurrent, LinregressResult):
    """ Accepts LinregressResult instance (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html#scipy.stats.linregress).
    Uses the regression to predict the voltage required to reach a setpoint current to speed up titrations. It is assumed that the relationship between electrolyser
    current and voltage are approximately linear beyond the ~1.3V max redox potential for water electrolysis. Regression can be obtained from
    a quick voltage sweep (funct. 'voltage_sweep') with the return calibration set to True.
    """
    voltage = (targetCurrent-LinregressResult.intercept)/LinregressResult.slope

    return voltage


def convert_electrolyzer_current_to_alkalinity():
    """ The change in concentration of protons is approximately equal to the change in alkalinity.
    This function takes the change in proton concentration in the form of change in pH
    """

    return


def voltage_sweep(serial_obj, filepath, fieldnames, electrolyzer_channel, min_voltage, max_voltage, volt_step_size, volt_limit, time_per_step, return_calibration=False, close_port=True):
    """ Sweeps electrolyzer voltage and records voltage, current and time in a separate file
    This data can be combined with sensing data to examine the relationship between electrolyzer current/voltage and pH.
    The pH can be calibrated separately.
    Time_per_step in seconds. If return calibration is set to true, the data is not saved to file. Rather, it returns the electrolyzer calibration. 
    Requires serial_obj containing the electrolyzer.
    """

    # daq num represents the index of eDAQ where the electrolyser is found.

    dev_channel_num = 4
    data_expected_per_channel = 2 # number or 'off' and a unit.
    data_len_per_device = dev_channel_num*data_expected_per_channel
    expected_rowsize = data_len_per_device # only accepts one serial obj.

    datapoints_per_potential = 1*time_per_step # since each step is 1 second

    if return_calibration is False:
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
    #ser = [
    #        serial.Serial(
    #        port = port,
    #        timeout=None, #Waits indefinitely for data to be returned.
    #        baudrate = 115200,
    #        bytesize=8,
    #        parity='N',
    #        stopbits=1
    #        )

    #        for port in ports
    #]
    #ser = [serial_obj] # temp fix


    buffer = []
    
    electrolyzer_setpoint = set_electrolyzer_potential(serial_obj, min_voltage, electrolyzer_channel)
    
    while electrolyzer_setpoint <= max_voltage:

        electrolyzer_setpoint = set_electrolyzer_potential(serial_obj, potential=(electrolyzer_setpoint), channel=electrolyzer_channel)
        communications.write_data(serial_obj, 'i 1')
        
        counter = 0 # counts the number of lines appended to dictionary
        
        while counter != datapoints_per_potential:
            
            sleep(1)
            data = []
            
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

            if return_calibration is True:
                continue
            elif len(buffer) == datapoints_per_potential and return_calibration is False: # write to file before each potential increment.
                communications.write_to_file(buffer,new_filepath)
                buffer = [] # clears buffer
            else:
                continue
        
        electrolyzer_setpoint = electrolyzer_setpoint+volt_step_size

    if return_calibration is True:
        """ Assuming that relationship between voltage and current is linear after 1.3V (about the max redox pot. for water electrolysis) """

        communications.write_to_file(buffer,filepath) # saving calibration data

        new_buff = []
        for line in buffer: 
            new_line = remove_every_nth(line, 2, skip_first_element=True) # removing unit cols for clarity
            new_buff.append(new_line)
        buffer = new_buff
        start_idx = find_closest_index(select(buffer, index=-1, dtype='float'), min_voltage) # The voltage channel in the last column
        x, y = select(buffer,index=-1, dtype='float'), select(buffer, index = (electrolyzer_channel-1)+1, dtype='float') # +1 to compensate for systime col
        x.pop(0) # removing first element as a quick fix
        y.pop(0) # removing first element as a quick fix
        regress = linregress(x=x, y=[log10(abs(element)) for element in y]) # taking the absolute value since sometimes at low voltage, the values are negative
        # need a better fix
        if close_port is True:
            serial_obj.close()
        return regress
    
    print("Sweep complete.")

    return

def voltage_sweep2(filepath, fieldnames, electrolyzer_channel, electrolyser_daq, daq_num, min_voltage, max_voltage, volt_step_size, volt_limit, time_per_step,close_port=True):
    """ Sweeps electrolyzer voltage and records voltage, current and time in a separate file
    This data can be combined with sensing data to examine the relationship between electrolyzer current/voltage and pH.
    The pH can be calibrated separately.
    Time_per_step in seconds. If return calibration is set to true, the data is not saved to file. Rather, it returns the electrolyzer calibration. 
    Requires serial_obj containing the electrolyzer.
    """

    # daq num represents the index of eDAQ where the electrolyser is found.

    dev_channel_num = 4
    data_expected_per_channel = 2 # number or 'off' and a unit.
    data_len_per_device = dev_channel_num*data_expected_per_channel
    expected_rowsize = data_len_per_device*daq_num # only accepts one serial obj.

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

    serial_obj_electrolyzer = ser[electrolyser_daq-1] # temp fix


    buffer = []
    
    electrolyzer_setpoint = set_electrolyzer_potential(serial_obj_electrolyzer, min_voltage, electrolyzer_channel)
    
    while electrolyzer_setpoint <= max_voltage:

        electrolyzer_setpoint = set_electrolyzer_potential(serial_obj_electrolyzer, potential=(electrolyzer_setpoint), channel=electrolyzer_channel)
        for serial_obj in ser:
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
    if close_port is True:
        for serial_obj in ser:
            serial_obj.close()
    
    print("Sweep complete.")

    return



def titrate(serial_obj, pid, electrolyzer_channel, electrolyzer_state, current_setpoint, LinregressResult,
buffer=None, tol=1, stabilization_time = 15, max_voltage=2000, close_port=False, debug_pid=False) -> list: 
# 1 datapoint = 1 second
    """ 
    returns updated electrolyzer state as dictionary.
    Expect the linear model to be log(y)
    """
    # Temp fix for debugging
    daq_num=1
    dev_channel_num = 4
    data_expected_per_channel = 2 # number or 'off' and a unit.
    data_len_per_device = dev_channel_num*data_expected_per_channel
    expected_rowsize = data_len_per_device*daq_num
    ###############################

    expected_rowsize = data_len_per_device*daq_num
    current = electrolyzer_state['current']
    starting_volt=electrolyzer_state['voltage']


    if current == current_setpoint:
        return [electrolyzer_state,pid]

    voltage_setpoint = starting_volt

    pid.setpoint = current_setpoint
    pid.output_limits = [-current_setpoint,200000]

    delta_current = pid(current) # computes new current adjustment

    buffer = []
    
    overall_count = 0

    while not isclose(current, current_setpoint, abs_tol=tol): 

        if voltage_setpoint > max_voltage:
            print("Error: Attempting to exceed rated voltage.")
            return

        print(current)

        delta_current = pid(current) # computes new current adjustment

        print('delta_current: {}'.format(delta_current))

        pid.output_limits = [-current,200000]

        try:

            next_target_current = current+delta_current
            
            print('new target current: {}'.format(next_target_current))

            log_next_target_current = log10(next_target_current)

            print('log new target current: {}'.format(log_next_target_current))

            voltage_setpoint = round(
                predict_voltage(log_next_target_current, LinregressResult),1) # in mV, rounds to 1 decimal point since that is the most precision available in eDAQ

            print('next voltage setpoint determined to be: {} mV'.format(voltage_setpoint))

            voltage = set_electrolyzer_potential(serial_obj, potential=voltage_setpoint, channel=electrolyzer_channel, beep=False, close_port=False)
            communications.write_data(serial_obj, 'i 1')

        except ValueError:

            print('ValueError')


        counter = 0 # counts the number of lines appended to dictionary

        if overall_count == 0:

            while counter != 3: ### change to datapoints for stabilization

                sleep(1)

                data = []

                new_data = communications.read_data(serial_obj)
                data.extend(new_data)

                if len(data) != expected_rowsize:
                    print('Warning: Unexpected row size. Row discarded.')
                    continue

                #time_received = time()
                #data.insert(0, str(time_received))
                #data.extend([str(electrolyzer_setpoint),'mV'])

                data = remove_every_nth(data,2,skip_first_element=False)
                buffer.append(data)

                counter = counter + 1

                current = float(buffer[-1][electrolyzer_channel-1]) # getting new_current of electrolyser #10 nA of tolerance

                if debug_pid is True:
                    print('Current: {}nA'.format(current))


                if counter==stabilization_time:
                    buffer = [] # clears buffer

        else:

            while counter != stabilization_time: ### change to datapoints for stabilization

                sleep(1)

                data = []

                new_data = communications.read_data(serial_obj)
                data.extend(new_data)

                if len(data) != expected_rowsize:
                    print('Warning: Unexpected row size. Row discarded.')
                    continue

                #time_received = time()
                #data.insert(0, str(time_received))
                #data.extend([str(electrolyzer_setpoint),'mV'])

                data = remove_every_nth(data,2,skip_first_element=False)
                buffer.append(data)

                counter = counter + 1

                lst_of_currents = select(buffer,index=electrolyzer_channel-1,dtype='float')

                current = fmean(lst_of_currents)
                #current = float(buffer[-1][electrolyzer_channel-1]) # getting new_current of electrolyser #10 nA of tolerance

                if debug_pid is True:
                    print('Current: {}nA'.format(current))


                if counter==stabilization_time:
                    buffer = [] # clears buffer

                ### change to update dict object, rather than create a new one.

        overall_count = overall_count+1


    if close_port is True:
        serial_obj.close()

    try:

        new_electrolyzer_state = {'current':current,'voltage':voltage}
        
        return [new_electrolyzer_state,pid]

    except UnboundLocalError:

        print('Current is already equal to current setpoint!')
        return [electrolyzer_state, pid]



def alkalinity_test(filepath, fieldnames, electrolyzer_channel, electrolyser_daq, list_of_sensor_channels, flow_rate, plot_calibration=False, skip_initial_stabilization=False,
datapoints_for_stabilization=1200, starting_volt=800, volt_step_size_initial=100, target_pH=4.5, tol=0.1, max_voltage=2000):

    """
    Read values using communication library.
    Take entire chunk.
    Chunksize can be set in alkalinity mode.
    take mean for each channel for a given chunk.
    return this mean as 'data'

    """

    volt_limit = max_voltage

    daq_num=2
    dev_channel_num = 4
    data_expected_per_channel = 2 # number or 'off' and a unit.
    data_len_per_device = dev_channel_num*data_expected_per_channel
    expected_rowsize = data_len_per_device*daq_num

    #list_of_sensor_channels = [idx-1 for idx in list_of_sensor_channels] # converting sensors channels to index numbers


    new_filepath = filepath+"_titration.csv" ### change filename to include sweep
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

    serial_obj_electrolyzer = ser[electrolyser_daq-1] # selecting serial object containing electrolysis


    buffer = []

    #########################################################################################################################

    # Titrate a solution of known alkalinity to get initial total alkalinity

    print("Please replace solution with a solution of standard alkalinity.")
    print("Before proceeding, ensure that the solution has fully primed the tubing and the sensors have been conditionned.")

    while True:
        anwser = input("Are you ready to proceed(y/n): ")
        if anwser == 'y':
            break
        elif anwser == 'n':
            return (print("Cancelling..."))
        else:
            print("Please enter valid input.")

    #print("Measuring sensor drift.")
    #print("Please wait...")

    #drift = check_sensor_drift(buffer)

    #print("Drift (nA/h): {}".format(drift))
    #input("Would you like to proceed? (y/n): ")

    # Storing the calibration data for each sensor

    isomodels = [fit_to_langmuir(channel, plot=plot_calibration) for channel in list_of_sensor_channels] # All args left as default, reads data from file in root of program.

    ################################ Calibrate electrode current response ########################
    # This will be used to recompute the new voltage target to achieve a current setpoint.
    # More accurate than using ohms law.
    print("Calibrating electrolyzer current response.")
    print("Please wait...")
    electrolyzer_response = voltage_sweep(serial_obj=serial_obj_electrolyzer, filepath=None, fieldnames=['systime','ch1','units', 'ch2','units', 'ch3','units', 'ch4','units'], # temporary fix
    electrolyzer_channel=3, min_voltage=1000,max_voltage=1250, volt_step_size=50,
    time_per_step=15, volt_limit=2000,
    return_calibration=True, close_port=False) # since return calibration is True, this will return a regression.
    print("Electrolyzer calibration complete!")
    input('Discharge electrolyzer by shorting. Once complete press enter.')
    ##############################################################################################

    for serial_obj in ser:
        serial_obj.close()

    input('Adjust current range to optimal range in MFconfig')

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

    serial_obj_electrolyzer = ser[electrolyser_daq-1] # selecting serial object containing electrolysis

    print('setting electrolyser potential to back to 0 mV.')
    voltage = set_electrolyzer_potential(serial_obj_electrolyzer, potential=0, channel=electrolyzer_channel, beep=True, close_port=False)
    print('Success!')

    current = get_channel_current(serial_obj_electrolyzer, electrolyzer_channel)
    print('Waiting for current from residual voltage to subside.')
    sleep(30)
    electrolyzer_state = {'voltage':voltage, 'current':current}
    print("Voltage setpoint found to be {}mV, and current to be {}nA".format(electrolyzer_state['voltage'], electrolyzer_state['current']))
    print('Initial electrolyser state recorded.')


    num_loops = 0

    while True:
        
        #### Set enough current by default to titrate 1000 AT to get to pH get to pH 3.

        counter = 0
        if num_loops == 0:
            if skip_initial_stabilization is True:
                counter = datapoints_for_stabilization-3 # allowing to do at least 3 cycles for mean.

        num_loops = num_loops + 1
        
        for serial_obj in ser:
            communications.write_data(serial_obj, 'i 1')
        
        print('Started data acquisition.')

        while counter != datapoints_for_stabilization:
            #### I need to measure pH in this loop and check if it changed.
            ### If it changed, I should interpolate the pH and use the current difference from the initial titration to set the starting point of the new titration.

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
            data.extend([str(electrolyzer_state['voltage']),'mV'])
        
            buffer.append(data)
        
            counter = counter + 1

            print('Data: {}'.format(data))

            print('Iteration count: {}'.format(counter))
        
            if len(buffer) == datapoints_for_stabilization: # write to file before each potential increment.

                print('computing diff pH...')

                new_buff = []
                for line in buffer: 
                    new_line = remove_every_nth(line, 2, skip_first_element=True) # removing unit cols for clarity
                    new_buff.append(new_line)

                    latest_electrolyzer_current = float(buffer[-1][electrolyzer_channel+(dev_channel_num*(electrolyser_daq-1))]) # to compute the idx number regardless of edaq num

                electrolyzer_state.update({'current':latest_electrolyzer_current})

                pHs = []
                # calculating current mean pH for the last 120 datapoints
                for idx, channel in enumerate(list_of_sensor_channels): # cannot deal with more than one eDAQ
                    sensor_current_data = select(new_buff, index=channel, dtype='float') # Since there is a time column, it is not required ot substract 1 to get index.
                    sensor_current_data = sensor_current_data[-120:] # selecting the last 2 mins of data
                    sensor_current_mean = sum(sensor_current_data)/len(sensor_current_data)
                    # interpolating pH
                    """
                    Source: https://pygaps.readthedocs.io/en/master/manual/isotherm.html
                    "Interpolation can be dangerous. pyGAPS does not implicitly allow interpolation outside the bounds of the data, 
                    although the user can force it to by passing an interp_fill parameter to the interpolating functions, 
                    usually if the isotherm is known to have reached the maximum adsorption plateau. 
                    Otherwise, the user is responsible for making sure the data is fit for purpose."
                    """
                    print('Mean current for channel {} found to be {}'.format(channel, sensor_current_mean))
                    pH = convert_curent_to_pH(sensor_current_mean, isomodels[idx], use_lm=True)
                    if pH is None:
                        continue
                    pHs.append(pH)


                mean_pH = sum(pHs)/len(pHs) # computing the mean of sensor pH for acidic side.

                print('Mean pH calculated to be {}'.format(mean_pH))

                communications.write_to_file(buffer,new_filepath)

                buffer = [] # clears buffer
                
                if not isclose(mean_pH, 4, abs_tol=tol):

                    # calculate difference in protons
                    # calculate how much current is needed to return to pH 4.5
                    delta_current = conv_protons_to_current((10**(-4.5))-(10**(-mean_pH)), flow_rate)
                    print('delta current is {}'.format(delta_current))
                    new_current_target = electrolyzer_state['current'] + delta_current

                    print('New electrolyser current target is: {}nA'.format(new_current_target))
                    
                    print("Performing initial pH titration with electrolyser.")
                    print("Titrating to pH 4.5.")
                    print("Please wait...")

                    electrolyzer_state = titrate(serial_obj=serial_obj_electrolyzer, electrolyzer_channel=electrolyzer_channel, electrolyzer_state=electrolyzer_state,
                     current_setpoint=new_current_target, LinregressResult=electrolyzer_response, max_voltage=2000, debug_pid=True)

                    print("Titration complete!")
                    print("Voltage setpoint found to be {}mV, and current to be {}nA".format(electrolyzer_state['voltage'], electrolyzer_state['current']))

            else:
                continue

    for serial_obj in ser:
        serial_obj.close()


        return 0

def open_all_ports() -> list:
    ports = communications.get_com_ports()
    ser = [
            serial.Serial(
            port = port,
            timeout=None, #Waits indefinitely for data to be returned.
            baudrate = 115200,
            bytesize=8,
            parity='N',
            stopbits=1)
        
        for port in ports
        ]

    return ser


#def read_data_while_stabilizing(serial_obj:list, filename:str, ) -> str:


def titration_test(filename: str, fieldnames: list, currentTargets: list, repeats: int, 
electrolyser_daq: int, electrolyzer_channel: int, daq_num:int, # number of daq's available in total.
datapoints_for_stabilization:int, volt_limit=2000, tolerance=20 #nA
) -> None:
    """ Evaluates ability to reach current targets. Can be used to change between pHs.
    """
    print('Note: the program currently assumes the electrolyser is at the same location that it was during the calibration.')
    
    dev_channel_num = 4 # number of channels per device

    ser = open_all_ports()
    
    serial_obj_electrolyzer = ser[electrolyser_daq-1] # selecting serial object containing electrolysis

    electrolyser_idx = electrolyzer_channel+(dev_channel_num*(electrolyser_daq-1))
    print(electrolyser_idx)
    # getting index of electrolyser column
    # since index 0 is systime, this math works out
    # ex. if electrolyser is channel 4 on daq 1, this equals to index of 4. (idx 0 being systime)
    # This also assumes that the unit column is removed.

    dev_channel_num = 4
    data_expected_per_channel = 2 # number or 'off' and a unit.
    data_len_per_device = dev_channel_num*data_expected_per_channel
    expected_rowsize = data_len_per_device*daq_num
    
    from simple_pid import PID
    pid = PID(
        1.25, #Kp, proportionality constant
        0.2, # weight of integral term
        0.1 #kd weight of derivative term
        ) # initializing PID
        # https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller#:~:text=A%20proportional%E2%80%93integral%E2%80%93derivative%20controller%20%28PID%20controller%20or%20three-term%20controller%29,variety%20of%20other%20applications%20requiring%20continuously%20modulated%20control.

    repeat_counter = 0

    #print('Setting voltage to 0 mV.')
    #voltage = set_electrolyzer_potential(serial_obj_electrolyzer, potential=0, 
    #channel=electrolyzer_channel, beep=True, close_port=False) # should return current

    voltage = get_channel_voltage(serial_obj=serial_obj_electrolyzer,channel=electrolyzer_channel,close_port=False)
    print('Voltage left at {}mV'.format(voltage))

    print('Reading initial current')
    # read current
    initial_current = get_channel_current(serial_obj=serial_obj_electrolyzer,channel=electrolyzer_channel,close_port=False)

    # recording initial electrolyser state
    electrolyser_state = {'current':initial_current, 'voltage':voltage}

    if not exists('latest_electrolyser_calibration'):

        print('Could not find past calibration.')

        print('Calibrating electrolyser.')
        print('This may take a while.')
    
        electrolyzer_response = voltage_sweep(serial_obj=serial_obj_electrolyzer, filepath='latest_electrolyser_calibration', 
        fieldnames=fieldnames, 
        electrolyzer_channel=electrolyzer_channel,
        min_voltage=600,max_voltage=volt_limit, volt_step_size=1,
        time_per_step=7, volt_limit=volt_limit,
        return_calibration=True) # since return calibration is True, this will return a regression.

    else:
        print('Previous electrolyser calibration found.')
        response = input('Would you like to load this calibration (y/n)? ')
    
        if response.lower() == 'n':

            print('Calibrating electrolyser.')
            print('This may take a while.')

            electrolyzer_response = voltage_sweep(serial_obj=serial_obj_electrolyzer, filepath='latest_electrolyser_calibration', 
            fieldnames=fieldnames, 
            electrolyzer_channel=electrolyzer_channel,
            min_voltage=600,max_voltage=volt_limit, volt_step_size=1,
            time_per_step=7, volt_limit=volt_limit,
            return_calibration=True) # since return calibration is True, this will return a regression. # changed to log calibration. should add argument for this

        elif response == 'y':

            electrolyzer_calibration = readNewChunk('latest_electrolyser_calibration')
            electrolyzer_calibration = decode_chunk(electrolyzer_calibration,nth=2) # removing unit cols. skips first col by defau
            

            electrolyser_currents = select(lstOfLsts=electrolyzer_calibration,index=electrolyser_idx,dtype='float')
            electrolyser_voltages = select(lstOfLsts=electrolyzer_calibration,index=-1,dtype='float')

            electrolyser_currents.pop(0) # removing first element as a quick fix
            electrolyser_voltages.pop(0) # removing first element as a quick fix

            ## remove column titles! otherwise math error.

            #electrolyzer_response = np.poly1d(np.polyfit(electrolyser_voltages, electrolyser_currents, 9))
            electrolyzer_response = linregress(x=electrolyser_voltages, y=[log10(abs(y)) for y in electrolyser_currents]) # change to appropriate regression
            # set to abs(y) since at very low values the current can be 'negative'. This is due to not autoranging during calibration and otherwise
            # needs a better fix.
            print('Information from loaded model: {}'.format(electrolyzer_response))

        
        else:
            print('invalid input.')
            return

    while repeat_counter != repeats:

        for current in currentTargets:

            pid.setpoint = current # changing setpoint to new current target
            pid.output_limits = [-current,200000] # limits the pid calcs. to -current to max limit of range (in this case 200000nA) 

            print('Current setpoint set to: {} nA'.format(current))

            counter = 0

            buffer = []

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
                data.extend([str(electrolyser_state['voltage']),'mV'])

                buffer.append(data)

                print('Data: {}'.format(data))

                print('Iteration count: {}'.format(counter))


                data_no_units = remove_every_nth(data, n=2,skip_first_element=True)
                latest_electrolyzer_current = float(data_no_units[electrolyser_idx]) # to compute the idx number regardless of edaq num

                electrolyser_state.update({'current':latest_electrolyzer_current})
                    
                try:
                    
                    next_target_current = current+delta_current
                    
                    print('new target current: {}'.format(next_target_current))

                    log_next_target_current = log10(next_target_current)

                    print('log new target current: {}'.format(log_next_target_current))

                    voltage_setpoint = round(
                        predict_voltage(log_next_target_current,electrolyzer_response),
                        1) # in mV, rounds to 1 decimal point since that is the most precision available in eDAQ

                    if voltage_setpoint <= volt_limit:

                        print('next voltage setpoint determined to be: {} mV'.format(voltage_setpoint))

                        electrolyser_state.update({'voltage':voltage_setpoint})

                        voltage = set_electrolyzer_potential(
                            serial_obj_electrolyzer, potential=voltage_setpoint, 
                            channel=electrolyzer_channel, beep=False, close_port=False)

                    else: 
                        print('Error: attempting to exceed rated voltage!')
                        print('Voltage not changed.')

                    for ser in serial_obj:
                        communications.write_data(serial_obj, 'i 1')


                except ValueError:

                    print('ValueError')
        
                counter = counter + 1

            
                if len(buffer) == datapoints_for_stabilization: # write to file before each potential increment.

                    communications.write_to_file(buffer,filename)

                    buffer = [] # clears buffer
                
        repeat_counter = repeat_counter+1 # incrementing repeats

    for serial_obj in ser:
        serial_obj.close()

    return