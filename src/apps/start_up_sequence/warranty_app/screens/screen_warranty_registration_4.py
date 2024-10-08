"""
Created on nov 2020
@author: Ollie
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

Builder.load_string(
    """

<WarrantyScreen4>:
				
	title_label : title_label
	success_label : success_label
	next_button : next_button

	BoxLayout: 
		size_hint: (None,None)
		width: dp(1.0*app.width)
		height: dp(1.0*app.height)
		orientation: 'vertical'

		canvas:
			Color:
				rgba: hex('##e5e5e5')
			Rectangle:
				size: self.size
				pos: self.pos

		BoxLayout:
			padding: 0
			spacing: 0
			orientation: "vertical"

			# HEADER
			BoxLayout:
				padding: 0
				spacing: 0
				canvas:
					Color:
						rgba: hex('#1976d2ff')
					Rectangle:
						pos: self.pos
						size: self.size
				Label:
					id: title_label
					size_hint: (None,None)
					height: dp(0.125*app.height)
					width: dp(1.0*app.width)
					text: "SmartBench Warranty Registration"
					color: hex('#f9f9f9ff')
					# color: hex('#333333ff') #grey
					font_size: dp(0.0375*app.width)
					halign: "center"
					valign: "bottom"
					markup: True

			# BODY
			BoxLayout:
				size_hint: (None,None)
				width: dp(1.0*app.width)
				height: dp(0.620833333333*app.height)
				orientation: 'vertical'

				BoxLayout:
					orientation: 'vertical'
					width: dp(1.0*app.width)
					height: dp(0.416666666667*app.height)
					padding:[dp(0.025)*app.width, 0]
					size_hint: (None,None)

					Label:
						id: success_label
						font_size: str(0.0375*app.width) + 'sp'
						text_size: self.size
						valign: 'top'
						halign: 'center'
						markup: 'true'
						color: hex('#333333ff')


			# FOOTER
			BoxLayout: 
				padding:[dp(0.0125)*app.width, 0, dp(0.0125)*app.width, dp(0.0208333333333)*app.height]
				size_hint: (None, None)
				height: dp(0.254166666667*app.height)
				width: dp(1.0*app.width)
				orientation: 'horizontal'
				BoxLayout: 
					size_hint: (None, None)
					height: dp(0.254166666667*app.height)
					width: dp(0.305625*app.width)
					padding:[0, 0, dp(0.230625)*app.width, 0]
					# Button:
					#     size_hint: (None,None)
					#     height: dp(52)
					#     width: dp(60)
					#     background_color: hex('#F4433600')
					#     center: self.parent.center
					#     pos: self.parent.pos
					#     on_press: root.prev_screen()
					#     BoxLayout:
					#         padding: 0
					#         size: self.parent.size
					#         pos: self.parent.pos
					#         Image:
					#             source: "back_to_menu.png"
					#             center_x: self.parent.center_x
					#             y: self.parent.y
					#             size: self.parent.width, self.parent.height
					#             allow_stretch: True

				BoxLayout: 
					size_hint: (None, None)
					height: dp(0.254166666667*app.height)
					width: dp(0.36375*app.width)
					padding:[0, 0, 0, dp(0.0666666666667)*app.height]
					Button:
						id: next_button
						background_normal: "next.png"
						background_down: "next.png"
						border: [dp(14.5)]*4
						size_hint: (None,None)
						width: dp(0.36375*app.width)
						height: dp(0.164583333333*app.height)
						on_press: root.next_screen()
						text: 'Next...'
						font_size: str(0.0375*app.width) + 'sp'
						color: hex('#f9f9f9ff')
						markup: True
						center: self.parent.center
						pos: self.parent.pos
				BoxLayout: 
					size_hint: (None, None)
					height: dp(0.254166666667*app.height)
					width: dp(0.305625*app.width)
					padding:[dp(0.241875)*app.width, 0, 0, 0]

"""
)


class WarrantyScreen4(Screen):
    def __init__(self, localization, machine, start_sequence, **kwargs):
        super().__init__(**kwargs)
        self.start_seq = start_sequence
        self.m = machine
        self.l = localization
        self.update_strings()

    def next_screen(self):
        self.start_seq.next_in_sequence()

    def prev_screen(self):
        self.start_seq.prev_in_sequence()

    def update_strings(self):
        self.title_label.text = self.l.get_str("SmartBench Warranty Registration")
        self.success_label.text = self.l.get_bold(
            "You have successfully completed your warranty registration."
        )
        self.next_button.text = self.l.get_str("Next") + "..."
