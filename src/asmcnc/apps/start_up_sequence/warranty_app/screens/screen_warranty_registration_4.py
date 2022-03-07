'''
Created on nov 2020
@author: Ollie
'''

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import sys, os
from asmcnc.skavaUI import widget_status_bar
Builder.load_string("""

<WarrantyScreen4>:
				
	title_label : title_label
	success_label : success_label
	next_button : next_button

	BoxLayout: 
		size_hint: (None,None)
		width: dp(800)
		height: dp(480)
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
					height: dp(60)
					width: dp(800)
					text: "SmartBench Warranty Registration"
					color: hex('#f9f9f9ff')
					# color: hex('#333333ff') #grey
					font_size: dp(30)
					halign: "center"
					valign: "bottom"
					markup: True

			# BODY
			BoxLayout:
				size_hint: (None,None)
				width: dp(800)
				height: dp(298)
				orientation: 'vertical'

				BoxLayout:
					orientation: 'vertical'
					width: dp(800)
					height: dp(200)
					padding: [dp(20), 0]
					size_hint: (None,None)

					Label:
						id: success_label
						font_size: '30sp'
						text_size: self.size
						valign: 'top'
						halign: 'center'
						markup: 'true'
						bold: True
						color: hex('#333333ff')


			# FOOTER
			BoxLayout: 
				padding: [10,0,10,10]
				size_hint: (None, None)
				height: dp(122)
				width: dp(800)
				orientation: 'horizontal'
				BoxLayout: 
					size_hint: (None, None)
					height: dp(122)
					width: dp(244.5)
					padding: [0, 0, 184.5, 0]
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
					#             source: "./asmcnc/apps/systemTools_app/img/back_to_menu.png"
					#             center_x: self.parent.center_x
					#             y: self.parent.y
					#             size: self.parent.width, self.parent.height
					#             allow_stretch: True

				BoxLayout: 
					size_hint: (None, None)
					height: dp(122)
					width: dp(291)
					padding: [0,0,0,32]
					Button:
						id: next_button
						background_normal: "./asmcnc/skavaUI/img/next.png"
						background_down: "./asmcnc/skavaUI/img/next.png"
						border: [dp(14.5)]*4
						size_hint: (None,None)
						width: dp(291)
						height: dp(79)
						on_press: root.next_screen()
						text: 'Next...'
						font_size: '30sp'
						color: hex('#f9f9f9ff')
						markup: True
						center: self.parent.center
						pos: self.parent.pos
				BoxLayout: 
					size_hint: (None, None)
					height: dp(122)
					width: dp(244.5)
					padding: [193.5, 0, 0, 0]

""")

class WarrantyScreen4(Screen):

	def __init__(self, **kwargs):
		super(WarrantyScreen4, self).__init__(**kwargs)
		self.start_seq=kwargs['start_sequence']
		self.m=kwargs['machine']
		self.l=kwargs['localization']

		self.update_strings()

	def next_screen(self):
		self.start_seq.next_in_sequence()

	def prev_screen(self):
		self.start_seq.prev_in_sequence()

	def update_strings(self):
		self.title_label.text = self.l.get_str("SmartBench Warranty Registration")
		self.success_label.text = self.l.get_str("You have sucessfully completed your warranty registration.")
		self.next_button.text = self.l.get_str("Next") + "..."