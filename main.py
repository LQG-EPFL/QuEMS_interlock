from interlock import *
import gui

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

logger = logging.getLogger('interlock')

heartbeat = True
load_config = True

#connect all the devices

from drivers.piplates_driver import *
from drivers.pfeiffer_driver import *

#pres_ins = make_TPG362('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AM0076FH-if00-port0')
temp_ins = make_THERMOplate(1)
daqc1_ins, daqc1_outs = make_DAQCplate(3)
#daqc2_ins, daqc2_outs = make_DAQCplate(1)


#test inputs and outputs
#import numpy as np
#test_float = Input(np.random.rand, 'test float', 'float')
#test_bool = Input(lambda: np.random.rand()>0.5, 'test bool', 'bool')
#test_out = Output(print, 'test_out','float',0, 0, 0)

#start interlock
interlock = Interlock(temp_ins+daqc1_ins,daqc1_outs) 
#Interlock(pres_ins+temp_ins+daqc1_ins+daqc2_ins,daqc1_outs + daqc2_outs)   

#load old configuration
config_folder = '/home/aokilab/Interlock/configs'
values_folder = '/home/aokilab/Interlock/values'
if load_config:
    interlock.load_config(config_folder+'/startup.iconf')

#start heartbeat
if heartbeat:
    for output in daqc1_outs:
        if output.name == 'do(3,0)':
            hb_ouput = output
            break
    interlock.set_heartbeat(output)


interlock.run()
interlock.reset()




#launch gui
import remi
remi.start(gui.QuEMS_Interlock,start_browser=False,username = 'aokilab', password = 'Cesium8523',address='192.168.100.30', port = 10000, userdata = (interlock,config_folder,values_folder,))

