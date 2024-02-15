
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


def voltage_sweep():
    """ Sweeps electrolyzer voltage and records voltage, current and time in a separate file
    This data can be combined with sensing data to examine the relationship between electrolyzer current/voltage and pH.
    The pH can be calibrated separately.
    """

    

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
