from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image

from ui.utils.hoverable import HoverBehavior


class ButtonBase(Button, HoverBehavior):
    """
    The ButtonBase class is the base class for all our buttons we use in our screens and apps.
    It offers base functionality that every button needs e.g. setting the size so that every button looks the same.

    Base classes:
     - kivy.uix.Button
     - HoverBehaviour (to be implemented)

    Additional notes:
    This is an abstract class and must not be instantiated directly!
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_release(self):
        self.record_button_action("on_release")

    def on_press(self):
        self.record_button_action("on_press")


class ImageButtonBase(ButtonBehavior, Image):
    """
    The ImageButton class is a button that uses an image as its background.

    Base classes:
     - kivy.uix.image.Image
     - kivy.uix.behaviors.ButtonBehavior

    Additional notes:
    This is an abstract class and must not be instantiated directly!
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
