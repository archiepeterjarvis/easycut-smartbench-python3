'''
Created on 12 December 2019
Screen 2 to help user calibrate distances

Screen needs to do the following: 

Step 2: Inform user of measurement after machine has moved, and ask user if they want to adjust steps per mm 
Step 4: Report old no. steps vs. new no. steps, and allow user to home and verfiy. 
        They will then need to go through the homing screen, and back to step 1.

@author: Letty
'''

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput

# from asmcnc.calibration_app import screen_measurement

Builder.load_string("""

<DistanceScreen2Class>:

    user_instructions_text: user_instructions_text
    improve_button_label:improve_button_label
    continue_button_label:continue_button_label

    canvas:
        Color: 
            rgba: hex('#FFFFFF')
        Rectangle: 
            size: self.size
            pos: self.pos
             
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 0

        BoxLayout:
            orientation: 'horizontal'
            padding: 0, 0
            spacing: 20
            size_hint_y: 0.2
        
            Button:
                size_hint_y:0.9
                id: getout_button
                size: self.texture_size
                valign: 'top'
                halign: 'center'
                disabled: False
                # background_color: hex('#a80000FF')
                on_release: 
                    root.repeat_section()
                    
                BoxLayout:
                    padding: 5
                    size: self.parent.size
                    pos: self.parent.pos
                    
                    Label:
                        #size_hint_y: 1
                        font_size: '20sp'
                        text: 'Repeat section'

            Button:
                size_hint_y:0.9
                id: getout_button
                size: self.texture_size
                valign: 'top'
                halign: 'center'
                disabled: False
                # background_color: hex('#a80000FF')
                on_release: 
                    root.skip_section()
                    
                BoxLayout:
                    padding: 5
                    size: self.parent.size
                    pos: self.parent.pos
                    
                    Label:
                        #size_hint_y: 1
                        font_size: '20sp'
                        text: 'Skip section'
                        
            Button:
                size_hint_y:0.9
                id: getout_button
                size: self.texture_size
                valign: 'top'
                halign: 'center'
                disabled: False
                # background_color: hex('#a80000FF')
                on_release: 
                    root.skip_to_lobby()
                    
                BoxLayout:
                    padding: 5
                    size: self.parent.size
                    pos: self.parent.pos
                    
                    Label:
                        #size_hint_y: 1
                        font_size: '20sp'
                        text: 'Quit calibration'

        BoxLayout:
            orientation: 'horizontal'
            spacing: 20
            padding: 10

            BoxLayout:
                orientation: 'vertical'
                spacing: 0
                size_hint_x: 1.3
                 
                Label:
                    size_hint_y: 0.3
                    font_size: '35sp'
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                    text: '[color=000000]  X Distance:[/color]'
                    markup: True

                ScrollView:
                    size_hint: 1, 1
                    pos_hint: {'center_x': .5, 'center_y': .5}
                    do_scroll_x: True
                    do_scroll_y: True
                    scroll_type: ['content']
                    
                    RstDocument:
                        id: user_instructions_text
                        background_color: hex('#FFFFFF')
                        
                BoxLayout: 
                    orientation: 'horizontal' 
                    padding: 30
                    spacing: 10
                    
                    Button:
                        size_hint_y:0.9
                        size: self.texture_size
                        valign: 'top'
                        halign: 'center'
                        disabled: False
                        # background_color: hex('#a80000FF')
                        on_release: 
                            root.left_button()
                            
                        BoxLayout:
                            padding: 5
                            size: self.parent.size
                            pos: self.parent.pos
                            
                            Label:
                                id: improve_button_label
                                #size_hint_y: 1
                                font_size: '20sp'
                                text: 'I want to try to improve the result'

                    Button:
                        size_hint_y:0.9

                        valign: 'top'
                        halign: 'center'
                        disabled: False
                        # background_color: hex('#a80000FF')
                        on_release: 
                            root.right_button()
                            
                        BoxLayout:
                            padding: 5
                            size: self.parent.size
                            pos: self.parent.pos
                            
                            Label:
                                id: continue_button_label
                                text_size: self.size
                                text: 'Ok, it measures as expected. Move to the next section.'
                                valign: 'middle'
                                halign: 'center'
                                #markup: True


                        
            
""")

class DistanceScreen2Class(Screen):

    improve_button_label = ObjectProperty()
    continue_button_label = ObjectProperty()
    user_instructions_text = ObjectProperty()
    
    # step 2
    initial_x_cal_move = NumericProperty()
    x_cal_measure_1 = NumericProperty()
    
    # step 4
    old_steps = NumericProperty()
    new_setps = NumericProperty()
    
    sub_screen_count = 0
   
    def __init__(self, **kwargs):
        super(DistanceScreen2Class, self).__init__(**kwargs)
        self.sm=kwargs['screen_manager']
        self.m=kwargs['machine']

    def on_enter(self):
               
        self.set_up_screen()

    def set_up_screen(self):
        
        if self.sub_screen_count == 0: 
            # Step 2: 
            self.user_instructions_text.text = 'Re-measure distance between guard post and end plate. \n\n' \
                            '[b]The distance should measure ' + str(self.initial_x_cal_move + self.x_cal_measure_1) + '[/b]'
            self.improve_button_label.text = 'I want to try to improve the result'
            self.continue_button_label.text = 'OK, it measures as expected. Finish and move to the next section'

        if self.sub_screen_count == 1: 
            # Step 4: 
            self.user_instructions_text.text = 'The old number of steps per mm was : [b]' + str(self.old_steps) + '[/b] \n\n' \
                            'The new number of steps per mm is: [b]' + str(self.new_steps) + '[/b] \n\n' \
                            'You will need to home the machine, and then repeat steps 1 and 2 to verify your results. \n\n' \
                            ' \n [b]WARNING: SETTING THE NEW NUMBER OF STEPS WILL CHANGE HOW THE MACHINE MOVES.[/b] \n\n' \
                            'Would you like to set the new number of steps?'
                            
                            
            self.improve_button_label.text = 'NO - RESTART THIS SECTION'
            self.continue_button_label.text = 'YES - HOME AND VERIFY'
                        

    def left_button(self):
        
        if self.sub_screen_count == 0: # Step 2: Improve result
            self.sub_screen_count = 1
            self.sm.current = 'distance'
        elif self.sub_screen_count == 1: # Step 4: Start over
            self.sub_screen_count = 0
            self.repeat_section()

    def right_button(self):
        if self.sub_screen_count == 0: # Step 2: FINISH & GO TO NEXT SECTION
            self.skip_section(0)
            
        elif self.sub_screen_count == 1: # Step 4: SET, HOME AND VERIFY
            
            # set new steps per mm
            self.m.send_any_gcode_command('$100 = new_steps')
            self.m.get_grbl_settings()
            
            # refresh step 1 for verification
            self.sm.get_screen('distance').refresh_screen_to_step1()
            self.sub_screen_count = 0
            
            # get homing screen
            self.sm.get_screen('homing').return_to_screen = 'distance'
            self.sm.current = 'homing'

    def repeat_section(self):
        if self.sub_screen_count == 0:
            self.sm.current = 'backlash'
        elif self.sub_screen_count == 1:
            self.sm.get_screen('distance').refresh_screen_to_step1()
            self.sub_screen_count = 0
            self.sm.current = 'distance'

    def skip_section(self):
        self.next_screen()
    
    def skip_to_lobby(self):
        self.sm.current = 'lobby'
        
    def next_screen(self):
        self.sub_screen_count = 0        
        # Y STUFF
        self.sm.current = 'backlash'

