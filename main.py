from interlock import *
import gui

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger('interlock')

import numpy as np     
test_infloat = Input(np.random.rand, 'test_infloat', 'float', tag = 'tree')


def randbool():
    x = np.random.rand()
    
    if x >0.01:
        return False
    else:
        return True

test_inbool = Input(randbool, 'test_inbool', 'bool')
test_outfloat = Output(lambda x: logger.info('Output set to '+str(x)), 'test_outfloat', 'float',0., 0., 1.)
test_outbool = Output(lambda x: logger.info('Output set to '+str(x)), 'test_outbool', 'bool',False, False, False)

test_infloat.add_trigger('greater than', 0.9)
test_inbool.add_trigger('True')

interlock = Interlock([test_infloat, test_inbool], [test_outfloat, test_outbool])   

interlock.run()
interlock.reset()

config_folder = 'C:\\Users\\sauerwei\\OneDrive\\Projekte und Jobs\\EPFL_Brantut\\programs\\interlock\\QuEMS_interlock\\configs'

import remi
remi.start(gui.QuEMS_Interlock,start_browser=False, port = 10000, userdata = (interlock,config_folder,))

