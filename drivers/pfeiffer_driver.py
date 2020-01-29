### Load the module:
from drivers.PfeifferVacuum import MaxiGauge
from interlock import *
import numpy as np
class TPG362channel:
    def __init__(self, mg, channel_id):
        self.mg = mg
        self.channel_id = channel_id
        
    def get_value(self):
        return float(self.mg.pressure(self.channel_id).pressure)
    
def make_TPG362(serial_port):
    
    mg = MaxiGauge(serial_port)
    inputs = []
    
    
    for channel_id in np.arange(1,3):
        gauge = TPG362channel(mg, channel_id)
        inputs += [Input(gauge.get_value, 'pres('+str(serial_port)[-7:]+','+str(channel_id)+')', 'float', tag = 'pressure')]
        
    return inputs
        
    