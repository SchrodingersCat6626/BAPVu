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

def conv_current_to_protons(current,flow_rate):
    """ Function which takes in electrolyzer current and flow_rate (L/min) as args. Returns change in proton concentration. """

    coulomb_conv_fact = 6.24150975*(10**18) # to electron per coulomb
    avogadro_num = 6.022141527*(10**23)

    flow_rate = flow_rate/60 # convert L/min to L/sec
    
    conc_protons = ((current*coulomb_conv_fact)/(flow_rate*avogadro_num)) # ((C/s)(-e/C)((atoms)/e))/((L/s)(atoms/mol)) = moles/L = M

    return conc_protons ## In molars

def find_closest_index(lst, target):

    return min(range(len(lst)), key=lambda i: abs(lst[i] - target))


def predict_voltage(targetCurrent, LinregressResult):
    """ Accepts LinregressResult instance (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html#scipy.stats.linregress).
    Uses the regression to predict the voltage required to reach a setpoint current to speed up titrations. It is assumed that the relationship between electrolyser
    current and voltage are approximately linear beyond the ~1.3V max redox potential for water electrolysis. Regression can be obtained from
    a quick voltage sweep (funct. 'voltage_sweep') with the return calibration set to True.
    """
    voltage = (targetCurrent-LinregressResult.yintercept)/LinregressResult.slope

    return voltage


def convert_electrolyzer_current_to_alkalinity():


    return


def voltage_sweep(filepath, fieldnames, electrolyzer_channel, min_voltage, max_voltage, volt_step_size, volt_limit, time_per_step, daq_num, return_calibration=False):
    """ Sweeps electrolyzer voltage and records voltage, current and time in a separate file
    This data can be combined with sensing data to examine the relationship between electrolyzer current/voltage and pH.
    The pH can be calibrated separately.
    Time_per_step in seconds. If return calibration is set to true, the data is not saved to file. Rather, it returns the electrolyzer calibration.
    """
    daq_num=1
    dev_channel_num = 4
    data_expected_per_channel = 2 # number or 'off' and a unit.
    data_len_per_device = dev_channel_num*data_expected_per_channel
    expected_rowsize = data_len_per_device*daq_num

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

            if return_calibration is True: 
                continue
            elif len(buffer) == datapoints_per_potential and return_calibration is False: # write to file before each potential increment.
                communications.write_to_file(buffer,new_filepath)
                buffer = [] # clears buffer
            else:
                continue
        
        electrolyzer_setpoint = electrolyzer_setpoint+volt_step_size

    for serial_obj in ser:
        serial_obj.close()

    if return_calibration is True:
        """ Assuming that relationship between voltage and current is linear after 1.3V (about the max redox pot. for water electrolysis) """
        start_idx = find_closest_index(select(buffer, -1), 1.3) # The voltage channel in the last column
        x, y = select(buffer,0), select(buffer, electrolyzer_channel-1)
        regress = linregress(x=x[start_idx:None], y=y[start_idx:None])
        return regress
    
    print("Sweep complete.")

    return



def titrate(filepath, data, electrolyzer_channel, starting_volt=800, volt_step_size_initial=100, target_pH=4.5, tol=0.1, set_current_first=False, electrolyzer_current_setpoint=None, LinregressResult=None):
    """ Performs a titration. 'starting_volt' arg represents the voltage to start the titration with (mV).
    If 'set_current_first', is set to 'True', the electrolyser current will, first, be adjusted to the setpoint.
    Note: In 'set_current_first' mode, data will not be saved while setting current. Therefore, if the setpoint cannot be reached,
    the program will hang. This mode should be used when setpoint has been computed.
    """


    # The electrolyzer eDAQ needs to ba in a sep. obj than sensors!


    ### Set it to titrate to a current

    volt_step_size = volt_step_size_initial
    electrolyzer_setpoint = starting_volt

    pid = PID(setpoint=electrolyzer_current_setpoint)
    new_current = electrolyzer_current_setpoint # setting initial value

    if set_current_first is True:
        while not isclose(electrolyzer_current, electrolyzer_current_setpoint, abs_tol=10): #10 nA of tolerance
            new_current = pid(new_current) # computes new current adjustment
            new_voltage = predict_voltage(new_current+electrolyzer_current_setpoint, LinregressResult)
            for serial_obj in ser:
                electrolyzer_setpoint = set_electrolyzer_potential(serial_obj, potential=(electrolyzer_setpoint), channel=electrolyzer_channel)
                communications.write_data(serial_obj, 'i 1')


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


                #### If the pH has changed only a small amount. Change decay rate dynamically.

            volt_step_size = volt_step_size*(1.01**(counter*(-1))) # using an exponential decay to decrease step size

            mean_pH_of_all_sens = sum(pHs)/len(pHs) # ensuring all sensors are in agreement

            if mean_pH_of_all_sens > target_pH:
                electrolyzer_setpoint = electrolyzer_setpoint+volt_step_size
            elif mean_pH_of_all_sens < target_pH:
                electrolyzer_setpoint = electrolyzer_setpoint-volt_step_size
            else:
                continue # I guess if this condition is met then we are at 4.5?

            results = {'current': electrolyzer_current_mean, 'voltage': electrolyzer_setpoint}

        return results



def alkalinity_test(filepath, electrolyzer_channel, list_of_sensor_channels = [1,2,3],  starting_volt=800, volt_step_size_initial=100, target_pH=4.5, tol=0.1):

    """
    Read values using communication library.
    Take entire chunk.
    Chunksize can be set in alkalinity mode.
    take mean for each channel for a given chunk.
    return this mean as 'data'

    """

    daq_num=1
    dev_channel_num = 4
    data_expected_per_channel = 2 # number or 'off' and a unit.
    data_len_per_device = dev_channel_num*data_expected_per_channel
    expected_rowsize = data_len_per_device*daq_num

    list_of_sensor_channels = [idx-1 for idx in list_of_sensor_channels] # converting sensors channels to index numbers
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

    #print("Measuring sensor drift.")
    #print("Please wait...")

    #drift = check_sensor_drift(buffer)

    #print("Drift (nA/h): {}".format(drift))
    #input("Would you like to proceed? (y/n): ")

    # Storing the calibration data for each sensor

    isomodels = [fit_to_langmuir(channel) for channel in list_of_sensor_channels] # All args left as default, reads data from file in root of program.

    ################################ Calibrate electrode current response ########################
    # This will be used to recompute the new voltage target to achieve a current setpoint.
    # More accurate than using ohms law.
    print("Calibrating electrolyzer current response.")
    print("Please wait...")
    electrolyzer_response = voltage_sweep(
        filepath=None, fieldnames=new_fieldnames, 
        electrolyzer_channel=electrolyzer_channel,
        min_voltage=1300,max_voltage=1800,
        volt_step_size=1000,time_per_step=60, 
        return_calibration=True # since return calibration is True, this will return a regression.
    )
    print("Electrolyzer calibration complete!")
    ##############################################################################################

    print("Performing initial pH titration with electrolyser.")
    print("Titrating to pH 4.5.")
    print("Please wait...")
    init_electrolyzer_current = titrate() # returns a dict containing electrolyzer current and voltage. Voltage can be used as starting param in next titration
    print("Initial titration complete!")
    print("Voltage setpoint found to be {}mV, and current to be {}nA".format(init_electrolyzer_current['voltage'], init_electrolyzer_current['current']))

    while True:

        new_electrolyzer_current = titrate()

        diff = init_electrolyzer_current

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


        return 0
