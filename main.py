import logging
import sys


file_handler = logging.FileHandler(filename='errors.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.ERROR, 
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger('interlock')


from interlock import *
import gui


mockup = False
heartbeat = True
load_config = True
rate = 1.0

#connect all the devices
if not mockup:
    from drivers.piplates_driver import *
    from drivers.pfeiffer_driver import *

    pres_ins = make_TPG362('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AM0076FH-if00-port0')
    temp_ins = make_THERMOplate(2)
    daqc1_ins, daqc1_outs = make_DAQCplate(0)
    daqc2_ins, daqc2_outs = make_DAQCplate(1)


#test inputs and outputs
if mockup:
    import numpy as np
    test_float = Input(lambda: np.random.rand()/(int(np.random.rand()*10)), 'test float', 'float')
    test_bool = Input(lambda: np.random.rand()>0.5 , 'test bool', 'bool')
    test_out = Output(lambda x: True, 'test_out','float',0, 0, 0)

#start interlock
if mockup:
    interlock = Interlock([test_float, test_bool], [test_out], rate = rate) #pres_ins+temp_ins+daqc1_ins+daqc2_ins,daqc1_outs + daqc2_outs)   
else:
    interlock = Interlock(pres_ins+temp_ins+daqc1_ins+daqc2_ins,daqc1_outs + daqc2_outs, rate = rate)   

#load old configuration
if not mockup:
    config_folder = '/home/lqg/QuEMS_interlock/configs'
    values_folder = '/home/lqg/QuEMS_interlock/values'
    if load_config:
        interlock.load_config(config_folder+'/startup.iconf')

    #start heartbeat
    if heartbeat:
        for output in daqc2_outs:
            if output.name == 'do(1,0)':
                hb_ouput = output
                break
        interlock.set_heartbeat(output)
else:
    config_folder = 'configs'
    values_folder = 'values'

interlock.run()
interlock.reset()




#launch gui
import remi

if mockup:
    remi.start(gui.QuEMS_Interlock,start_browser=False,username = 'lqg', password = 'ManipeEPFL2018', port = 10000, userdata = (interlock,config_folder,values_folder,))
else:
    remi.start(gui.QuEMS_Interlock,start_browser=False, username = 'lqg', password = 'ManipeEPFL2018',address='0.0.0.0', port = 10000, userdata = (interlock,config_folder,values_folder,))

