import time

class Trigger:
    def __init__(self, inp, mode, value):
        self.mode = mode
        self.value = value
        self.input = inp
    def __repr__(self):
        if self.value == None:
            value = ''
        else:
            value = self.value
        return 'Trigger if '+str(self.input)+' '+self.mode+' '+str(value)

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
                   "False": trigger interlock on False
                   "True": trigger interlock on True
                  if value_type is float
                   "greater than": trigger interlock is read gives result greater than value 
                   "smaller than": trigger interlock is read gives result smaller than value
        '''

        self.triggers += [Trigger(self, mode, value)]
            
    def check_triggers(self):
            
        res = self.read()
            
        for trigger in self.triggers:
         
            if self.value_type == 'bool':
                
                if trigger.mode == 'False':
                    if res == False:
                        return trigger

                elif trigger.mode == 'True':
                    if res:
                        return trigger
                        
                else:
                    raise ValueError('trigger mode "'+trigger.mode+'" is incorrect for value_type "bool"')
                        
            if self.value_type == 'float':
                    
                if trigger.mode == 'greater than':
                        if res > trigger.value:
                            return trigger
                elif trigger.mode == 'smaller than':
                        if res < trigger.value:
                            return trigger
                else:
                    raise ValueError('trigger mode "'+trigger.mode+'" is incorrect for value_type "float"')
    
    def __repr__(self):
        
        return 'Input '+self.name+' ('+self.user_name+')'
                    
                        
                        
                        
                        
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
        
        return 'Output '+self.name+' ('+self.user_name+')'        

import traceback
    
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
            for i in range(3):
                for inp in self.inputs:
                    if self.triggered == False:
                        trig = inp.check_triggers()
                        if trig is not None:
                            self.trigger()

                            print ('There is a problem! ', trig)
                        else:    
                            print ('everything ok')
                    else:
                        print ('Interlock is triggered')  

                time.sleep(1/self.rate)
        except:
            traceback.print_exc()
            self.trigger()
            
            
        
    def stop(self):
        self.thread.join()
        self.trigger()
           


        