"""
Created July 2020

@author: Letty

Spindle cooldown screen
"""

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

Builder.load_string(
    """

<SpindleCooldownScreen>:

    countdown: countdown
    cool_down_label : cool_down_label

    BoxLayout: 
        spacing: 0
        padding:[dp(0.025)*app.width, dp(0.0416666666667)*app.height]
        orientation: 'vertical'
        size_hint: (None, None)
        height: dp(1.0)*app.height
        width: 1.0*app.width
        canvas:
            Color: 
                rgba: hex('#E5E5E5FF')
            Rectangle: 
                size: self.size
                pos: self.pos         

        BoxLayout: 
            spacing: 0
            padding: 
            orientation: 'vertical'
            canvas:
                Color: 
                    rgba: [1,1,1,1]
                RoundedRectangle:
                    size: self.size
                    pos: self.pos    
            
            Label:
                id: cool_down_label
                size_hint_y: 1
                # text: 'Cooling down spindle...'
                color: [0,0,0,1]
                markup: True
                font_size: str(0.0375*app.width) + 'px' 
                valign: 'middle'
                halign: 'center'
                size:self.texture_size
                text_size: self.size

            BoxLayout: 
                spacing: 0
                padding:[dp(0.125)*app.width, 0, dp(0.125)*app.width, dp(0.270833333333)*app.height]
                orientation: 'horizontal'          
                size_hint: (None, None)
                height: dp(251.0/480.0)*app.height
                width: 1.0*app.width
                pos: self.parent.pos


                BoxLayout: 
                    spacing: 0
                    padding:[dp(0.01)*app.width, 0, dp(0.07125)*app.width, 0]
                    orientation: 'horizontal'          
                    size_hint: (None, None)
                    height: dp(121.0/480.0)*app.height
                    width: 0.225*app.width
                    Image:
                        id: spindle_icon
                        source: "spindle_cooldown_on.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True
                        size_hint: (None, None)
                        height: dp(0.252083333333*app.height)
                        width: dp(0.14375*app.width) 

                BoxLayout: 
                    spacing: 0
                    padding:[0, 0, 0, 0]
                    orientation: 'horizontal'          
                    size_hint: (None, None)
                    height: dp(121.0/480.0)*app.height
                    width: 0.25*app.width
                    Label:
                        id: countdown
                        markup: True
                        font_size: str(0.125*app.width) + 'px' 
                        valign: 'middle'
                        halign: 'center'
                        size:self.texture_size
                        text_size: self.size  
                        text: '10'
                        color: [0,0,0,1]

                BoxLayout: 
                    spacing: 0
                    padding:[dp(0.0875)*app.width, 0, dp(0.0125)*app.width, dp(0.00625)*app.height]
                    orientation: 'horizontal'          
                    size_hint: (None, None)
                    height: dp(121.0/480.0)*app.height
                    width: 0.225*app.width
                    Image:
                        id: countdown_icon
                        source: "countdown_big.png"
                        center_x: self.parent.center_x
                        y: self.parent.y
                        size: self.parent.width, self.parent.height
                        allow_stretch: True
                        size_hint: (None, None)
                        height: dp(0.245833333333*app.height)
                        width: dp(0.125*app.width) 


"""
)


class SpindleCooldownScreen(Screen):
    return_screen = "job_feedback"
    seconds = "10"
    update_timer_event = None

    def __init__(self, localization, machine, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.sm = screen_manager
        self.m = machine
        self.l = localization
        self.seconds = self.m.spindle_cooldown_time_seconds
        self.cool_down_label.text = self.l.get_str("Cooling down spindle") + "..."

    def on_pre_enter(self):
        self.m.cooldown_zUp_and_spindle_on()
        self.seconds = self.m.spindle_cooldown_time_seconds
        self.countdown.text = str(self.seconds)

    def on_enter(self):
        Clock.schedule_once(self.exit_screen, self.seconds)
        self.update_timer_event = Clock.schedule_interval(self.update_timer, 1)

    def exit_screen(self, dt):
        self.sm.current = self.return_screen

    def update_timer(self, dt):
        if self.seconds >= 0:
            self.seconds = self.seconds - 1
            self.countdown.text = str(self.seconds)

    def on_leave(self):
        self.m.turn_off_spindle()
        self.m.turn_off_vacuum()
        if self.update_timer_event != None:
            Clock.unschedule(self.update_timer_event)
        self.seconds = self.m.spindle_cooldown_time_seconds
        self.countdown.text = str(self.seconds)
