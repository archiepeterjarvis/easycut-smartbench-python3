'''
Created on 16 Nov 2017
@author: Ed
YetiTool's UI for SmartBench
www.yetitool.com
'''

# config
#import os
#os.environ['KIVY_GL_BACKEND'] = 'sdl2'
import time

from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemanddock')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window

from asmcnc.comms import router_machine 
# NB: router_machine imports serial_connection

from asmcnc.skavaUI import screen_inital, screen_help
from asmcnc.skavaUI import screen_home
from asmcnc.skavaUI import screen_local_filechooser
from asmcnc.skavaUI import screen_usb_filechooser
from asmcnc.skavaUI import screen_go
from asmcnc.skavaUI import screen_template
from asmcnc.skavaUI import screen_lobby
from asmcnc.skavaUI import screen_vj_polygon
from asmcnc.skavaUI import screen_file_loading
from asmcnc.skavaUI import screen_alarm_proto
from asmcnc.skavaUI import screen_error_proto

Cmport = 'COM3'

class SkavaUI(App):

    def build(self):

        print("Starting " + time.strftime('%H:%M:%S'))
        # Establish screens
        sm = ScreenManager(transition=NoTransition())

        # Initialise 'm'achine object
        m = router_machine.RouterMachine(Cmport, sm)
        
        job_gcode = []  # declare g-code object
        
        # initialise the screens
        lobby_screen = screen_lobby.LobbyScreen(name='lobby', screen_manager = sm, machine = m)
        home_screen = screen_home.HomeScreen(name='home', screen_manager = sm, machine = m, job = job_gcode)
        local_filechooser = screen_local_filechooser.LocalFileChooser(name='local_filechooser', screen_manager = sm)
        usb_filechooser = screen_usb_filechooser.USBFileChooser(name='usb_filechooser', screen_manager = sm)
        go_screen = screen_go.GoScreen(name='go', screen_manager = sm, machine = m, job = job_gcode)
        template_screen = screen_template.TemplateScreen(name='template', screen_manager = sm)
        vj_polygon_screen = screen_vj_polygon.ScreenVJPolygon(name='vj_polygon', screen_manager = sm)
        loading_screen = screen_file_loading.LoadingScreen(name = 'loading', screen_manager = sm, machine =m, job = job_gcode)
        alarm_screen = screen_alarm_proto.AlarmScreenClass(name='alarmScreen', screen_manager = sm, machine = m, alarmmsg='')
        error_screen = screen_error_proto.ErrorScreenClass(name='errorScreen', screen_manager = sm, machine = m, errormsg = '')
           
        
        # add the screens to screen manager
        sm.add_widget(lobby_screen)
        sm.add_widget(home_screen)
        sm.add_widget(local_filechooser)
        sm.add_widget(usb_filechooser)
        sm.add_widget(go_screen)
        sm.add_widget(template_screen)
        sm.add_widget(vj_polygon_screen)
        sm.add_widget(loading_screen)
        sm.add_widget(alarm_screen)
        sm.add_widget(error_screen)


        # set screen to start on
        sm.current = 'lobby'
        return sm


if __name__ == '__main__':

    SkavaUI().run()
