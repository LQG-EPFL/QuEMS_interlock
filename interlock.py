import time
from datetime import datetime
import logging
import sys
import json
import threading

import traceback

import numpy as np

logger = logging.getLogger('interlock')


from influxdb import InfluxDBClient
class InfluxdbChannel:
    def __init__(self, error_timeout = 10):
        '''
        error_timeout: if there is any error with the connection to influxdb, the object will do nothing until
        the error_timeout time has part
        '''
        self.dbClient = InfluxDBClient('192.168.1.1', 8086, 'root', 'root', 'mydb',
                       timeout = 0.1, retries = 2)
        self.error = False
        self.error_timeout = error_timeout
        self.time_of_last_error = 0
        
    def send_data(self, data):
        if self.error == False or time.time() - self.time_of_last_error > self.error_timeout:
            try:
                self.dbClient.write_points(data)
                self.error = False
            except KeyboardInterrupt:
                    raise
            except Exception as e:
                # ~ logger.error(e, exc_info=True)
                self.error = True
                self.time_of_last_error = time.time()
        else:
            pass

inflxudb_channel = InfluxdbChannel()


class Trigger:
    def __init__(self, inp, mode, value, trigger_count):
        self.mode = mode
        self.value = value
        self.input = inp
        self.triggered = False
        self.warned = False
        self.trigger_count = trigger_count
        self.count = self.trigger_count
        self.check()
    
    def __repr__(self):
        if self.value == None:
            value = ''
        else:
            value = self.value
        return 'Trigger if '+str(self.input)+' '+self.mode+' '+str(value)
    def get_value(self):
        
        return self.value
    
    def set_value(self, value):
        
        self.value = value
        self.status()
        
    def get_mode(self):
        return self.mode
    
    def set_mode(self, mode):
        self.mode = mode
        self.status()
        
    def reset(self):
    
        self.triggered = False
    
    def status(self):
        try:
            if np.isfinite(self.trigger_count):
                data = [
            {
              "measurement": 'Trigger if '+str(self.input),
                  "tags": {
                  },
                  "time":  datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                  "fields": {
                      "trigger if" : self.mode,
                      "value of trigger": self.value,
                      "is triggered": self.triggered,
                      "trigger count": self.trigger_count,
                      "count": self.count,
                      "is warned": self.warned,
                  }
              }
            ]
            else:
                data = [
            {
              "measurement": 'Trigger if '+str(self.input),
                  "tags": {
                  },
                  "time":  datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                  "fields": {
                      "trigger if" : self.mode,
                      "value of trigger": self.value,
                      "is triggered": self.triggered,
                      "is warned": self.warned,
                  }
              }
            ]
                
            #logger.info(self.value)
            inflxudb_channel.send_data(data)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
        
        
        
    def check(self):
        res = self.input.last_value
        to_trigger = False
        if self.input.value_type == 'bool':
            if self.mode == 'False':
                if res == False:
                    to_trigger = True

            elif self.mode == 'True':
                if res:
                    to_trigger = True
                    
            else:
                raise ValueError('trigger mode "'+self.mode+'" is incorrect for value_type "bool"')
                    
        if self.input.value_type == 'float':
            if self.mode == 'greater than':
                    if res > self.value:
                        to_trigger = True
            elif self.mode == 'smaller than':
                    if res < self.value:
                        to_trigger = True
            else:
                raise ValueError('trigger mode "'+self.mode+'" is incorrect for value_type "float"')
        
        
        
        
        if to_trigger:
            self.count -= 1
            self.warned = True
        else:
            self.count = self.trigger_count
            self.warned = False
            
        if self.count < 1:
            self.triggered = True
            self.status()
            
            return True
        
        
        self.status()
        
        return False
    
    def get_config(self):
        config = {'mode': self.mode, 
                  'value': self.value, 
                  'triggered': self.triggered,
                  'trigger_count': self.trigger_count}
        return config
        
    def set_config(self, config):
        self.mode = config['mode']
        self.value = config['value']
        self.triggered = config['triggered']
        if 'trigger_count' in config:
            self.trigger_count = config['trigger_count']
        else:
            self.trigger_count = 10
               
class Input:
    def __init__(self, read, name, value_type, username = None, tag = 'no tag'):
        '''
        read: read function
        name: str that identifies what this input refers to, for example ADC 0 0 for 0th ADC of 0th DAQ plate 
        value_type: "bool" or 'float'
        username: str that specifies the name of the input. So what is connected to it
        '''
        self.read = read
        self.name = name
        self.value_type = value_type
        
        self.tag = tag
        
        if username == None:
            self.username = name
            
        self.triggers = []
        
        self.update()
            
    def add_trigger(self, mode, value = None, trigger_count = 10):
        '''
            mode: if value_type is "bool" the mode can be
                   "False": trigger interlock on False
                   "True": trigger interlock on True
                  if value_type is float
                   "greater than": trigger interlock is read gives result greater than value 
                   "smaller than": trigger interlock is read gives result smaller than value
            trigger count: number of times that condition has to be fullfilled before interlock
                    triggers
        '''
        trigger = Trigger(self, mode, value, trigger_count)
        self.triggers += [trigger]
        
        return trigger
    def get_tag(self):
        return self.tag
        
    def set_tag(self, tag):
        self.tag = tag
        self.status()
    
    def get_username(self):
        
        return self.username
    
    def set_username(self, username):
        
        self.username = username
        
        self.status()
        
    def reset(self):
        for trigger in self.triggers:
            trigger.reset()
    
    def read_timeout(self):
        
        return self.read()
    
    
    def update(self):
    
        success = True
        try:
            value = self.read_timeout()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error('Error in reading the value from ', str(self))
            logger.error(e, exc_info=True)
            
            success = False
            
            value = -1
            #raise Exception('Value of ',str(self),' could not be read')
            
        self.last_value = value
        self.status()
        
        return success
        
    def get_value(self):
        
        return self.last_value
        
    def status(self):

        try:
            data = [
        {
          "measurement": self.name,
              "tags": {
              },
              "time":  datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
              "fields": {
                  "value" : self.last_value,
                  "username" : self.username,
                  "tag": self.tag,
              }
          }
        ]
            inflxudb_channel.send_data(data)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error('Connection with influxdb failed in ', str(self))
            logger.error(e, exc_info=True)
        
    def check_triggers(self):
        to_trig = False
        
        for trigger in self.triggers:
            to_trig = trigger.check() or to_trig
        
        return to_trig
            
    
    def __repr__(self):
        
        return 'Input '+self.name+' ('+self.username+')'
        
    def get_config(self):
        config = {'name': self.name,
                  'tag': self.tag, 
                  'username': self.username,
                  'triggers': []}
        
        for trigger in self.triggers:
            config['triggers'] += [trigger.get_config()]
            
        return config
            
    def set_config(self, config):
        self.username = config['username']
        self.tag = config['tag']
        
        self.triggers.clear()
        
        for trig_conf in config['triggers']:
            if 'trigger_count' in trig_conf:
                self.add_trigger(trig_conf['mode'], value = trig_conf['value'], trigger_count = trig_conf['trigger_count'])
            else:
                self.add_trigger(trig_conf['mode'], value = trig_conf['value'])
                                     
class Output:
    def __init__(self, write, name, value_type, initial_value, normal_value, triggered_value, username = None, tag = 'no tag'):
        '''
        read: read function
        name: str that identifies what this input refers to, for example ADC 0 0 for 0th ADC of 0th DAQ plate 
        value_type: "bool" or [min_value, max_value]
        username: str that specifies the name of the input. So what is connected to it
        '''
        
        self.write = write
        self.name = name
        self.value_type = value_type
        
        self.tag = tag
        self.interlock = None
        
        if username == None:
            self.username = name
        
        if value_type == 'float':
            self.triggered_value = float(triggered_value)
            self.normal_value = float(normal_value)
            self.value_before_trigger = float(initial_value)
            
        if value_type == 'bool':
            self.triggered_value = bool(triggered_value)
            self.normal_value = bool(normal_value)
            self.value_before_trigger = bool(initial_value)
        self.set_value(initial_value)
        
        self.is_heardbeat = False


    
    def status(self):
        
        try:
            data = [
        {
          "measurement": str(self.name),
              "tags": {
              },
              "time":  datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
              "fields": {
                  "username" : self.username,
                  "value" : self.value,
                  "triggered_value": self.triggered_value,
                  "normal_value": self.normal_value,
                  "tag": self.tag,
              }
          }
        ]
            inflxudb_channel.send_data(data)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(e, exc_info=True)
    def get_tag(self):
        return self.tag
        
    def set_tag(self, tag):
        self.tag = tag
        self.status()
    def set_username(self, username):
        self.username = username
        self.status()
        
    def get_username(self):
        
        return self.username
        
    def set_value(self, value, force = False):
        if not self.interlock is None:
            if not force and self.interlock.triggered and not self.is_heardbeat:
                return 0
        
        if self.value_type == 'float':
            value = float(value)
        if self.value_type == 'bool':
            value = bool(value)
    
        self.value = value
        
    def update(self):
        try:
            self.write(self.value)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error('Error in writing the value to ', str(self))
            logger.error(e, exc_info=True)
            raise Exception('Value of ',str(self),' could not be set')
            
        self.status()
        
    def get_value(self):
        return self.value
        
    def get_normal_value(self):
        return self.normal_value
        
    def set_normal_value(self, value):
        self.normal_value = value
        self.status()
        
    def get_triggered_value(self):
        return self.triggered_value
        
    def set_triggered_value(self, value):
        self.triggered_value = value
        self.status()
    
    def set_to_normal_value(self):
        self.set_value(self.normal_value)
        
    def set_to_triggered_value(self):
        self.set_value(self.triggered_value)
            
    def trigger(self):
        self.value_before_trigger = self.value
        if self.triggered_value is not None:
            self.set_value(self.triggered_value, force = True)
        
                
    def reset(self):
        self.set_value(self.value_before_trigger)
        
    def set_normal(self):
        if self.normal_value is not None:
            self.set_value(self.normal_value)
            
    def __repr__(self):
        return 'Output '+self.name+' ('+self.username+')'

    def get_config(self):
        config = {'name': self.name,
                  'tag': self.tag, 
                  'username': self.username, 
                  'normal_value': self.normal_value,
                  'triggered_value': self.triggered_value}
                  
        return config
                  
    def set_config(self, config):
        self.tag = config['tag']
        self.username = config['username']
        self.normal_value = config['normal_value']
        self.triggered_value = config['triggered_value']
        
        self.set_value(self.triggered_value)

class Interlock:
    def __init__(self, inputs, outputs, rate = 1, trigger_count = 10):
        self.loop_time = 0.
        
        self.inputs = {input.name: input for input in inputs}
        
        for input in self.inputs.values():
            input.interlock = self
        
        self.outputs = {output.name: output for output in outputs}
        
        for output in self.outputs.values():
            output.interlock = self
        
        self.running = False
        self.rate = rate
        
        self.gui = False
        self.heartbeat_connected = False
        
        self.trigger()
        

    
    def get_input_tags(self):
        tags = set([])
        for input in self.inputs.values():
            tags.add(input.tag)
    
    def get_output_tags(self):
        tags = set([])
        for output in self.outputs.values():
            tags.add(output.tag)
    
    def get_config(self):
        
        config = {'running': self.running, 
                'triggered': self.triggered,
                'outputs': {},
                'inputs': {}}
                
        for output in self.outputs.values():
            config['outputs'][output.name] = output.get_config()
            
        for input in self.inputs.values():
            config['inputs'][input.name] = input.get_config()
            
        return config
            
    def set_config(self, config):
        self.running = config['running']
        self.triggered = config['triggered']
        
        for name, out_conf in config['outputs'].items():
            if name in self.outputs:
                self.outputs[name].set_config(out_conf)
        
        for name, in_conf in config['inputs'].items():
            if name in self.inputs:
                self.inputs[name].set_config(in_conf)
    
    def save_config(self, filename, comment = ''):
        config = self.get_config()
        config['comment'] = comment
        json.dump( config, open( filename, 'w' ) ,indent=4)
        
    def load_config(self, filename):
        config = json.load( open( filename) )
        self.set_config(config)
        
        return config['comment']
        
    def get_values(self):
        values = {}
        for output in self.outputs.values():
            values[output.name] = output.get_value()   
        return values
            
    def set_values(self, values):
        for name, out_val in values.items():
            if name in self.outputs:
                self.outputs[name].set_value(out_val)
        
        
    def load_values(self, filename):
        values = json.load( open( filename) )
        self.set_values(values)
        
        return values['comment']
        
    def save_values(self, filename, comment = ''):
        values = self.get_values()
        values['comment'] = comment
        json.dump( values, open( filename, 'w' ) ,indent=4)
    
    def status(self):
        try:
            data = [
        {
          "measurement": "interlock",
              "tags": {
              },
              "time":  datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
              "fields": {
                  "running" : self.running,
                  "rate": self.rate,
                  "triggered": self.triggered,
                  "loop_time": self.loop_time,
              }
          }
        ]
            inflxudb_channel.send_data(data)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error('Connection with influxdb failed in ', str(self))
            logger.error(e, exc_info=True)
                
    def trigger(self):
        self.triggered = True
        for output in self.outputs.values():
            output.trigger()
        self.status()
    
    def set_heartbeat(self, hb_output):
        
        self.heartbeat = hb_output
        self.heartbeat.is_heardbeat = True
        self.heartbeat_connected = True
    
    def reset(self):
        if self.triggered:
            self.triggered = False
            for input in self.inputs.values():
                input.reset()
            
            for output in self.outputs.values():
                output.reset()
            self.status()
        else:
            logger.info('Interlock was not triggered. Nothing to reset')
           
    def set_normal(self):
        self.triggered = False
        for output in self.outputs.values():
            output.set_normal()
        self.status()
    
    def run(self):
        self.running = True
        
        self.thread = threading.Thread(target=self.loop)
        self.thread.daemon = True
        self.thread.start()
        self.status()
        
    def loop(self):
        try:
            while self.running:
                t = time.time()
                to_trig = False
                
                logger.info('Check inputs')
                
                # read inputs from device
                for inp in self.inputs.values():
                    to_trig = not inp.update() or to_trig
                
                
                # check triggers
                for inp in self.inputs.values():
                    to_trig = inp.check_triggers() or to_trig
                    logger.info(inp)
                
                # react to triggers
                if self.triggered:
                    to_trig = False
                
                if to_trig:
                    self.trigger()
                    
                else:
                    if self.triggered:
                        logger.info('state:triggered')
                    else:
                        logger.info('state:ok')
                        
                
                    
                logger.info('Sending status')
                self.status()
                # update heartbeat
                if self.heartbeat_connected:
                    logger.info('Sawp heartbeat')
                    self.swap_heartbeat()
                
                # update outputs
                for output in self.outputs.values():
                    output.update()
                
                time_passed = time.time()-t
                self.loop_time = time_passed
                if 1/self.rate - time_passed > 0:
                    time.sleep(1/self.rate - time_passed)
                else:
                    max_rate = 1/time_passed
                    logger.info(f'rate of {self.rate:2f} could not be reached. Best rate: {max_rate:2f}')
                # ~ print ('all fine, next iteration -->')
                print (time.time()-t)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error('Fatal error in Interlock loop!!!', str(self))
            logger.error(e, exc_info=True)
            self.running = False
            self.trigger()
            self.status()
            
            for output in self.outputs.values():
                    output.update()
            
            
    def swap_heartbeat(self):
        if self.heartbeat.get_value():
            self.heartbeat.set_value(False)
        else:
            self.heartbeat.set_value(True)
    
    def add_gui(self,interlock_app):
        self.interlock_app = interlock_app
        self.gui = True
        logger.info('interlock gui connected to interlock')
            
    def stop(self):
        logger.info('Interlock was stopped')
    
        self.running = False
        self.thread.join()
        self.trigger()
        self.status()
           


        
