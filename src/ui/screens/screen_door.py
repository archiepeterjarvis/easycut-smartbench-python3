"""
Created March 2020

@author: Letty

Screen to handle door command, and allow user to resume.
"""

from core.logging.logging_system import Logger
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

Builder.load_string(
    """

<DoorScreen>:

    countdown_image: countdown_image
    spindle_raise_label: spindle_raise_label
    x_beam: x_beam
    stop_img: stop_img
    resume_button: resume_button
    cancel_button: cancel_button
    header_label: header_label


    canvas:
        Color: 
            rgba: [1, 1, 1, 1]
        Rectangle: 
            size: self.size
            pos: self.pos

    FloatLayout:
        size_hint: (None, None)
        height: dp(0.73125*app.height)
        width: dp(0.62*app.width)
        pos: (dp(148.0/800.0)*app.width, dp(80.0/480.0)*app.height)
        Image:
            id: x_beam
            source: "door_x_beam.png"
            size: self.parent.width, self.parent.height
            pos: self.parent.pos
            allow_stretch: True

    FloatLayout:
        size_hint: (None, None)
        height: dp(0.114583333333*app.height)
        width: dp(0.06875*app.width)
        pos: (dp(270.0/800.0)*app.width, dp(240.0/480.0)*app.height)
        Image:
            id: stop_img
            source: "stop.png"
            size: self.parent.width, self.parent.height
            pos: self.parent.pos
            allow_stretch: True
            opacity: 0

    BoxLayout:
        orientation: 'vertical'
        padding: 0
        spacing: 0
        size_hint: (None, None)
        height: dp(1.0*app.height)
        width: dp(1.0*app.width)

        # Door label
        BoxLayout: 
            padding:[dp(0.01875)*app.width, 0, 0, 0]
            spacing: 0
            size_hint: (None, None)
            height: dp(0.104166666667*app.height)
            width: dp(1.0*app.width)
            Label:
                id: header_label
                size_hint: (None, None)
                font_size: str(0.0375*app.width) + 'sp'
                color: [0,0,0,1]
                markup: True
                halign: 'left'
                height: dp(0.104166666667*app.height)
                width: dp(0.9875*app.width)
                text_size: self.size
                size: self.parent.size
                pos: self.parent.pos

        BoxLayout: 
            padding:[dp(0.0125)*app.width, 0, dp(0.0125)*app.width, 0]
            spacing: 0
            size_hint: (None, None)
            height: dp(0.0104166666667*app.height)
            width: dp(1.0*app.width)
            Image:
                id: red_underline
                source: "red_underline.png"
                center_x: self.parent.center_x
                y: self.parent.y
                size: self.parent.width, self.parent.height
                allow_stretch: True
        
        # Alarm image and text
        BoxLayout: 
            padding: 0
            spacing: 0
            size_hint: (None, None)
            height: dp(0.614583333333*app.height)
            width: dp(1.0*app.width)
            orientation: 'vertical'

            BoxLayout: 
                padding: 0
                spacing: 0
                size_hint: (None, None)
                height: dp(0.510416666667*app.height)
                width: dp(1.0*app.width)
                orientation: 'vertical'

            FloatLayout: 
                padding: 0
                spacing: 0
                size_hint: (None, None)
                height: dp(0.104166666667*app.height)
                width: dp(1.0*app.width)
                orientation: 'vertical'
                pos: (dp(0),dp(130.0/480.0)*app.height)

                canvas:
                    Color: 
                        rgba: [1, 1, 1, 0]
                    Rectangle: 
                        size: self.size
                        pos: self.pos

                Label:
                    id: spindle_raise_label
                    size_hint: (None, None)
                    font_size: str(0.03*app.width) + 'sp'
                    color: [0,0,0,1]
                    markup: True
                    halign: 'center'
                    valign: 'middle'
                    height: dp(0.104166666667*app.height)
                    width: dp(0.9*app.width)
                    text_size: self.size
                    size: self.parent.size
                    x: self.parent.x + 80.0/800*app.width
                    y: self.parent.y
                    opacity: 1

                Image:
                    id: countdown_image
                    source: "countdown_big.png"
                    x: self.parent.x
                    y: self.parent.y
                    height: self.parent.height
                    allow_stretch: True
                    opacity: 0


        BoxLayout:
            orientation: 'horizontal'
            spacing: 0
            size_hint: (None, None)
            height: dp(0.270833333333*app.height)
            width: dp(1.0*app.width)
            padding:[0, 0, 0, dp(0.0208333333333)*app.height]
   

            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                id: cancel_button
                size_hint_x: 1
                background_color: hex('#FFFFFF00')
                on_press: root.cancel_stream()
                disabled: True
                BoxLayout:
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "cancel_from_pause.png"
                        size: self.parent.width, self.parent.height
                        allow_stretch: True
            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                id: resume_button
                size_hint_x: 1
                background_color: hex('#FFFFFF00')
                on_press: root.resume_stream()
                disabled: True
                BoxLayout:
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "resume_from_pause.png"
                        size: self.parent.width, self.parent.height
                        allow_stretch: True 
                

"""
)


class DoorScreen(Screen):
    poll_for_resume = None
    return_to_screen = "home"
    countdown_image = ObjectProperty()
    spindle_raise_label = ObjectProperty()

    def __init__(self, localization, database, job, machine, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.sm = screen_manager
        self.m = machine
        self.jd = job
        self.db = database
        self.l = localization
        self.header_label.text = self.l.get_bold("Interrupt bar pushed!")
        self.spindle_raise_label.text = (
            self.l.get_str("Preparing to resume, please wait") + "..."
        )
        self.anim_spindle_label = (
            Animation(opacity=1, duration=1.5)
            + Animation(opacity=0, duration=0.5)
            + Animation(opacity=0, duration=1.5)
            + Animation(opacity=1, duration=0.5)
        )
        self.anim_countdown_img = (
            Animation(opacity=0, duration=1.5)
            + Animation(opacity=1, duration=0.5)
            + Animation(opacity=1, duration=1.5)
            + Animation(opacity=0, duration=0.5)
        )
        self.anim_stop_bar = (
            Animation(x=150, duration=0.3)
            + Animation(x=153, duration=0.2)
            + Animation(x=151, duration=0.2)
            + Animation(x=152, duration=0.2)
            + Animation(x=152, duration=0.2)
            + Animation(x=152, duration=0.2)
            + Animation(x=152, duration=1.6)
            + Animation(x=140, duration=2)
            + Animation(x=140, duration=2)
        )
        self.anim_stop_img = (
            Animation(opacity=0, duration=0.3)
            + Animation(opacity=1, duration=0.2)
            + Animation(opacity=0.8, duration=0.2)
            + Animation(opacity=1, duration=0.2)
            + Animation(opacity=0.8, duration=0.2)
            + Animation(opacity=1, duration=0.2)
            + Animation(opacity=1, duration=1.6)
            + Animation(opacity=0, duration=2)
            + Animation(opacity=0, duration=2)
        )
        self.anim_spindle_label_end = Animation(opacity=0, duration=0.5)
        self.anim_countdown_img_end = Animation(opacity=0, duration=0.5)

    def on_pre_enter(self):
        self.resume_button.disabled = True
        self.cancel_button.disabled = True
        self.resume_button.opacity = 0
        self.cancel_button.opacity = 0

    def on_enter(self):
        if not str(self.m.state()).startswith("Door:0"):
            Logger.debug(str(self.m.state()))
            self.anim_countdown_img.repeat = True
            self.anim_spindle_label.repeat = True
            Clock.schedule_once(self.start_spindle_label_animation, 1.4)
            self.poll_for_resume = Clock.schedule_interval(
                lambda dt: self.check_spindle_has_raised(), 0.2
            )
        else:
            Clock.schedule_once(self.ready_to_resume, 0.2)
        self.db.send_event(
            1, "Job paused", "Paused job (Interrupt bar pushed): " + self.jd.job_name, 3
        )
        self.start_x_beam_animation(0)

    def on_pre_leave(self):
        if self.poll_for_resume != None:
            Clock.unschedule(self.poll_for_resume)
        self.anim_stop_bar.repeat = False
        self.anim_stop_img.repeat = False

    def on_leave(self):
        self.spindle_raise_label.text = (
            self.l.get_str("Preparing to resume, please wait") + "..."
        )

    def start_x_beam_animation(self, dt):
        self.anim_stop_bar.start(self.x_beam)
        self.anim_stop_img.start(self.stop_img)

    def start_spindle_label_animation(self, dt):
        if not str(self.m.state()).startswith("Door:0"):
            self.anim_spindle_label.start(self.spindle_raise_label)
            self.anim_countdown_img.start(self.countdown_image)

    def check_spindle_has_raised(self):
        if str(self.m.state()).startswith("Door:0") or not str(
            self.m.state()
        ).startswith("Door"):
            Clock.unschedule(self.poll_for_resume)
            self.anim_spindle_label.repeat = False
            self.anim_countdown_img.repeat = False
            self.anim_spindle_label.cancel(self.spindle_raise_label)
            self.anim_countdown_img.cancel(self.countdown_image)
            self.anim_countdown_img_end.start(self.countdown_image)
            Clock.schedule_once(self.ready_to_resume, 0.2)
            self.start_x_beam_animation(1.5)

    def ready_to_resume(self, dt):
        self.resume_button.opacity = 1
        self.cancel_button.opacity = 1
        self.resume_button.disabled = False
        self.cancel_button.disabled = False
        self.anim_stop_bar.repeat = True
        self.anim_stop_img.repeat = True
        self.spindle_raise_label.text = "..." + self.l.get_str("ready to resume")
        self.spindle_raise_label.opacity = 1

    def resume_stream(self):
        self.db.send_event(0, "Job resumed", "Resumed job: " + self.jd.job_name, 4)
        self.m.resume_after_a_hard_door()
        self.return_to_app()

    def cancel_stream(self):
        if self.return_to_screen == "go":
            self.sm.get_screen("job_incomplete").prep_this_screen(
                "cancelled", event_number=False
            )
            self.return_to_screen = "job_incomplete"
        else:
            self.m.s.cancel_sequential_stream(reset_grbl_after_cancel=False)
        self.m.cancel_after_a_hard_door()
        self.return_to_app()

    def return_to_app(self):
        if self.sm.has_screen(self.return_to_screen):
            self.sm.current = self.return_to_screen
        else:
            self.sm.current = "lobby"
