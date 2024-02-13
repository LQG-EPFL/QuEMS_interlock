from interlock import *

import piplates.THERMOplate as THERMO
import piplates.DAQC2plate as DQ

class ThermoMeter:
    def __init__(self, piid, tid):
        self.piid = piid
        self.tid = tid
        
    def get_value(self):
        

        value = THERMO.getTEMP(self.piid, self.tid)

        time.sleep(0.01)
        return value

def make_THERMOplate(piid):
    inputs = []
    for tid in range(11):
        tid += 1
        thermometer = ThermoMeter(piid, tid)
        inputs += [Input(thermometer.get_value, 'temp('+str(piid)+','+str(tid)+')', 'float', tag = 'temperature')]
    return inputs

class DI:
    def __init__(self, piid, tid):
        self.piid = piid
        self.tid = tid
        
    def get_value(self):
        return bool(DQ.getDINbit(self.piid, self.tid))
    
class DO:
    def __init__(self, piid, tid):
        self.piid = piid
        self.tid = tid
        
    def set_value(self, value):
        if value == True:
            DQ.setDOUTbit(self.piid, self.tid)
        else:
            DQ.clrDOUTbit(self.piid, self.tid)

class AI:
    def __init__(self, piid, tid):
        self.piid = piid
        self.tid = tid
        
    def get_value(self):
        return DQ.getADC(self.piid, self.tid)

class AO:
    def __init__(self, piid, tid):
        self.piid = piid
        self.tid = tid
        
    def set_value(self, value):
        DQ.setDAC(self.piid, self.tid, value)
        
class PWM:
    def __init__(self, piid, tid):
        self.piid = piid
        self.tid = tid
        
    def set_value(self, value):
        DQ.setPWM(self.piid, self.tid, value)

def make_DAQCplate(piid):
    inputs = []
    outputs = []
    
    for tid in range(8):
        di = DI(piid, tid)
        inputs += [Input(di.get_value, 'di('+str(piid)+','+str(tid)+')', 'bool', tag = 'digital input')]
        
    for tid in range(8):
        do = DO(piid, tid)
        outputs += [Output(do.set_value, 'do('+str(piid)+','+str(tid)+')', 'bool',False ,False , False , tag = 'digital output')]
        
    for tid in range(8):
        ai = AI(piid, tid)
        inputs += [Input(ai.get_value, 'ai('+str(piid)+','+str(tid)+')', 'float', tag = 'analog input')]
        
    for tid in range(4):
        ao = AO(piid, tid)
        outputs += [Output(ao.set_value, 'ao('+str(piid)+','+str(tid)+')', 'float',0., 0., 0., tag = 'analog output')]
        
    for tid in range(2):
        pwm = PWM(piid, tid)
        outputs += [Output(pwm.set_value, 'pwm('+str(piid)+','+str(tid)+')', 'float',0., 0., 0., tag = 'pwm output')]
        
    return inputs, outputs
    
