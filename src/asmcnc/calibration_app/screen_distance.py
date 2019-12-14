'''
Created on 12 December 2019
Screen to help user calibrate distances 

@author: Letty
'''

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
import screen_distance2

# from asmcnc.calibration_app import screen_measurement

Builder.load_string("""

<DistanceScreenClass>:

    value_input:value_input
    set_move_label: set_move_label
    test_instructions_label: test_instructions_label
    user_instructions_text: user_instructions_text
    nudge002_button:nudge002_button
    nudge01_button:nudge01_button

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
                        id: nudge01_button
                        size: self.texture_size
                        valign: 'top'
                        halign: 'center'
                        disabled: False
                        # background_color: hex('#a80000FF')
                        on_release: 
                            root.nudge_01()
                            
                        BoxLayout:
                            padding: 5
                            size: self.parent.size
                            pos: self.parent.pos
                            
                            Label:
                                #size_hint_y: 1
                                font_size: '20sp'
                                text: 'Nudge 0.1 mm'

                    Button:
                        size_hint_y:0.9
                        id: nudge002_button
                        size: self.texture_size
                        valign: 'top'
                        halign: 'center'
                        disabled: False
                        # background_color: hex('#a80000FF')
                        on_release: 
                            root.nudge_002()
                            
                        BoxLayout:
                            padding: 5
                            size: self.parent.size
                            pos: self.parent.pos
                            
                            Label:
                                #size_hint_y: 1
                                font_size: '20sp'
                                text: 'Nudge 0.02 mm'


            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 0.6
                
                BoxLayout: 
                    orientation: 'horizontal'
                    TextInput: 
                        id: value_input
                        size_hint_y: 0.4
                        valign: 'middle'
                        halign: 'center'
                        text_size: self.size
                        font_size: '20sp'
                        markup: True
                        input_filter: 'float'
                        multiline: False
                        text: ''
                        on_text_validate: root.save_measured_value()
                        
                    Label: 
                        text_size: self.size
                        text: '[color=000000]  mm[/color]'
                        font_size: '18sp'
                        halign: 'left'
                        valign: 'bottom'
                        markup: True

                Label:
                    id: test_instructions_label
                    text_size: self.size
                    font_size: '18sp'
                    halign: 'center'
                    valign: 'middle'
                    markup: True
                    
                BoxLayout:
                    orientation: 'horizontal'
                    padding: 10
                    size_hint_y: 1
                    
                    Button:
                        size: self.texture_size
                        valign: 'top'
                        halign: 'center'
                        disabled: False
                        on_release: 
                            root.next_instruction()
                            
                        BoxLayout:
                            padding: 5
                            size: self.parent.size
                            pos: self.parent.pos
                            
                            Label:
                                id: set_move_label
                                #size_hint_y: 1
                                font_size: '20sp'
                                text: 'Set and move'
                        
            
""")

class DistanceScreenClass(Screen):

    value_input = ObjectProperty()
    set_move_label = ObjectProperty()
    test_instructions_label = ObjectProperty()
    user_instructions_text = ObjectProperty()
    nudge01_button = ObjectProperty()
    nudge002_button = ObjectProperty()

    nudge_counter = 0
    
    initial_x_cal_move = 1000
    x_cal_measure_1 = NumericProperty()
    x_cal_measure_2 = NumericProperty()  
  
    sub_screen_count = 0
    
    def __init__(self, **kwargs):
        super(DistanceScreenClass, self).__init__(**kwargs)
        self.sm=kwargs['screen_manager']
        self.m=kwargs['machine']

    def on_enter(self):
        
        if self.sub_screen_count == 0:
            self.refresh_screen()
        
    def refresh_screen(self):
        # self.m.jog_absolute_single_axis('X',-1184,9999)
        self.sub_screen_count = 0
        
        self.user_instructions_text.text = '\n\n Push the tape measure up against the guard post, and take an exact measurement against the end plate. \n\n' \
                        ' Do not allow the tape measure to bend. \n\n Use the nudge buttons so that the measurement is precisely up to a millimeter line,' \
                        ' before entering the value on the right.'
                        
        self.test_instructions_label.text = '[color=000000]Enter the value recorded by your tape measure. [/color]'

        self.set_move_label.text = 'Set and move'


    def skip_to_lobby(self):
        self.sm.current = 'lobby'
        
    def nudge_01(self):
        self.m.jog_relative('X',0.1,9999)
        self.nudge_counter += 0.1
        
    def nudge_002(self):
        self.m.jog_relative('X',0.02,9999)
        self.nudge_counter += 0.02

    def save_measured_value(self):
        if self.sub_screen_count == 0:
            if not self.value_input.text == '':
                self.x_cal_measure_1 = float(self.value_input.text)
            else: self.x_cal_measure_1 = 0    
            
        if self.sub_screen_count == 1:
            if not self.value_input.text == '':
                self.x_cal_measure_2 = float(self.value_input.text)
            else: self.x_cal_measure_2 = 0   
    
    # sub-screen 1
    def set_and_move(self):
        # self.m.jog_relative('X', self.initial_x_cal_move, 9999)
        pass
    
    # sub-screen 2
    def set_and_check(self):
        self.final_x_cal_move = self.initial_x_cal_move + self.nudge_total # (machine thinks) 
        self.measured_x_cal_move =  self.x_cal_measure_2 - self.x_cal_measure_1
        
        # get dollar settings
        self.m.get_grbl_settings()
        
        # get setting 100 from serial screen
        self.existing_steps_per_mm = self.m.s.setting_100
        
        #calculate new steps per mm
        self.new_x_steps_per_mm = self.existing_steps_per_mm * ( self.final_x_cal_move / self.measured_x_cal_move )
        
        if self.new_x_steps_per_mm < self.existing_steps_per_mm + 10 and self.new_x_steps_per_mm > self.existing_steps_per_mm - 10:
            self.m.send_any_gcode_command('$100 =' + self.new_x_steps_per_mm)
        else: 
            self.set_move_label.text = 'Error!!'

    def next_instruction(self):
        if self.sub_screen_count == 0:
            self.save_measured_value()
            self.value_input.text = ''
            self.nudge_counter = 0
            self.sub_screen_count = 1
            self.set_move_label.text = 'Set and check'
            self.user_instructions_text.text = 'Using the nudges move the carriage to achieve' \
                                                ' a measurement at the next perfect millimeter increment.'
            self.test_instructions_label.text = 'Enter the value measured'
            self.set_and_move()
            self.next_screen()
            
        elif self.sub_screen_count == 1:
            self.nudge_total = self.nudge_counter            
            self.set_and_check()
            self.nudge_counter = 0            
            self.sub_screen_count = 2
            
        elif self.sub_screen_count == 2: 
            pass

    def repeat_section(self):
        if self.sub_screen_count == 0:
            self.sm.current = 'backlash'
        else:
            self.refresh_screen()

    def skip_section(self):
        self.next_screen()
        
    def next_screen(self):
        
        if not self.sm.has_screen('distance2'):
            distance2_screen = screen_distance2.DistanceScreen2Class(name = 'distance2', screen_manager = self.sm, machine = self.m)
            self.sm.add_widget(distance2_screen)
        self.sm.get_screen('distance2').initial_x_cal_move = self.initial_x_cal_move
        self.sm.get_screen('distance2').x_cal_measure_1 = self.x_cal_measure_1
        self.sm.current = 'distance2'


