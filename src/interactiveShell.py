#!/usr/bin/python3
from cmd import Cmd

class interactiveShell(Cmd):
    intro = ''
        # This prompt is a placeholder. The prompt should indicate which device you are interfacing with.
    prompt = '(eDAQ) >'
    file = None

    def placeholder(self, inp):

        print("test1")

        return



 # Note: all the code in this function is pasted from the old main.py and may not be compatible.
        
        # selecting which device to send commands to. There should be an option to send commands to all devices at the same time.
        
            # list_edaq=subprocess.Popen("/home/thomas/Dropbox/B.A.Vu/./list_edaqs.sh", stdout=subprocess.PIPE)
            # output= list_edaq.stdout.read()
            # output = bytes.decode(output)
            # edaq_list = output.split('\n')

            # for edaq in edaq_list:
            #     if edaq == '':
            #         edaq_list.remove(edaq)
            #         
            # if len(edaq_list)==0:
            #     edaq_list = '(None)'

            # print(edaq_list)

            # edaq = input("Input a the selected device: ")

            # if edaq in edaq_list:
            #     print('eDAQ selection is valid.')
            #     
            # else:
            #     print("selected eDAQ not found. Try again.")
            #     return

