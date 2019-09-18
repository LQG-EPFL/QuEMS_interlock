import remi.gui as gui
from remi import start, App


def launch(interlock):
    
    def make_interlock_status():
        
        container = gui.Hbox()
        
        return container
    
    def make_input_explorer():
        
        container = gui.VBox()
        
        container.append(gui.Label('Inputs'))
        
        for inp in interlock.inputs:
            inp_cont = gui.HBox()
            
            inp_cont.append(gui.Label('Input '+str(inp.name)))
            
            for i, trigger in enumerate(inp.triggers):
                trig_cont = gui.VBox()
                trig_cont.append(gui.Label('test'))
                inp_cont.append(trig_cont)
            
            print(inp_cont.children)
            container.append(inp_cont)
            
        return container
    
    class MyApp(App):
        def __init__(self, *args):
            super(MyApp, self).__init__(*args)

        def main(self):

            container = gui.VBox()
            self.lbl = gui.Label('QuEMS Interlock')
            
            self.inpexp = make_input_explorer()
            
            self.bt = gui.Button('Press me!')

            # setting the listener for the onclick event of the button
            self.bt.onclick.do(self.on_button_pressed)

            # appending a widget to another, the first argument is a string key
            container.append(self.lbl)
            container.append(self.inpexp)
            container.append(self.bt)

            # returning the root widget
            return container

        # listener function
        def on_button_pressed(self, widget):
            self.lbl.set_text('Button pressed!')
            self.bt.set_text('Hi!')
    # starts the web server
    import remi
    start(MyApp)

