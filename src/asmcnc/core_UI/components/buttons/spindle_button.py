import os

from kivy.uix.image import Image

from asmcnc.core_UI import path_utils
from asmcnc.core_UI.components.buttons.button_base import ButtonBase
from asmcnc.core_UI.components.widgets.blinking_widget import BlinkingWidget

SKAVA_UI_PATH = path_utils.get_path("skavaUI")[0]
SKAVA_UI_IMG_PATH = os.path.join(SKAVA_UI_PATH, "img")
SPINDLE_ON_IMAGE = os.path.join(SKAVA_UI_IMG_PATH, "spindle_on.png")
SPINDLE_OFF_IMAGE = os.path.join(SKAVA_UI_IMG_PATH, "spindle_off.png")


class SpindleButton(ButtonBase, BlinkingWidget):
    """A custom button widget used for spindle functionality."""

    background_normal = SPINDLE_OFF_IMAGE
    background_down = SPINDLE_OFF_IMAGE

    border = (0, 0, 0, 0)
    allow_stretch = True

    def __init__(self, router_machine, serial_connection, screen_manager, **kwargs):
        super(SpindleButton, self).__init__(**kwargs)

        self.router_machine = router_machine
        self.serial_connection = serial_connection
        self.screen_manager = screen_manager

        self.image = Image(source=SPINDLE_OFF_IMAGE, size=self.size, pos=self.pos, allow_stretch=True)
        self.add_widget(self.image)

        self.serial_connection.bind(spindle_on=self.__on_spindle_on)
        self.bind(on_press=self.__on_press)

    def __on_press(self, *args):
        """
        Handles what happens when the button is pressed.
        If the spindle is off, it shows the safety popup.
        If the spindle is on, it turns it off.
        :return:
        """
        if not self.serial_connection.spindle_on:
            self.screen_manager.pm.show_spindle_safety_popup(None, self.router_machine.turn_on_spindle)
        else:
            self.router_machine.turn_off_spindle()

    def __on_spindle_on(self, instance, value):
        """
        Callback for the spindle_on event. Changes the button image and starts/stops the blinking.

        :param instance:
        :param value: the new value of the spindle_on property from SerialConnection
        :return: None
        """
        self.image.source = SPINDLE_ON_IMAGE if value else SPINDLE_OFF_IMAGE

        self.blinking = value

