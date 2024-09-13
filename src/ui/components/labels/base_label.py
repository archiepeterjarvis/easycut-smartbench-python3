from kivy.uix.label import Label

from ui.utils.hoverable import HoverBehavior


class LabelBase(Label, HoverBehavior):
    """
    Description:
    This is the base class for all labels that we use in our apps. It offers base functionality that every label needs.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
