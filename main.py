from interlock import *
import gui


import numpy as np     
test_inp = Input(np.random.rand, 'test_in', 'float')
test_out = Output(np.random.rand, print, 'test_out', 'float')

test_inp.add_trigger('greater than', 0.5)

interlock = Interlock([test_inp], [test_out])   

interlock.run()
interlock.reset()

gui.launch(interlock)