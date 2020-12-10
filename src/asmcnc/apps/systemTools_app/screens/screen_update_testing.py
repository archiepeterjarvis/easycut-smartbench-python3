'''
Created on 18 November 2020
Update testing screen for system tools app

@author: Letty
'''

from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.screenmanager import ScreenManager, Screen
import sys, os
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.clock import Clock

Builder.load_string("""

<ScrollableLabelOSOutput>:
    scroll_y:1

    canvas.before:
        Color:
            rgba: 0,0,0,1
        Rectangle:
            size: self.size
            pos: self.pos
    
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        font_size: '12sp'
        text: root.text
        max_lines: 3


<UpdateTestingScreen>

    output_view: output_view

    BoxLayout:
        height: dp(800)
        width: dp(480)
        canvas.before:
            Color: 
                rgba: [226 / 255., 226 / 255., 226 / 255., 1.]
            Rectangle: 
                size: self.size
                pos: self.pos

        BoxLayout:
            padding: 10
            spacing: 10
            orientation: "vertical"
            BoxLayout:
                padding: 0
                spacing: 0
                canvas:
                    Color:
                        rgba: [1,1,1,1]
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                Label:
                    size_hint: (None,None)
                    height: dp(70)
                    width: dp(780)
                    text: "Update Testing"
                    color: [0,0,0,1]
                    font_size: 30
                    halign: "center"
                    valign: "bottom"
                    markup: True
       
            BoxLayout:
                size_hint: (None,None)
                width: dp(780)
                height: dp(240)
                padding: 20
                spacing: 0
                orientation: 'vertical'
                canvas:
                    Color:
                        rgba: [1,1,1,1]
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size

                GridLayout: 
                    size: self.size
                    pos: self.parent.pos
                    cols: 4
                    rows: 4
                    size_hint_y: 0.67

                    Button:
                        text: 'Reclone EC from USB'
                                
                    Button:
                        text: 'Reclone EC from web'
                                   
                    Button:
                        text: 'Reclone PL from USB'
                        
                    Button:
                        text: 'Reclone PL from web'

                    Button:
                        text: 'EC Git repair'

                    Button:
                        text: 'EC Hard reset'

                    Button:
                        text: 'PL Git repair'
                                   
                    Button:
                        text: 'PL Hard reset'
                        
                    Button:
                        text: 'Flash FW from USB'

                    Button:
                        text: 'PL Ansible run'

                    Button:
                        text: 'CO platform branch'

                    Button:
                        text: 'CO software branch'
                                   
                    Button:
                        text: 'Pull PL [branch]'
                        
                    Button:
                        text: 'Pull SW [branch]'

                    Button:
                        text: 'Reboot'
                        
                    Button:
                        text: 'Update all'


            BoxLayout:
                size_hint: (None,None)
                width: dp(780)
                height: dp(130)
                padding: 0
                spacing: 10
                orientation: 'horizontal'
                canvas:
                    Color:
                        rgba: [1,1,1,1]
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size

                BoxLayout:
                    size_hint: (None,None)
                    width: dp(192.5)
                    height: dp(130)
                    padding: 0
                    spacing: 0

                    BoxLayout: 
                        size_hint: (None, None)
                        height: dp(130)
                        width: dp(192.5)
                        padding: [52.25,31,52.25,31]
                        Button:
                            size_hint: (None,None)
                            height: dp(68)
                            width: dp(88)
                            background_color: hex('#F4433600')
                            center: self.parent.center
                            pos: self.parent.pos
                            on_press: root.go_back()
                            BoxLayout:
                                padding: 0
                                size: self.parent.size
                                pos: self.parent.pos
                                Image:
                                    source: "./asmcnc/apps/shapeCutter_app/img/arrow_back.png"
                                    center_x: self.parent.center_x
                                    y: self.parent.y
                                    size: self.parent.width, self.parent.height
                                    allow_stretch: True

                BoxLayout:
                    size_hint: (None,None)
                    width: dp(385)
                    height: dp(130)
                    padding: 10
                    spacing: 0
                    orientation: 'vertical'

                    ScrollableLabelOSOutput:
                        id: output_view

                BoxLayout:
                    size_hint: (None,None)
                    width: dp(192.5)
                    height: dp(130)
                    padding: 0
                    spacing: 0    


                    BoxLayout: 
                        size_hint: (None, None)
                        height: dp(130)
                        width: dp(192.5)
                        padding: [40.25,9,40.25,9] 
                        Button:
                            size_hint: (None,None)
                            height: dp(112)
                            width: dp(112)
                            background_color: hex('#F4433600')
                            center: self.parent.center
                            pos: self.parent.pos
                            on_press: root.exit_app()
                            BoxLayout:
                                padding: 0
                                size: self.parent.size
                                pos: self.parent.pos
                                Image:
                                    source: "./asmcnc/apps/systemTools_app/img/exit_system_tools.png"
                                    center_x: self.parent.center_x
                                    y: self.parent.y
                                    size: self.parent.width, self.parent.height
                                    allow_stretch: True
""")

class ScrollableLabelOSOutput(ScrollView):
    text = StringProperty('')

class UpdateTestingScreen(Screen):

    WIDGET_UPDATE_DELAY = 0.2
    output_view_buffer = []

    def __init__(self, **kwargs):
        super(UpdateTestingScreen, self).__init__(**kwargs)
        self.systemtools_sm = kwargs['system_tools']
        self.m = kwargs['machine']

        Clock.schedule_interval(self.update_display_text, self.WIDGET_UPDATE_DELAY)

    def go_back(self):
        self.systemtools_sm.open_system_tools()

    def exit_app(self):
        self.systemtools_sm.exit_app()

    def update_display_text(self, dt):   
        self.output_view.text = '\n'.join(self.output_view_buffer)
        if len(self.output_view_buffer) > 61:
            del self.monitor_text_buffer[0:len(self.output_view_buffer)-60]


# UPDATE FUNCTIONS
