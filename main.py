from interlock import *
import gui

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

logger = logging.getLogger('interlock')

heartbeat = True
load_config = False

#connect all the devices

from drivers.piplates_driver import *
from drivers.pfeiffer_driver import *

pres_ins = make_TPG362('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AM0076FH-if00-port0')
temp_ins = make_THERMOplate(2)
daqc1_ins, daqc1_outs = make_DAQCplate(0)
daqc2_ins, daqc2_outs = make_DAQCplate(1)


#test inputs and outputs
#import numpy as np
#test_inp = Input(np.random.rand, 'test_in', 'float')
#test_out = Output(print, 'test_out','float',0, 0, 0)

#start interlock
interlock = Interlock(pres_ins+temp_ins+daqc1_ins+daqc2_ins,daqc1_outs + daqc2_outs)   

#load old configuration
config_folder = './configs'
values_folder = './values'
if load_config:
    interlock.load_config(config_folder+'/startup.iconf')

#start heartbeat
if heartbeat:
    for output in daqc2_outs:
        if output.name == 'do(1,0)':
            hb_ouput = output
            break
    interlock.set_heartbeat(output)


interlock.run()
interlock.reset()




#launch gui
import remi
remi.start(gui.QuEMS_Interlock,start_browser=False,username = 'lqg', password = 'ManipeEPFL2018',address='0.0.0.0', port = 10000, userdata = (interlock,config_folder,values_folder,))

