"""
Created on 26 Jul 2021
@author: Dennis
Widget to display gcode as an alternative to a drawing
"""

from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.properties import StringProperty

Builder.load_string(
    """

<ScrollViewGCode>:

    text_container: text_container

    Label:
        font_size: str(0.01875 * app.width) + 'sp'
        id: text_container
        color: [0, 0, 0, 1]
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        markup: True

<GCodeSummary>:

    gcode_scrollview: gcode_scrollview

    BoxLayout:
        size: self.parent.size
        pos: self.parent.pos

        ScrollViewGCode:
            id: gcode_scrollview

"""
)


class ScrollViewGCode(ScrollView):
    text = StringProperty("")


class GCodeSummary(Widget):
    def __init__(self, job, **kwargs):
        super().__init__(**kwargs)
        self.jd = job

    def display_summary(self):
        self.gcode_scrollview.text_container.text = self.jd.gcode_summary_string

    def hide_summary(self):
        self.gcode_scrollview.text_container.text = ""
