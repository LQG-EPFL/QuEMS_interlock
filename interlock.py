from flexx import flx
import time

class Trigger:
    def __init__(self, mode, value):
        self.mode = mode
        self.value = value

class Input:
    def __init__(self, read, name, value_type, user_name = None):
        '''
        read: read function
        name: str that identifies what this input refers to, for example ADC 0 0 for 0th ADC of 0th DAQ plate 
        value_type: "bool" or 'float'
        user_name: str that specifies the name of the input. So what is connected to it
        '''
        self.read = read
        self.name = name
        self.value_type = value_type
        
        if user_name == None:
            self.user_name = name
            
        self.triggers = []
            
    def add_trigger(self, mode, value = None):
        '''
            mode: if value_type is "bool" the mode can be
                   "if False": trigger interlock on False
                   "if True": trigger interlock on True
                  if value_type is float
                   "if greater than": trigger interlock is read gives result greater than value 
                   "if smaller than": trigger interlock is read gives result smaller than value
        '''

        self.triggers += [Trigger(mode, value)]
            
    def check_triggers(self):
            
        res = self.read()
            
        for trigger in self.triggers:
         
            if self.value_type == 'bool':
                
                if trigger.mode == 'if False':
                    if res == False:
                        return False

                elif trigger.mode == 'if True':
                    if res:
                        return False
                        
                else:
                    raise ValueError('trigger mode '+trigger.mode+' is incorrect for value_type "bool"')
                        
            if self.value_type == 'float':
                    
                if trigger.mode == 'if greater than':
                        if res > trigger.value:
                            return False
                elif trigger.mode == 'if smaller than':
                        if res < trigger.value:
                            return False
                else:
                    raise ValueError('trigger mode '+trigger.mode+' is incorrect for value_type "flaot"')
            
        return True
    
    def __repr__(self):
        
        return self.name+' ('+self.user_name+')'
                    
                        
                        
                        
                        
class Output:
    def __init__(self, read, write, name, value_type, user_name = None):
        '''
        read: read function
        name: str that identifies what this input refers to, for example ADC 0 0 for 0th ADC of 0th DAQ plate 
        value_type: "bool" or [min_value, max_value]
        user_name: str that specifies the name of the input. So what is connected to it
        '''
        
        self.read = read
        self.write = write
        self.name = name
        self.value_type = value_type
        self.triggered_value = None
        self.normal_value = None
        self.value_before_trigger = self.read()
        
        
        if user_name == None:
            self.user_name = name
            
    def if_triggered_set_to(self, value):
            
        self.triggered_value = value
            
    def if_normal_set_to(self, value):
            
        self.normal_value = value
            
    def trigger(self):
        self.value_before_trigger = self.read()
            
        if self.triggered_value is not None:
            self.write(self.triggered_value)
                
    def reset(self):
        self.write(self.value_before_trigger)
        
    def set_normal(self):
            
        if self.normal_value is not None:
                
            self.write(self.normal_value)
    def __repr__(self):
        
        return self.name+' ('+self.user_name+')'        
            
class Interlock:
    
    def __init__(self, inputs, outputs, rate = 1):
        
        self.inputs = inputs
        self.outputs = outputs
        
        self.trigger()
        
        self.rate = rate
        
    
    def trigger(self):
        
        self.triggered = True
        for output in self.outputs:
            output.trigger()
    
    def reset(self):
        if self.triggered:
            self.triggered = False
            for output in self.outputs:
                output.reset()
        else:
            print ('Interlock was not triggered. Nothing to reset')
           
    
    def set_normal(self):
        self.triggered = False
        for output in self.outputs:
            output.set_normal()
    
    def run(self):
        import threading
        
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()
        
    def loop(self):
        try:
            while True:
                for inp in self.inputs:
                    if self.triggered == False:
                        if inp.check_triggers() == False:
                            self.trigger()

                            print ('There is a problem with ', inp)
                        else:    
                            print ('everything ok')
                    else:
                        print ('Interlock is triggered')  

                time.sleep(1/self.rate)
        except:
            self.trigger()
        
    def stop(self):
        self.thread.join()
        self.trigger()
        

import numpy as np     
test_inp = Input(np.random.rand, 'test_in', 'float')
test_out = Output(np.random.rand, print, 'test_out', 'float')

test_inp.add_trigger('if greater than', 0.5)

interlock = Interlock([test_inp], [test_out])      
        
class InputGUI(flx.Widget):
    
    def init(self,inp):
        super().init()
        self.input = inp
        with flx.VBox():
            flx.Label(html = str(inp))
        

class InterlockGUI(flx.Widget):

    def init(self):
        super().init()
        
        
        with flx.VBox():
            flx.Label(html = '<h1> QuEMS Interlock </h1>')
            
            for inp in interlock.inputs:
                 InputGUI(inp)
            
            
     


if __name__ == '__main__':
    
    
    
    m = flx.launch(InterlockGUI, 'chrome')
    flx.run()