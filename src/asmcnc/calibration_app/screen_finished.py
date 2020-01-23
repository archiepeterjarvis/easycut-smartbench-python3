'''
Created on 12 December 2019
Landing Screen for the Calibration App

@author: Letty
'''

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock

# from asmcnc.calibration_app import screen_prep_calibration

Builder.load_string("""

<FinishedCalScreenClass>:

    screen_text:screen_text

    canvas:
        Color: 
            rgba: hex('##FAFAFA')
        Rectangle: 
            size: self.size
            pos: self.pos
             
    BoxLayout:
        orientation: 'horizontal'
        padding: 90,50
        spacing: 0
        size_hint_x: 1

        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.8

            Label:
                id: screen_text
                text_size: self.size
                font_size: '28sp'
                halign: 'center'
                valign: 'middle'
                text: '[color=455A64]Calibration Complete![/color]'
                markup: 'True'
""")

class FinishedCalScreenClass(Screen):
    
    screen_text = ObjectProperty()
    calibration_cancelled = False
    
    def __init__(self, **kwargs):
        super(FinishedCalScreenClass, self).__init__(**kwargs)
        self.sm=kwargs['screen_manager']
        self.m=kwargs['machine']

    def on_enter(self):

        if self.calibration_cancelled == True:
            self.screen_text.text = '[color=455A64]Calibration Cancelled.[/color]'
        else: 
            self.screen_text.text = '[color=455A64]Calibration Complete![/color]'           

        
        self.poll_for_success = Clock.schedule_once(self.exit_screen, 1.5)
        if self.sm.has_screen('measurement'):
            self.sm.remove_widget(self.sm.get_screen('measurement'))
        if self.sm.has_screen('backlash'):
            self.sm.remove_widget(self.sm.get_screen('backlash'))
        if self.sm.has_screen('prep'):
            self.sm.remove_widget(self.sm.get_screen('prep'))
        if self.sm.has_screen('wait'):
            self.sm.remove_widget(self.sm.get_screen('wait'))
        if self.sm.has_screen('calibration_landing'):
            self.sm.remove_widget(self.sm.get_screen('calibration_landing'))
        if self.sm.has_screen('tape_measure_alert'):
            self.sm.remove_widget(self.sm.get_screen('tape_measure_alert'))
        
    def exit_screen(self, dt):
        self.sm.current = 'lobby'
        
    def on_leave(self):
        self.sm.remove_widget(self.sm.get_screen('calibration_complete'))