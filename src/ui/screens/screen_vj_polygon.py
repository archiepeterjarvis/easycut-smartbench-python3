from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

Builder.load_string(
    """

<ScreenVJPolygon>

	polygon_vj: polygon_vj

	BoxLayout:

		PolygonVJ:
			id: polygon_vj

"""
)


class ScreenVJPolygon(Screen):
    polygon_vj = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.polygon_vj.sm = kwargs["screen_manager"]
