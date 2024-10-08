"""
Created Feb 2024

@author: Benji
"""

from kivy.app import App
from core.logging.logging_system import Logger
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

Builder.load_string(
    """
<ProbingScreen>:
    
    probing_label: probing_label

    canvas:
        Color: 
            rgba: hex('#E5E5E5FF')
        Rectangle: 
            size: self.size
            pos: self.pos         

    BoxLayout: 
        spacing: 0
        padding:[dp(0.05)*app.width, dp(0.0833333333333)*app.height]
        orientation: 'vertical'

        Label:
            font_size: str(0.01875 * app.width) + 'sp'
            size_hint_y: 1

        BoxLayout:
            orientation: 'horizontal'
            spacing:0.025*app.width
            size_hint_y: 1.5

            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint_x: 1
                background_color: hex('#FFFFFF00')
                on_press: root.probe_button_press()
                BoxLayout:
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "z_probe_big.png"
                        size: self.parent.width, self.parent.height
                        allow_stretch: True 
                        
            Label:
                id: probing_label
                size_hint_x: 1.1
                markup: True
                font_size: str(0.0375*app.width) + 'px' 
                valign: 'middle'
                halign: 'center'
                size:self.texture_size
                text_size: self.size
                color: hex('#333333ff')
                        
            Button:
                font_size: str(0.01875 * app.width) + 'sp'
                size_hint_x: 1
                background_color: hex('#FFFFFF00')
                on_press: root.stop_button_press()
                BoxLayout:
                    size: self.parent.size
                    pos: self.parent.pos
                    Image:
                        source: "stop_big.png"
                        size: self.parent.width, self.parent.height
                        allow_stretch: True 
                        
        Label:
            font_size: str(0.01875 * app.width) + 'sp'
            size_hint_y: 1                

"""
)


class ProbingScreen(Screen):
    parent_button = None

    def __init__(self, fast_probe, localization, machine, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.sm = screen_manager
        self.m = machine
        self.l = localization
        self.fp = fast_probe
        self.not_probing = False
        self.alarm_triggered = False
        self.variable_debug = False
        self.function_debug = False
        self.current_dust_shoe_setting = None
        self.usm = App.get_running_app().user_settings_manager

    def update_text(self, string):
        self.probing_label.text = self.l.get_str(string) + "..."

    def on_enter(self):
        self.current_dust_shoe_setting = self.usm.get_value("dust_shoe_detection")
        self.usm.set_value("dust_shoe_detection", False)
        if self.function_debug:
            Logger.debug("**** on_enter called")
        if self.variable_debug:
            Clock.schedule_interval(lambda dt: self.debug_log(), 1)
        delay_time = [0]
        self.update_text("Please wait")
        if self.m.reason_for_machine_pause == "Resuming":
            self.update_text("Probing")
            self.m.reason_for_machine_pause = None
        if self.m.is_spindle_on():
            Logger.warning("Spindle is on, turning off before probing")
            self.m.turn_off_spindle()
            delay_time.append(8)
        if self.m.state().lower() == "run" or self.m.state().lower() == "jog":
            Logger.warning("Machine is running, pausing before probing")
            self.m._grbl_feed_hold()
            Clock.schedule_once(lambda dt: self.m._grbl_soft_reset(), 3.5)
            delay_time.append(4)
        self.probing_event = Clock.schedule_once(
            lambda dt: self.probe(), max(delay_time)
        )
        if not hasattr(self, "watchdog_event"):
            Clock.schedule_once(lambda dt: self.watchdog_clock(), max(delay_time) + 1)
        elif not self.watchdog_event.is_triggered:
            Clock.schedule_once(lambda dt: self.watchdog_clock(), max(delay_time) + 1)
        if self.alarm_triggered:
            Logger.warning("Probing screen exited due to alarm")
            self.exit()

    def probe(self):
        if self.function_debug:
            Logger.debug("**** probing called")
        if self.m.state().lower() == "idle":
            self.m.probe_z(self.fp)
            self.update_text("Probing")
        else:
            Logger.error(f"Machine state is {self.m.state()}, not idle. Cannot probe")

    def watchdog_clock(self):
        if self.function_debug:
            Logger.debug("**** watchdog_clock called")
        self.watchdog_event = Clock.schedule_interval(lambda dt: self.watchdog(), 0.1)

    def watchdog(self):
        if self.function_debug:
            Logger.debug("**** watchdog called")
        machine_state = self.m.state().lower()
        screen = self.sm.current
        screen = str(screen).lower()
        self.not_probing = machine_state != "run"
        self.alarm_triggered = "alarm" in machine_state or "alarm" in screen
        if screen != "probing":
            Clock.unschedule(self.watchdog_event)
        if screen == "probing" and self.alarm_triggered:
            Logger.warning("Probing screen exited due to alarm")
            self.exit()
        if screen == "probing" and self.not_probing:
            Clock.unschedule(self.watchdog_event)
            Clock.schedule_once(lambda dt: self.exit(), 2)
        if self.variable_debug:
            Logger.debug(
                (
                    "Watchdog:\nMachine state: " + machine_state,
                    "Not probing: " + str(self.not_probing),
                    "Alarm triggered: " + str(self.alarm_triggered),
                )
            )

    def probe_button_press(self):
        pass

    def stop_button_press(self):
        if self.function_debug:
            Logger.debug("**** stop_button_press called")
        Logger.info("Probing cancelled by user")
        self.cancel_probing()
        self.exit()

    def cancel_probing(self):
        if self.function_debug:
            Logger.debug("**** cancel_probing called")
        Clock.unschedule(self.probing_event)
        self.m._grbl_feed_hold()
        Clock.schedule_once(lambda dt: self.m._grbl_soft_reset(), 0.5)

    def exit(self):
        self.usm.set_value("dust_shoe_detection", self.current_dust_shoe_setting)
        if self.function_debug:
            Logger.debug("**** exit called")
        if self.sm.current != "probing":
            Logger.warning(
                "Probing screen exited but current screen may not be as expected"
            )
        if hasattr(self, "watchdog_event"):
            if self.watchdog_event.is_triggered:
                Clock.unschedule(self.watchdog_event)
        self.not_probing = False
        self.alarm_triggered = False
        self.parent_button.close_screen()

    def debug_log(self):
        Logger.debug(
            (
                "Current screen: " + self.sm.current,
                "Machine state: " + self.m.state(),
                "Not probing: " + str(self.not_probing),
                "Alarm triggered: " + str(self.alarm_triggered),
                "Watchdog scheduled: " + str(self.watchdog_event.is_triggered)
                if hasattr(self, "watchdog_event")
                else "No watchdog event",
            )
        )
