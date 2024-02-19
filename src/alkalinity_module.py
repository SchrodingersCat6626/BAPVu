import communications

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


def convert_curent_to_pH():
    """ Takes in sensor current and converts to pH """




    return


def set_electrolyzer_potential():




    return


def get_electrolyzer_potential():



    return


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


def voltage_sweep(data, filepath, fieldnames, electrolyzer_channel, sensor_channels, min_voltage, max_voltage, volt_step_size, current_linit, volt_limit, time_delay):
    """ Sweeps electrolyzer voltage and records voltage, current and time in a separate file
    This data can be combined with sensing data to examine the relationship between electrolyzer current/voltage and pH.
    The pH can be calibrated separately.
    """

    dev_channel_num = 4
    data_expected_per_channel = 2 # number or 'off' and a unit.
    data_len_per_device = dev_channel_num*data_expected_per_channel
    expected_rowsize = data_len_per_device*daq_num


    new_filepath = filepath+"_sweep" ### change filename to include sweep
    new_fieldnames = fieldnames # creating a local copy of fieldnames
    new_fieldnames.append('electrolyzer_potential')
    #### New fields: systime, ch1, ch2, ch3, ch4...etc., electrolyzer_potential
    fileHandling.filecreate(new_filepath, new_fieldnames)

     # Reading a list of com ports
    ports = get_com_ports()

    if len(ports) > 3:
        
        print("Reading more than 3 eDAQ's is currently unsuported!")

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


    buffer = dict() # save buffer as dictionary. All data is written to the file once the sweep is completed.


    for serial_obj in ser:
        write_data(serial_obj, 'i 1')
        sleep(time_delay)
    
    for serial_obj in ser:
        data = read_data(serial_obj)
    
    data.extend(get_electrolyzer_potential())

    chunk = dict(zip(new_fieldnames, data))

    def wait():

        return 

    def continue_reading_data():
        
        return

    from threading import Thread


        # Using threading, the sweep will read data whenever do_sweep is sleeping.
        # Race condition!
        # Need to block writing to data dict?

    
    def do_read_data():





        return
    
    
    lock = threading.lock()



    data_reading_thread = Thread(x, args=())
    wait_thread = Thread(time.sleep, args=(time_delay,))


    def do_sweep(lock):


        ######################## Set minimum voltage. No need to have started reading data yet #################################

        if max_voltage > volt_limit:

            print("Error: given voltage range exceeds device limit.")
            
            return
            
            
        set_electrolyzer_potential(min_voltage)
        
        time.sleep(time_delay)
        
        electrolyzer_setpoint = min_voltage
        
        while get_electrolyzer_potential() != min_voltage: # waiting for electrolyzer setpoint to be changed to starting point

            time.sleep(time_delay)


        ######################################## Start reading/writing data ##############################################################

        ######################################## Ramp voltage ############################################################################

        ########################## Read data while we wait ~10 mins before incrementing voltage ##########################################
            
            
        while electrolyzer_setpoint <= max_voltage:
            
            electrolyzer_setpoint = electrolyzer_setpoint+volt_step_size
            
            set_electrolyzer_potential(electrolyzer_setpoint)
            
            time.sleep(time_delay)
            
            while get_electrolyzer_potential() != electrolyzer_setpoint: # waiting for electrolyzer setpoint to be changed.
                
                time.sleep(time_delay)



    communications.write_to_file(data,filepath=new_filepath)




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

    buffer.append(data)

    if len(buffer) == chunk_size:
        write_to_file(buffer,filepath)
        buffer = [] # clears buffer
    else:
        continue
        

    
    for serial_obj in ser:

        serial_obj.close()


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
