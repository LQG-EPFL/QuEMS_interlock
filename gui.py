import remi.gui as gui
from remi import start, App
import os

import psutil

import logging
logger = logging.getLogger('interlock')

import numpy as np

def read_text(text, app):
    audio_filename = '/home/pi/QuEMS_interlock/audio/speech.mp3'
    # Import the required module for text  
    # to speech conversion 
    from gtts import gTTS 
  
    # This module is imported so that we can  
    # play the converted audio 
    import os 
  
    # The text that you want to convert to audio 
  
    # Language in which you want to convert 
    language = 'en'
    
    print (text)
    # Passing the text and language to the engine,  
    # here we have marked slow=False. Which tells  
    # the module that the converted audio should  
    # have a high speed 
    myobj = gTTS(text=text, lang=language, slow=False) 
  
    # Saving the converted audio in a mp3 file named 
    #welcome  
    myobj.save(audio_filename) 
  
    
    app.execute_javascript("(new Audio('%s')).play();"%gui.load_resource(audio_filename))

class GenericDialog(gui.Container):
    """ Generic Dialog widget. It can be customized to create personalized dialog windows.
        You can setup the content adding content widgets with the functions add_field or add_field_with_label.
        The user can confirm or dismiss the dialog with the common buttons Cancel/Ok.
        Each field added to the dialog can be retrieved by its key, in order to get back the edited value. Use the function
         get_field(key) to retrieve the field.
        The Ok button emits the 'confirm_dialog' event. Register the listener to it with set_on_confirm_dialog_listener.
        The Cancel button emits the 'cancel_dialog' event. Register the listener to it with set_on_cancel_dialog_listener.
    """

    def __init__(self, title='', message='', *args, **kwargs):
        """
        Args:
            title (str): The title of the dialog.
            message (str): The message description.
            kwargs: See Container.__init__()
        """
        super(GenericDialog, self).__init__(*args, **kwargs)
        self.set_layout_orientation(gui.Container.LAYOUT_VERTICAL)
        self.style.update({'display':'block', 'overflow':'auto', 'margin':'0px auto'})

        if len(title) > 0:
            t = gui.Label(title)
            t.add_class('DialogTitle')
            self.append(t, "title")

        if len(message) > 0:
            m = gui.Label(message)
            m.css_margin = '5px'
            self.append(m, "message")

        self.container = gui.Container()
        self.container.style.update({'display':'block', 'overflow':'auto', 'margin':'5px'})
        self.container.set_layout_orientation(gui.Container.LAYOUT_HORIZONTAL)
        
        self.conf = gui.Button('Ok')
        self.conf.set_size(60, 30)
        self.conf.css_margin = '3px'
        self.cancel = gui.Button('Cancel')
        self.cancel.set_size(60, 30)
        self.cancel.css_margin = '3px'
        hlay = gui.HBox(height=35)
        hlay.css_display = 'block'
        hlay.style['overflow'] = 'visible'
        hlay.append(self.conf, "confirm_button")
        hlay.append(self.cancel, "cancel_button")
        self.conf.style['float'] = 'right'
        self.cancel.style['float'] = 'right'

        self.append(self.container, "central_container")
        self.append(hlay, "buttons_container")

        self.conf.onclick.connect(self.confirm_dialog)
        self.cancel.onclick.connect(self.cancel_dialog)

        self.inputs = {}

    def add_field_with_label(self, key, label_description, field):
        """
        Adds a field to the dialog together with a descriptive label and a unique identifier.
        Note: You can access to the fields content calling the function GenericDialog.get_field(key).
        Args:
            key (str): The unique identifier for the field.
            label_description (str): The string content of the description label.
            field (Widget): The instance of the field Widget. It can be for example a TextInput or maybe
            a custom widget.
        """
        self.inputs[key] = field
        label = gui.Label(label_description)
        label.css_margin = '0px 5px'
        label.style['min-width'] = '30%'
        container = gui.HBox()
        container.style.update({'justify-content':'space-between', 'overflow':'auto', 'padding':'3px'})
        container.append(label, key='lbl' + key)
        container.append(self.inputs[key], key=key)
        self.container.append(container, key=key)

    def add_field(self, key, field):
        """
        Adds a field to the dialog with a unique identifier.
        Note: You can access to the fields content calling the function GenericDialog.get_field(key).
        Args:
            key (str): The unique identifier for the field.
            field (Widget): The widget to be added to the dialog, TextInput or any Widget for example.
        """
        self.inputs[key] = field
        container = gui.HBox()
        container.style.update({'justify-content':'space-between', 'overflow':'auto', 'padding':'3px'})
        container.append(self.inputs[key], key=key)
        self.container.append(container, key=key)

    def get_field(self, key):
        """
        Args:
            key (str): The unique string identifier of the required field.
        Returns:
            Widget field instance added previously with methods GenericDialog.add_field or
            GenericDialog.add_field_with_label.
        """
        return self.inputs[key]

    @gui.decorate_set_on_listener("(self,emitter)")
    @gui.decorate_event
    def confirm_dialog(self, emitter):
        """Event generated by the OK button click.
        """
        return ()

    @gui.decorate_set_on_listener("(self,emitter)")
    @gui.decorate_event
    def cancel_dialog(self, emitter):
        """Event generated by the Cancel button click."""
        return ()

    @gui.decorate_explicit_alias_for_listener_registration
    def set_on_confirm_dialog_listener(self, callback, *userdata):
        self.confirm_dialog.connect(callback, *userdata)

    @gui.decorate_explicit_alias_for_listener_registration
    def set_on_cancel_dialog_listener(self, callback, *userdata):
        self.cancel_dialog.connect(callback, *userdata)

class TextInputDialog(GenericDialog):
    """Input Dialog widget. It can be used to query simple and short textual input to the user.
    The user can confirm or dismiss the dialog with the common buttons Cancel/Ok.
    The Ok button click or the ENTER key pression emits the 'confirm_dialog' event. Register the listener to it
    with set_on_confirm_dialog_listener.
    The Cancel button emits the 'cancel_dialog' event. Register the listener to it with set_on_cancel_dialog_listener.
    """

    def __init__(self, title='Title', message='Message', initial_value='', *args, **kwargs):
        """
        Args:
            title (str): The title of the dialog.
            message (str): The message description.
            initial_value (str): The default content for the TextInput field.
            kwargs: See Container.__init__()
        """
        super(TextInputDialog, self).__init__(title, message, *args, **kwargs)

        self.inputText = gui.TextInput()
        self.inputText.onkeydown.connect(self.on_keydown_listener)
        self.add_field('textinput', self.inputText)
        self.inputText.set_text(initial_value)

        self.confirm_dialog.connect(self.confirm_value)

    def on_keydown_listener(self, widget, value, keycode):
        """event called pressing on ENTER key.
        propagates the string content of the input field
        """
        if keycode=="13":
            self.inputText.set_text(value)
            self.confirm_value(self)

    @gui.decorate_set_on_listener("(self, emitter, value)")
    @gui.decorate_event
    def confirm_value(self, widget):
        """Event called pressing on OK button."""
        return (self.inputText.get_text(),)

    @gui.decorate_explicit_alias_for_listener_registration
    def set_on_confirm_value_listener(self, callback, *userdata):
        self.confirm_value.connect(callback, *userdata)
        
class FloatInputDialog(GenericDialog):
    """Input Dialog widget. It can be used to query simple and short textual input to the user.
    The user can confirm or dismiss the dialog with the common buttons Cancel/Ok.
    The Ok button click or the ENTER key pression emits the 'confirm_dialog' event. Register the listener to it
    with set_on_confirm_dialog_listener.
    The Cancel button emits the 'cancel_dialog' event. Register the listener to it with set_on_cancel_dialog_listener.
    """

    def __init__(self, title='Title', message='Message', initial_value=0, *args, **kwargs):
        """
        Args:
            title (str): The title of the dialog.
            message (str): The message description.
            initial_value (str): The default content for the TextInput field.
            kwargs: See Container.__init__()
        """
        super(FloatInputDialog, self).__init__(title, message, *args, **kwargs)

        self.inputText = gui.TextInput()
        self.inputText.onkeydown.connect(self.on_keydown_listener)
        self.add_field('textinput', self.inputText)
        self.inputText.set_text(str(initial_value))

        self.confirm_dialog.connect(self.confirm_value)

    def on_keydown_listener(self, widget, value, keycode):
        """event called pressing on ENTER key.
        propagates the string content of the input field
        """
        if keycode=="13":
            self.inputText.set_text(value)
            self.confirm_value(self)

    @gui.decorate_set_on_listener("(self, emitter, value)")
    @gui.decorate_event
    def confirm_value(self, widget):
        """Event called pressing on OK button."""
        return (self.inputText.get_text(),)

    @gui.decorate_explicit_alias_for_listener_registration
    def set_on_confirm_value_listener(self, callback, *userdata):
        self.confirm_value.connect(callback, *userdata)
        
class SelectionInputDialog(GenericDialog):
    """Input Dialog widget. It can be used to query simple and short textual input to the user.
    The user can confirm or dismiss the dialog with the common buttons Cancel/Ok.
    The Ok button click or the ENTER key pression emits the 'confirm_dialog' event. Register the listener to it
    with set_on_confirm_dialog_listener.
    The Cancel button emits the 'cancel_dialog' event. Register the listener to it with set_on_cancel_dialog_listener.
    """

    def __init__(self, options, title='Title', message='Message', initial_value='', *args, **kwargs):
        """
        Args:
            title (str): The title of the dialog.
            message (str): The message description.
            initial_value (str): The default content for the TextInput field.
            kwargs: See Container.__init__()
        """
        super(SelectionInputDialog, self).__init__(title, message, *args, **kwargs)

        self.inputSelection = gui.DropDown()
        self.inputSelection.append(options)
        self.inputSelection.set_value(initial_value)

        self.add_field('selectioninput', self.inputSelection)

class BoolInputDialog(SelectionInputDialog):
    """Input Dialog widget. It can be used to query simple and short textual input to the user.
    The user can confirm or dismiss the dialog with the common buttons Cancel/Ok.
    The Ok button click or the ENTER key pression emits the 'confirm_dialog' event. Register the listener to it
    with set_on_confirm_dialog_listener.
    The Cancel button emits the 'cancel_dialog' event. Register the listener to it with set_on_cancel_dialog_listener.
    """

    def __init__(self, title='Title', message='Message', initial_value=False, *args, **kwargs):
        """
        Args:
            title (str): The title of the dialog.
            message (str): The message description.
            initial_value (str): The default content for the TextInput field.
            kwargs: See Container.__init__()
        """
        super(BoolInputDialog, self).__init__(['True', 'False'] ,title, message, initial_value=str(initial_value), *args, **kwargs)

class InterlockStatus(gui.VBox):
    
    def __init__(self, interlock, app, *args, **kwargs):
    
        super(InterlockStatus, self).__init__(*args, **kwargs)
        
        self.interlock = interlock
        self.app = app
        self.style.update({'width': '100%'})
        self.style['border-radius'] = '25px'
        self.style['margin-top'] = '1em'
        self.style['padding-top'] = '1em'
        self.style['margin-bottom'] = '1em'
        self.style['padding-bottom'] = '1em'
        
        self.heading_cont = gui.HBox(width = "98%")
        
        
        
        self.heading = gui.Container(width = '150pt')
        self.heading.style['padding-left'] = '10pt'
        
        self.heading_label = gui.Label('Status', width = '50pt')
        self.heading_label.style['text-align'] = 'left'
        self.heading_label.style['font-size'] = '20pt'
        
        
        self.heading.append(self.heading_label)
        
        self.label_status = gui.Label()
        self.label_status.style['text-align'] = 'left'
        self.label_status.style['font-size'] = '20pt'
        
        self.heading.append(self.label_status)
        
        self.heading_cont.append(self.heading)
        
        self.config_man = ConfigManager(self.interlock, self.app)
        
        self.heading_cont.append(self.config_man)
        
        self.values_man = ValuesManager(self.interlock, self.app)
        
        self.heading_cont.append(self.values_man)
        
        
        
        self.status = gui.VBox()
        
        self.running = gui.HBox(width = '150pt')
        self.label_running_title = gui.Label('Running: ')
        self.running.append(self.label_running_title)
        self.label_running_state = gui.Label()
        self.running.append(self.label_running_state)
        self.status.append(self.running)

        self.triggered = gui.HBox(width = '150pt')
        self.label_triggered_title = gui.Label('Triggered: ')
        self.triggered.append(self.label_triggered_title)
        self.label_triggered_state = gui.Label()
        self.triggered.append(self.label_triggered_state)
        self.status.append(self.triggered)
        self.heading_cont.append(self.status)
        
        
        #cpu and ram usage
        self.cpu_cont = gui.HBox(width = '150pt')
        self.cpu = gui.Progress()
        self.cpu_cont.append([gui.Label('CPU: ') ,self.cpu])
        self.status.append(self.cpu_cont)
        
        self.ram_cont = gui.HBox(width = '150pt')
        self.ram = gui.Progress()
        self.ram_cont.append([gui.Label('RAM: ') ,self.ram])
        self.status.append(self.ram_cont)
        
        self.update_status()
        
        self.buttons_cont = gui.HBox(width = '200pt')
        self.heading_cont.append(self.buttons_cont)
        
        self.append(self.heading_cont)
        
        ## All interaction buttons
        # starting and stopping botton

        self.bt_start_stop = gui.Button(text = 'Stop', width = "70pt", height = '40pt')
        self.bt_start_stop.style['background-color'] = "red"
        self.buttons_cont.append(self.bt_start_stop)
        
        self.bt_start_stop.onclick.connect(self.start_stop_interlock)

        self.bt_trigger_untrigger = gui.Button(text = 'Trigger', width = "70pt", height = '40pt')
        self.bt_trigger_untrigger.style['background-color'] = "red"
        self.buttons_cont.append(self.bt_trigger_untrigger)
        
        self.bt_trigger_untrigger.onclick.connect(self.trigger_untrigger_interlock)
        
        self.update_buttons()
        
    
    def start_stop_interlock(self, widget):
        if self.interlock.running:
            self.interlock.stop()
        else:
            self.interlock.run()
        self.refresh()
        
    def trigger_untrigger_interlock(self, widget):
        if self.interlock.triggered:
            self.interlock.reset()
        else:
            self.interlock.trigger()
        self.refresh()
    
    def update_buttons(self):
    
        if self.interlock.triggered:
            self.bt_trigger_untrigger.style['background-color'] = 'green'
            self.bt_trigger_untrigger.set_text('Untrigger')
        else:
            self.bt_trigger_untrigger.style['background-color'] = 'red'
            self.bt_trigger_untrigger.set_text('Trigger')
        
        if self.interlock.running:
            self.bt_start_stop.style['background-color'] = 'red'
            self.bt_start_stop.set_text('Stop')
        else:
            self.bt_start_stop.style['background-color'] = 'green'
            self.bt_start_stop.set_text('Start')
    
    def update_status(self):
        if self.interlock.triggered or not self.interlock.running:
            self.label_status.set_text('ERROR !!')
            self.label_status.style['color'] = 'red'
        else:
            self.label_status.set_text('OK')
            self.label_status.style['color'] = 'green'
    
    
        if self.interlock.triggered:
            self.label_triggered_state.set_text('True')
            self.label_triggered_state.style['color'] = 'red'
        else:
            self.label_triggered_state.set_text('False')
            self.label_triggered_state.style['color'] = 'green'
        
        if self.interlock.running:
            self.label_running_state.set_text('True')
            self.label_running_state.style['color'] = 'green'
        else:
            self.label_running_state.set_text('False')
            self.label_running_state.style['color'] = 'red'
            
        
        
        self.cpu.set_value(psutil.cpu_percent())
        self.ram.set_value(psutil.virtual_memory()[2])
    
    def refresh(self):
        self.update_buttons()
        self.update_status()
        
    def reload(self):
        self.refresh()
        self.values_man.reload()
        
class TriggerGUI(gui.HBox):

    def __init__(self, trigger, app, *args, **kwargs):
        super(TriggerGUI, self).__init__(*args, **kwargs)
        
        self.trigger = trigger
        self.input = trigger.input
        self.app = app
        
        self.audio_warned = False
        
        self.style['border-style'] = 'solid'
        
        self.style['padding'] = '2pt'
        self.style['width'] = '160pt'
        
        self.update_border_color()
        
        
        self.title = gui.Label(width = '100%')
        self.update_title()
        self.append(self.title)
        
        
        if self.input.value_type == 'float':
            self.edit_mode = EditSelection(self.get_trigger_mode,self.set_trigger_mode,'trigger if',['greater than', 'smaller than'])
        
            self.append(self.edit_mode)
            
            self.value = gui.Label(str(self.trigger.get_value()), width = '40pt')
            self.append(self.value)
            edit_button = EditFloat(self.get_value, self.set_value, 'value')
            self.append(edit_button)
        if self.input.value_type == 'bool':
            self.edit_mode = EditSelection(self.get_trigger_mode,self.set_trigger_mode,'trigger if',['True', 'False'])
        
            self.append(self.edit_mode)
            
        self.count = gui.Label(str(self.trigger.count), width = '40pt')
        self.append(self.count)
        edit_button = EditFloat(self.get_trigger_count, self.set_trigger_count, 'trigger count')
        self.append(edit_button)
        
    def get_trigger_count(self):
        return self.trigger.trigger_count
        
    def set_trigger_count(self, trigger_count):
        self.trigger.trigger_count = int(trigger_count)
        
    
    def set_value(self, value):
        try:
            self.trigger.set_value(value)
        except:
            pass
        self.value.set_text(str(self.trigger.get_value()))
        
    def get_value(self):
    
        return self.trigger.get_value()
    def update_title(self):
        title = 'Trigger if '+self.trigger.mode
        self.title.set_text(title)
        
    def set_trigger_mode(self, mode):
        self.trigger.set_mode(mode)
        self.update_title()
        
    def get_trigger_mode(self):
        return self.trigger.get_mode()
    
    def update_border_color(self):
        if self.trigger.triggered:
            self.style['border-color'] = 'red'
        
        elif self.trigger.count < self.trigger.trigger_count:
            self.style['border-color'] = 'orange'
            if not self.audio_warned:
                try:
                    if self.input.value_type == 'float':
                        read_text('Warning! '+self.input.username+' is '+self.trigger.mode+' '+str(self.trigger.value)+'! The last read value was '+float_to_string(self.input.last_value)+'.', self.app)
                        
                    if self.input.value_type == 'bool':
                        read_text('Warning! '+self.input.username+' is '+self.trigger.mode+'!', self.app)
                    self.audio_warned = True
                except:
                    pass
        else:
            self.audio_warned = False
            self.style['border-color'] = 'green'
    def update_count(self):
        self.count.set_text(str(self.trigger.count))
        
    def refresh(self):
        self.update_count()
        self.update_border_color()

class TagList(gui.VBox):
    
    def __init__(self, elements = [], *args, **kwargs):
        """
        Args:
            output: output class
        """
        super(TagList, self).__init__(*args, **kwargs)
        self.style['width'] = '100%'
        self.elements = elements
        
        self.reload()   
    
    def reload(self):
        logger.info('reload')
        self.update_tags()
        self.empty()
        for tag in sorted(list(self.tags)):
            self.append(gui.VBox(width = '100%'), tag)
            self.children[tag].append(gui.Label(tag, width = '100%'), 'tag')
            self.children[tag].children['tag'].style['text-align'] = 'left'
            self.children[tag].children['tag'].style['font-size'] = '20pt'
            self.children[tag].children['tag'].style['color'] = 'grey'
            self.children[tag].children['tag'].style['margin-left'] = '1em'
            
            self.children[tag].append(self.get_elements_with_tag(tag))
            
    def add_elements(self, new_elements):
        self.elements += new_elements
        self.reload()
            
    def update_tags(self):
        self.tags = set([element.get_tag() for element in self.elements])
        logger.info(str(self.tags))
        
    def get_elements_with_tag(self, tag):
        return [element for element in self.elements if element.get_tag() == tag]
       
class InputGUI(gui.HBox):

    def __init__(self, input, app,*args, **kwargs):
        """
        Args:
            input: input class
        """
        super(InputGUI, self).__init__(*args, **kwargs)
        
        self.input = input
        self.app = app
        
        self.style['border-bottom'] = '1px solid'
        self.style['width'] = '100%'
        
        self.name = gui.Label(self.input.name, width = '100px')
        self.append(self.name)
        
        self.username_cont = gui.HBox(width = '200px')
        self.username = gui.Label(self.input.username, width = '170px')
        self.username_cont.append(self.username)

        edit_button = EditUsernameTag(self.input.get_username,
                                      self.input.set_username,
                                      self.input.get_tag,
                                      self.input.set_tag,
                                      self.app)
        self.username_cont.append(edit_button)
        self.append(self.username_cont)
        
        self.current_value = gui.Label(width = '100px')
        self.current_value.style['text-align'] = 'center'
        self.update_value()
        
        self.append(self.current_value)
        
        
        self.triggers_cont = gui.Container(width = '60%')
        self.triggers_cont.set_layout_orientation(gui.Container.LAYOUT_HORIZONTAL)
        
        for trigger in self.input.triggers:
            self.add_triggergui(trigger)
            
        self.append(self.triggers_cont)
        
        self.add_trigger_button = gui.Image('/images:plus.svg', height=30, margin='5px')
        self.add_trigger_button.onclick.do(self.add_trigger)
        self.append(self.add_trigger_button)
    
    def add_trigger(self, widget = None):
        
        if self.input.value_type == 'bool':
            gd = GenericDialog(title = 'Add Trigger')
            
            inputmode = gui.DropDown()
            inputmode.append(['True', 'False'])
            
            gd.add_field_with_label('mode', 'mode', inputmode)
            
        if self.input.value_type == 'float':
            gd = GenericDialog(title = 'Add Trigger')
            
            inputmode = gui.DropDown()
            inputmode.append(['smaller than', 'greater than'])
            
            gd.add_field_with_label('mode', 'mode', inputmode)
            
            inputvalue = gui.TextInput()
            
            gd.add_field_with_label('value', 'value', inputvalue)
        
        input_trigger_count = gui.TextInput()
        input_trigger_count.set_text('10')
        gd.add_field_with_label('trigger_count', 'trigger count', input_trigger_count)
        
        self.append(gd)
        
        def register_trigger(widget):
            
            mode = gd.get_field('mode').get_value()
            trigger_count = int(gd.get_field('trigger_count').get_value())
            if self.input.value_type == 'float':
                value = gd.get_field('value').get_value()
                trigger = self.input.add_trigger(mode, float(value), trigger_count )
            if self.input.value_type == 'bool':
                trigger = self.input.add_trigger(mode, None, trigger_count)
            self.add_triggergui(trigger)
            self.remove_child(gd)
        def undo(widget):
            self.remove_child(gd)
        
        gd.set_on_confirm_dialog_listener(register_trigger)
        gd.set_on_cancel_dialog_listener(undo)
        
    def get_tag(self):
        return self.input.get_tag()
    
    def add_triggergui(self, trigger):
        triggerhbox = gui.HBox(width = '200pt')
        
        triggergui = TriggerGUI(trigger, self.app)
        
        triggerhbox.append(triggergui, 'triggergui')
        
        remove_trigger_button = gui.Image('/images:error.svg', height=30, margin='5px')
        remove_trigger_button.trigger = trigger

        triggerhbox.append(remove_trigger_button)

        remove_trigger_button.triggergui_key = self.triggers_cont.append(triggerhbox)
        remove_trigger_button.onclick.do(self.remove_trigger_soft)
    
    def remove_trigger_soft(self, widget):
        
        
        
        
        
        
        check_dialog = GenericDialog(title='Are you sure?')
        self.append(check_dialog)
        check_dialog.trigger = widget.trigger
        check_dialog.triggergui_key = widget.triggergui_key
        
        def remove(widget):
            self.remove_trigger_hard(widget)
            self.remove_child(check_dialog)
            
        def undo(widget):
            self.remove_child(check_dialog)
        
        check_dialog.set_on_confirm_dialog_listener(remove)
        check_dialog.set_on_cancel_dialog_listener(undo)
        
        
    def remove_trigger_hard(self,widget):
            self.input.triggers.remove(widget.trigger)
            self.triggers_cont.remove_child(self.triggers_cont.children[widget.triggergui_key])
             
    def set_username(self, username):
        self.username.text = username
        self.input.set_username(username)
        
    def update_value(self):
        
        value = self.input.last_value
        if self.input.value_type == 'float':
            value = float_to_string(value)
        
        self.current_value.set_text(str(value))
        
    def refresh(self):
        self.update_value()
        
        self.username.set_text(self.input.username)
        
        for triggerhbox in self.triggers_cont.children.values():
            triggerhbox.children['triggergui'].refresh()
            
    def reload(self):
        self.update_value()
        
        self.username.set_text(self.input.username)
        
        self.triggers_cont.empty()
        
        for trigger in self.input.triggers:
            self.add_triggergui(trigger)
               
class InputsExplorer(gui.VBox):
    
    def __init__(self, interlock, app,*args, **kwargs):
        self.interlock = interlock
        self.app = app
        super(InputsExplorer, self).__init__(*args, **kwargs)
        
        self.style.update({'width': '100%'})
        self.style['border-radius'] = '25px'
        self.style['margin-top'] = '1em'
        self.style['padding-top'] = '1em'
        self.style['margin-bottom'] = '1em'
        self.style['padding-bottom'] = '1em'  
    
        
        self.heading = gui.Label('Inputs', height = '30pt')
        
        self.heading.style['font-size'] = '20pt'
        
        self.append(self.heading)

        self.column_label = gui.HBox([gui.Label('Name', width='100px'),
                                      gui.Label('Username', width='200px'),
                                      gui.Label('Normal value', width='100px'),
                                      gui.Label('List of triggers', width='60%'),
                                      gui.Label('', width='40px')], width='100%')
        self.append(self.column_label)
        
        inputguis = [InputGUI(inp, app) for inp in interlock.inputs.values()]
        self.inputs_cont = TagList(inputguis, width = '100%')

        
        self.append(self.inputs_cont)
        
    def refresh(self):
        for input in self.inputs_cont.elements:
            input.refresh()
            
    def reload(self):
        self.inputs_cont.reload()
        
        for input in self.inputs_cont.elements:
            input.reload()

class OutputGUI(gui.HBox):

    def __init__(self, output, app, *args, **kwargs):
        """
        Args:
            output: output class
        """
        super(OutputGUI, self).__init__(*args, **kwargs)
        
        self.output = output
        self.app = app
        
        self.style['border-bottom'] = '1px solid'
        self.style['width'] = '100%'
        
        self.name = gui.Label(self.output.name, width = '100px')
        self.append(self.name)
        
        self.username_cont = gui.HBox(width = '200px')
        self.username = gui.Label(self.output.username, width = '170px')
        self.username_cont.append(self.username)

        edit_button = EditUsernameTag(self.output.get_username,
                                      self.output.set_username,
                                      self.output.get_tag,
                                      self.output.set_tag,
                                      self.app)
        self.username_cont.append(edit_button)
        self.append(self.username_cont)
        
        self.append(self.username_cont)
        
        if self.output.value_type == 'float':
            self.normal_value_cont = gui.HBox(width = '120px')
            self.normal_value = gui.Label(float_to_string(self.output.normal_value), width = '70px')
            self.normal_value.style['text-align'] = 'right'
            self.normal_value_cont.append(self.normal_value)

            edit_button = EditFloat(self.output.get_normal_value, self.set_normal_value, 'normal_value')
            self.normal_value_cont.append(edit_button)
            
            self.append(self.normal_value_cont)
            
            self.triggered_value_cont = gui.HBox(width = '120px')
            
            self.triggered_value = gui.Label(float_to_string(self.output.triggered_value), width = '70px')
            self.triggered_value.style['text-align'] = 'right'
            self.triggered_value_cont.append(self.triggered_value)

            edit_button = EditFloat(self.output.get_triggered_value, self.set_triggered_value, 'triggered_value')
            self.triggered_value_cont.append(edit_button)
            
            self.append(self.triggered_value_cont)
            
            self.value_cont = gui.HBox(width = '120px')
            self.value = gui.Label(width = '70px')
            self.value.style['text-align'] = 'right'
            self.update_value()
            self.value_cont.append(self.value)
            
            edit_button = EditFloat(self.output.get_value, self.set_value, 'value')
            self.value_cont.append(edit_button)
            
            self.append(self.value_cont)
        
        if self.output.value_type == 'bool':
            self.normal_value_cont = gui.HBox(width = '120px')
            self.normal_value = gui.Label(str(self.output.normal_value), width = '70px')
            self.normal_value.style['text-align'] = 'right'
            self.normal_value_cont.append(self.normal_value)

            edit_button = EditBool(self.output.get_normal_value, self.set_normal_value, 'normal_value')
            self.normal_value_cont.append(edit_button)
            
            self.append(self.normal_value_cont)
            
            self.triggered_value_cont = gui.HBox(width = '120px')
            
            self.triggered_value = gui.Label(str(self.output.triggered_value), width = '70px')
            self.triggered_value.style['text-align'] = 'right'
            self.triggered_value_cont.append(self.triggered_value)

            edit_button = EditBool(self.output.get_triggered_value, self.set_triggered_value, 'triggered_value')
            self.triggered_value_cont.append(edit_button)
            
            self.append(self.triggered_value_cont)
            
            self.value_cont = gui.HBox(width = '120px')
            self.value = gui.Label(width = '70px')
            self.value.style['text-align'] = 'right'
            self.update_value()
            self.value_cont.append(self.value)
            
            edit_button = EditBool(self.output.get_value, self.set_value, 'value')
            self.value_cont.append(edit_button)
            
            self.append(self.value_cont)
        
        self.bt_set_to_normal = gui.Button('set normal', width = '100px')
        self.bt_set_to_normal.style['padding'] = '4pt'
        self.bt_set_to_normal.onclick.do(self.set_to_normal)
        self.append(self.bt_set_to_normal)
        
        self.bt_set_to_triggered = gui.Button('set triggered',width = '100px')
        self.bt_set_to_triggered.style['padding'] = '4pt'
        self.bt_set_to_triggered.onclick.do(self.set_to_triggered)
        self.append(self.bt_set_to_triggered)
    
    def update_value(self):
        if self.output.value_type == 'float':
            self.value.set_text(float_to_string(self.output.get_value()))
        if self.output.value_type == 'bool':
            self.value.set_text(str(self.output.get_value()))
    
    def set_to_normal(self, widget):
        self.output.set_to_normal_value()
        self.update_value()
        
    def set_to_triggered(self, widget):
        self.output.set_to_triggered_value()
        self.update_value()
        
    def get_tag(self):
        return self.output.get_tag()
        
    def set_username(self, username):
        self.username.text = username
        self.output.set_username(username)
        
    def set_normal_value(self, normal_value):
        if self.output.value_type == 'float':
            self.normal_value.text = float_to_string(normal_value)
        if self.output.value_type == 'bool':
            self.normal_value.text = str(normal_value)
        self.output.set_normal_value(normal_value)
    
    def set_triggered_value(self, triggered_value):
        if self.output.value_type == 'float':
            self.triggered_value.text = float_to_string(triggered_value)
        if self.output.value_type == 'bool':
            self.triggered_value.text = str(triggered_value)
        self.output.set_triggered_value(triggered_value)
        
    def set_value(self, value):
        if self.output.value_type == 'float':
            self.value.text = float_to_string(value)
        if self.output.value_type == 'bool':
            self.value.text = str(value)
        self.output.set_value(value)
        
    def refresh(self):
        self.update_value()
        
        self.username.set_text(self.output.username)
        if self.output.value_type == 'float':
            self.normal_value.set_text(float_to_string(self.output.normal_value))
            self.triggered_value.set_text(float_to_string(self.output.triggered_value))
        if self.output.value_type == 'bool':
            self.normal_value.set_text(str(self.output.normal_value))
            self.triggered_value.set_text(str(self.output.triggered_value))           
        
    def reload(self):
        self.refresh()

class OutputsExplorer(gui.VBox):
    
    def __init__(self, interlock, app, *args, **kwargs):
        self.interlock = interlock
        self.app = app
        super(OutputsExplorer, self).__init__(*args, **kwargs)
        
        self.style.update({'width': '100%'})
        self.style['border-radius'] = '25px'
        self.style['margin-top'] = '1em'
        self.style['padding-top'] = '1em'
        self.style['margin-bottom'] = '1em'
        self.style['padding-bottom'] = '1em'
    
    
        self.heading = gui.Label('Outputs', height = '30pt')
        
        self.heading.style['font-size'] = '20pt'
        
        self.append(self.heading)

        self.column_label = gui.HBox([gui.Label('Name', width = '100px'),
                                      gui.Label('Username', width = '200px'),
                                      gui.Label('Normal value', width = '120px'),
                                      gui.Label('Triggered value', width = '120px'),
                                      gui.Label('Current value', width = '120px'),
                                      gui.Label('', width = '100px'),
                                      gui.Label('', width = '100px'),], width = '100%')
        self.append(self.column_label)
        outputguis = [OutputGUI(out, self.app) for out in interlock.outputs.values()]
        self.outputs_cont = TagList(outputguis)
        
        self.append(self.outputs_cont)
        
    def refresh(self):
        for output in self.outputs_cont.elements:
            output.refresh()
    
    def reload(self):
        self.outputs_cont.reload()
        for output in self.outputs_cont.elements:
            output.reload()
   
class Edit(gui.HBox):
        
    def __init__(self,*args, **kwargs):
        super(Edit, self).__init__(*args, **kwargs)
        
        self.button_mode()
    
    def button_mode(self):
        self.empty()
        self.edit_button = gui.Image('/images:Edit.ico', height=30, margin='5px')
        self.append(self.edit_button)
        
        def on_click_edit(value):
            self.edit_mode()
            
        self.edit_button.onclick.do(on_click_edit)
        
        
    def edit_mode(self):
        pass

class EditUsernameTag(Edit):
    def __init__(self, get_username, set_username, get_tag, set_tag,app, *args, **kwargs):
        super(EditUsernameTag, self).__init__(*args, **kwargs)
        
        self.get_username = get_username
        self.set_username = set_username
        self.get_tag = get_tag
        self.set_tag = set_tag
        
        self.app = app
        
        
    def edit_mode(self):
        self.empty()   
        self.input = GenericDialog(title = 'Edit')
        
        self.username = gui.TextInput()
        self.username.set_text(self.get_username())
        self.input.add_field_with_label('username',  'username',self.username)
        
        self.tag = gui.TextInput()
        self.tag.set_text(self.get_tag())
        self.input.add_field_with_label('tag',  'tag',self.tag)
        
        self.append(self.input)
        
        def on_cancel(dialog):
            self.button_mode()
            
        def on_confirm(dialog):
            self.set_username(self.username.get_value())
            self.set_tag(self.tag.get_value())
            self.app.reload()
            self.button_mode()
        
        self.input.set_on_cancel_dialog_listener(on_cancel)
        self.input.set_on_confirm_dialog_listener(on_confirm)

class EditSelection(Edit):
        
    def __init__(self, get_function, set_function, name,options,*args, **kwargs):
        super(EditSelection, self).__init__(*args, **kwargs)

        self.set_function = set_function
        self.get_function = get_function
        self.name = name
        self.options = options
        
    def edit_mode(self):
        self.empty()
        #self.remove_child(self.edit_button)
        self.textinput = SelectionInputDialog(self.options,title='Edit', message= self.name, initial_value=self.get_function())
        self.append(self.textinput)

        
        def on_cancel(dialog):
            
            self.button_mode()
            
        def on_confirm(dialog):
            self.set_function(dialog.inputSelection.get_value())
            self.button_mode()
            
        self.textinput.set_on_cancel_dialog_listener(on_cancel)
        self.textinput.set_on_confirm_dialog_listener(on_confirm)

class EditText(Edit):
        
    def __init__(self, get_function, set_function, name,*args, **kwargs):
        super(EditText, self).__init__(*args, **kwargs)

        self.set_function = set_function
        self.get_function = get_function
        self.name = name
        
    def edit_mode(self):
        self.empty()
        #self.remove_child(self.edit_button)
        self.textinput = TextInputDialog(title='Edit', message= self.name, initial_value=str(self.get_function()))
        self.append(self.textinput)

        
        def on_cancel(dialog):
            
            self.button_mode()
            
        def on_confirm(dialog):
            self.set_function(dialog.inputText.get_text())
            self.button_mode()
            
        self.textinput.set_on_cancel_dialog_listener(on_cancel)
        self.textinput.set_on_confirm_dialog_listener(on_confirm)


def float_to_string(val, sig = 3):
    return str(round_sig(val, sig = sig))

def round_sig(x, sig=3):
    if x == 0:
        return 0
    return np.round(x, sig-int(np.floor(np.log10(np.abs(x))))-1)

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False
  
def isint(value):
  try:
    int(value)
    return True
  except ValueError:
    return False

def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError(str(s)+' must be either "True" or "False"')

def isbool(value):
  try:
    str_to_bool(value)
    return True
  except ValueError:
    return False

class EditFloat(Edit):
        
    def __init__(self, get_function, set_function, name,*args, **kwargs):
        super(EditFloat, self).__init__(*args, **kwargs)

        self.set_function = set_function
        self.get_function = get_function
        self.name = name
        
    def edit_mode(self):
        self.empty()
        #self.remove_child(self.edit_button)
        self.textinput = FloatInputDialog(title='Edit', message= self.name, initial_value=str(self.get_function()))
        self.append(self.textinput)

        
        def on_cancel(dialog):
            
            self.button_mode()
            
        def on_confirm(dialog):
            value = dialog.inputText.get_text()
            if isfloat(value):
                self.set_function(float(value))
                self.button_mode()
            else:
                self.textinput.children['message'].set_text('Float !')
                self.textinput.children['message'].style['color'] = 'red'
        self.textinput.set_on_cancel_dialog_listener(on_cancel)
        self.textinput.set_on_confirm_dialog_listener(on_confirm)
        
class EditBool(Edit):
        
    def __init__(self, get_function, set_function, name,*args, **kwargs):
        super(EditBool, self).__init__(*args, **kwargs)

        self.set_function = set_function
        self.get_function = get_function
        self.name = name
        
    def edit_mode(self):
        self.empty()
        #self.remove_child(self.edit_button)
        
        init = str(bool(self.get_function()))
        
        self.textinput = BoolInputDialog(title='Edit', message= self.name, initial_value=init)
        self.append(self.textinput)

        
        def on_cancel(dialog):
            
            self.button_mode()
            
        def on_confirm(dialog):
            value = dialog.inputSelection.get_value()
            
            
            if isbool(value):
                self.set_function(str_to_bool(value))
                self.button_mode()
            else:
                self.textinput.children['message'].set_text('Bool !')
                self.textinput.children['message'].style['color'] = 'red'
        self.textinput.set_on_cancel_dialog_listener(on_cancel)
        self.textinput.set_on_confirm_dialog_listener(on_confirm)

class ConfigSaveDialog(gui.GenericDialog):
    """file selection dialog, it opens a new webpage allows the OK/CANCEL functionality
    implementing the "confirm_value" and "cancel_dialog" events."""

    def __init__(self, title='Save Configuration', message='Select file to overwrite or got folder where to save',selection_folder='.', **kwargs):
        super(ConfigSaveDialog, self).__init__(title, message, **kwargs)

        self.css_width = '475px'
        self.fileFolderNavigator = gui.FileFolderNavigator(False, selection_folder,
                                                       True,
                                                       False)
        self.add_field('fileFolderNavigator', self.fileFolderNavigator)
        
        self.filename = gui.TextInput(initial_value = 'filename')
        
        self.add_field_with_label('filename','filename', self.filename)
        
        self.confirm_dialog.connect(self.confirm_value)
    
    def get_filename(self):
        file = self.fileFolderNavigator.get_selection_list()
        
        if len(file):
            return file[0]
        filename = self.filename.get_text()
        
        if not filename:
            import time
            filename = 'no_name_'+time.strftime("%Y%m%d-%H%M%S")
        
        return os.path.join(self.fileFolderNavigator._last_valid_path, filename+'.iconf')
        
    @gui.decorate_set_on_listener("(self, emitter, fileList)")
    @gui.decorate_event
    def confirm_value(self, widget):
        """event called pressing on OK button.
           propagates the string content of the input field
        """
        self.hide()
        params = (self.fileFolderNavigator.get_selection_list(),)
        return params

    @gui.decorate_explicit_alias_for_listener_registration
    def set_on_confirm_value_listener(self, callback, *userdata):
        self.confirm_value.connect(callback, *userdata)
        
class ValuesSaveDialog(gui.GenericDialog):
    """file selection dialog, it opens a new webpage allows the OK/CANCEL functionality
    implementing the "confirm_value" and "cancel_dialog" events."""

    def __init__(self, title='Save Values', message='Select file to overwrite or got folder where to save',selection_folder='.', **kwargs):
        super(ValuesSaveDialog, self).__init__(title, message, **kwargs)

        self.css_width = '475px'
        self.fileFolderNavigator = gui.FileFolderNavigator(False, selection_folder,
                                                       True,
                                                       False)
        self.add_field('fileFolderNavigator', self.fileFolderNavigator)
        
        self.filename = gui.TextInput(initial_value = 'filename')
        
        self.add_field_with_label('filename','filename', self.filename)
        
        self.confirm_dialog.connect(self.confirm_value)
    
    def get_filename(self):
        file = self.fileFolderNavigator.get_selection_list()
        
        if len(file):
            return file[0]
        filename = self.filename.get_text()
        
        if not filename:
            import time
            filename = 'no_name_'+time.strftime("%Y%m%d-%H%M%S")
        
        return os.path.join(self.fileFolderNavigator._last_valid_path, filename+'.ival')
        
    @gui.decorate_set_on_listener("(self, emitter, fileList)")
    @gui.decorate_event
    def confirm_value(self, widget):
        """event called pressing on OK button.
           propagates the string content of the input field
        """
        self.hide()
        params = (self.fileFolderNavigator.get_selection_list(),)
        return params

    @gui.decorate_explicit_alias_for_listener_registration
    def set_on_confirm_value_listener(self, callback, *userdata):
        self.confirm_value.connect(callback, *userdata)
        
class ConfigManager(gui.Container):

    def __init__(self, interlock, app, *args, **kwargs):
        super(ConfigManager, self).__init__(*args, **kwargs)
        self.style.update({'width': '200pt', 'overflow':'hidden', 'justify-content': 'center'})
        #self.style['border-radius'] = '25px'
        #self.style['margin-top'] = '1em'
        #self.style['padding-top'] = '1em'
        #self.style['margin-bottom'] = '1em'
        #self.style['padding-bottom'] = '1em'
        self.set_layout_orientation(gui.Container.LAYOUT_VERTICAL)
        self.interlock = interlock
        self.app = app
        
        self.append(gui.Label('Config Manager'))
        
        self.bt_save_config = gui.Image('/images:save.ico', height=30, margin = '5pt')
        self.bt_save_config.onclick.do(self.save_config)
        
        self.append(self.bt_save_config)
        
        self.bt_load_config = gui.Image('/images:upload.ico', height=30, margin = '5pt')
        self.bt_load_config.onclick.do(self.load_config)
        
        self.append(self.bt_load_config)
        
        self.dialog_cont = gui.Container()
        
        self.append(self.dialog_cont)
    
    def load_config(self, widget = None):
        
        self.fileexplorer = gui.FileSelectionDialog(selection_folder=self.app.config_folder,multiple_selection = False, allow_file_selection=True, allow_folder_selection=False)
        
        self.fileexplorer.set_on_cancel_dialog_listener(self.cancel)
        self.fileexplorer.set_on_confirm_dialog_listener(self.load_file)
        
        self.fileexplorer.show(self.app)
        
        
    def save_config(self, widget = None):
        self.dialog_cont.empty()
        config = self.interlock.get_config()
        
        self.comment = TextInputDialog(title = 'Save configuration', message = 'Enter comment')
        self.dialog_cont.append(self.comment)

        self.comment.set_on_cancel_dialog_listener(self.cancel)
        self.comment.set_on_confirm_dialog_listener(self.launch_file_explorer_save)
    
    def launch_file_explorer_save(self, widget):
        self.dialog_cont.empty()
        
        self.fileexplorer = ConfigSaveDialog(multiple_selection = False,selection_folder=self.app.config_folder )
        
        self.fileexplorer.set_on_cancel_dialog_listener(self.cancel)
        self.fileexplorer.set_on_confirm_dialog_listener(self.save_file)
        
        self.fileexplorer.show(self.app)
        
    def cancel(self, widget = None):
        self.dialog_cont.empty()
    
    def save_file(self, widget = None):
        filename = self.fileexplorer.get_filename()
        comment = self.comment.inputText.get_text()
        self.interlock.save_config(filename, comment = comment)
        self.dialog_cont.append(gui.Label('File saved to '+('...'+filename[-35:]) if len(filename) > 35 else filename))
        
        
    def load_file(self, widget = None):
        self.dialog_cont.empty()
        file = self.fileexplorer.fileFolderNavigator.get_selection_list()
        if len(file):
            filename = file[0]
            comment = self.interlock.load_config(filename)
            self.app.reload()
            self.dialog_cont.append(gui.Label('Config loaded correctly, comment: '+comment))
        else:
            self.dialog_cont.append(gui.Label('No file was selected'))

class ValuesManager(gui.Container):

    def __init__(self, interlock, app, *args, **kwargs):
        super(ValuesManager, self).__init__(*args, **kwargs)
        self.style.update({'width': '200pt', 'overflow':'hidden', 'justify-content': 'center'})
        #self.style['border-radius'] = '25px'
        #self.style['margin-top'] = '1em'
        #self.style['padding-top'] = '1em'
        #self.style['margin-bottom'] = '1em'
        #self.style['padding-bottom'] = '1em'
        self.set_layout_orientation(gui.Container.LAYOUT_VERTICAL)
        self.interlock = interlock
        self.app = app
        
        self.append(gui.Label('Values Manager'))
        
        self.bt_save_values = gui.Image('/images:save.ico', height=30, margin = '5pt')
        self.bt_save_values.onclick.do(self.save_values)
        
        self.append(self.bt_save_values)
        
        self.bt_reload = gui.Button(text = 'reload')
        self.bt_reload.style['padding'] = '4pt'
        self.bt_reload.onclick.connect(self.reload)
        self.append(self.bt_reload)
        self.dialog_cont = gui.Container()
        
        self.append(self.dialog_cont)
        
        self.values_buttons = gui.Container()
        self.append(self.values_buttons)
        self.make_values_list()
        
        
    def make_values_list(self):
        
        self.values_buttons.empty()
        
        for filename in os.listdir(self.app.values_folder):
            if filename.endswith(".ival"):
                bt = gui.Button(text = filename.split('.')[0], margin = '2pt')
                bt.style['padding'] = '4pt'
                bt.filename = filename
                bt.onclick.connect(self.load_values)
                
                self.values_buttons.append(bt)
    
    def reload(self, widget = None):
        self.make_values_list()
        
    
    def load_values(self, button):
        self.interlock.load_values(os.path.join(self.app.values_folder,button.filename))
        self.app.reload()
        self.reload()
    
    def save_values(self, widget = None):
        self.dialog_cont.empty()
        config = self.interlock.get_config()
        
        self.comment = TextInputDialog(title = 'Save values', message = 'Enter comment')
        self.dialog_cont.append(self.comment)

        self.comment.set_on_cancel_dialog_listener(self.cancel)
        self.comment.set_on_confirm_dialog_listener(self.launch_file_explorer_save)
    
    def launch_file_explorer_save(self, widget):
        self.dialog_cont.empty()
        
        self.fileexplorer = ValuesSaveDialog(multiple_selection = False,selection_folder=self.app.values_folder )
        
        self.fileexplorer.set_on_cancel_dialog_listener(self.cancel)
        self.fileexplorer.set_on_confirm_dialog_listener(self.save_file)
        
        self.fileexplorer.show(self.app)
        
    def cancel(self, widget = None):
        self.dialog_cont.empty()
    
    def save_file(self, widget = None):
        filename = self.fileexplorer.get_filename()
        comment = self.comment.inputText.get_text()
        self.interlock.save_values(filename, comment = comment)
        self.dialog_cont.append(gui.Label('File saved to '+('...'+filename[-35:]) if len(filename) > 35 else filename))
        
class QuEMS_Interlock(App):
    def __init__(self, *args):
        images_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
        audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
        super(QuEMS_Interlock, self).__init__(*args, static_file_path={'images':images_path,'audio':audio_path})

    def main(self, interlock, config_folder = '.', values_folder = '.'):
        
        self.interlock = interlock
        
        self.config_folder = config_folder
        
        self.values_folder = values_folder
        
        self.interlock.add_gui(self)
        
        self.container = gui.Container(width = '100%', height = '100%')
        
        self.container.style['background-color'] = '#e3dbd3'
        
        self.title_cont = gui.HBox(width = '100%')
        
        self.title_cont.style['margin-bottom'] = '2em'
        
        self.title = gui.Label('QuEMS Interlock')
        
        self.title.style['font-size'] = '20pt'
        
        self.title_cont.append(self.title)
        
        self.container.append(self.title_cont)
        
        self.inter_status = InterlockStatus(self.interlock, self)
        self.container.append(self.inter_status)
        
        
        self.inpexp = InputsExplorer(self.interlock, self)
        
        self.container.append(self.inpexp)
        
        self.outexp = OutputsExplorer(self.interlock, self)
        
        self.container.append(self.outexp)

        return self.container
    
    
    
    def refresh(self, widget = None):
        '''
        Function defines how the gui should refresh. This function will be colled by the interlock
        every time there are changes. At the same time the changes are send to influxdb.
        '''
        self.inter_status.refresh()
        self.inpexp.refresh()
        self.outexp.refresh()
        
    def reload(self, widget = None):
        '''
        Function defines how the gui should refresh. This function will be colled by the interlock
        every time there are changes. At the same time the changes are send to influxdb.
        '''
        self.inter_status.reload()
        self.inpexp.reload()
        self.outexp.reload()
    



    
    
