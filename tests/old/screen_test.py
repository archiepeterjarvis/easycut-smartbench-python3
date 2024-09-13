from kivy.config import Config

Config.set("kivy", "keyboard_mode", "systemanddock")
Config.set("graphics", "width", "800")
Config.set("graphics", "height", "480")
Config.set("graphics", "maxfps", "60")
Config.set("kivy", "KIVY_CLOCK", "interrupt")
Config.write()
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from core import localization

try:
    from unittest.mock import Mock
except:
    pass
from apps.system_tools_app.screens.calibration.screen_overnight_test import (
    OvernightTesting,
)

Cmport = "COM3"


class ScreenTest(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        systemtools_sm = Mock()
        systemtools_sm.sm = sm
        l = localization.Localization()
        sett = Mock()
        sett.ip_address = ""
        jd = Mock()
        calibration_db = Mock()
        m = Mock()
        test_screen = OvernightTesting(
            name="overnight_testing",
            m=m,
            systemtools=systemtools_sm,
            calibration_db=calibration_db,
            sm=systemtools_sm.sm,
            l=l,
        )
        sm.add_widget(test_screen)
        sm.current = "overnight_testing"
        return sm


ScreenTest().run()
