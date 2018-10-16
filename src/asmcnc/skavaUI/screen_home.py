'''
Created on 19 Aug 2017

@author: Ed
'''
# config

import kivy
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, ListProperty, NumericProperty # @UnresolvedImport
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from __builtin__ import file
from kivy.clock import Clock

import os, sys

from asmcnc.skavaUI import widget_virtual_bed, widget_status_bar,\
    widget_z_move, widget_xy_move, widget_common_move,\
    widget_quick_commands, widget_virtual_bed_control, widget_gcode_monitor,\
    widget_network_setup, widget_developer_options, widget_gcode_view
from asmcnc.geometry import job_envelope
from time import sleep


Builder.load_string("""

#:import hex kivy.utils.get_color_from_hex
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<HomeScreen>:

    home_image_preview:home_image_preview
    file_data_label:file_data_label
    virtual_bed_container:virtual_bed_container
    status_container:status_container
    z_move_container:z_move_container
    xy_move_container:xy_move_container
    common_move_container:common_move_container
    quick_commands_container:quick_commands_container
    virtual_bed_control_container:virtual_bed_control_container
    gcode_monitor_container:gcode_monitor_container
    network_container:network_container
    developer_container:developer_container
    part_info_label:part_info_label
    home_tab:home_tab
    tab_panel:tab_panel
    pos_tab:pos_tab
    gcode_preview_container:gcode_preview_container

    BoxLayout:
        padding: 0
        spacing: 10
        orientation: "vertical"

        BoxLayout:
            size_hint_y: 0.9 
            padding: 0
            spacing: 10
            orientation: "horizontal"

            BoxLayout:
                size_hint_x: 0.9            
                
                TabbedPanel:
                    id: tab_panel
                    size_hint: 1, 1
                    pos_hint: {'center_x': .5, 'center_y': .5}
                    do_default_tab: False
                    tab_pos: 'left_top'
                    tab_height: 90
                    tab_width: 90
                
                    TabbedPanelItem:
                        background_normal: 'asmcnc/skavaUI/img/tab_set_normal.png'
                        background_down: 'asmcnc/skavaUI/img/tab_set_up.png'
                        BoxLayout:
                            padding: 20
                            spacing: 20
                            canvas:
                                Color: 
                                    rgba: hex('#E5E5E5FF')
                                Rectangle: 
                                    size: self.size
                                    pos: self.pos
                                    
                            Accordion:
                                orientation: 'horizontal'
                        
                                AccordionItem:
                                    title: 'GCode monitor'
                                    collapse: False
                                    id: gcode_monitor_container
    
                                AccordionItem:
                                    title: 'Network'
                                    id: network_container
            
                                AccordionItem:
                                    title: 'Developer'
                                    id: developer_container

    
    
                    TabbedPanelItem:
                        background_normal: 'asmcnc/skavaUI/img/tab_move_normal.png'
                        background_down: 'asmcnc/skavaUI/img/tab_move_up.png'
                        BoxLayout:
                            orientation: 'horizontal'
                            padding: 20
                            spacing: 20
                            canvas:
                                Color: 
                                    rgba: hex('#E5E5E5FF')
                                Rectangle: 
                                    size: self.size
                                    pos: self.pos 
                            
                            BoxLayout:
                                size_hint_x: 3
                                id: xy_move_container
                                canvas:
                                    Color: 
                                        rgba: 1,1,1,1
                                    RoundedRectangle: 
                                        size: self.size
                                        pos: self.pos
                                         
                            BoxLayout:
                                size_hint_x: 1
                                id: common_move_container
    
                            BoxLayout:
                                size_hint_x: 2
                                id: z_move_container
                                canvas:
                                    Color: 
                                        rgba: 1,1,1,1
                                    RoundedRectangle: 
                                        size: self.size
                                        pos: self.pos
    
                                
                    TabbedPanelItem:
                        id: pos_tab
                        background_normal: 'asmcnc/skavaUI/img/tab_pos_normal.png'
                        background_down: 'asmcnc/skavaUI/img/tab_pos_up.png'
                        BoxLayout:
                            orientation: 'vertical'
                            padding: 20
                            spacing: 20
                            canvas:
                                Color: 
                                    rgba: hex('#E5E5E5FF')
                                Rectangle: 
                                    size: self.size
                                    pos: self.pos                        
                                                        
                            BoxLayout:
                                size_hint_y: 5
                                padding: 10
                                canvas:
                                    Color: 
                                        rgba: 1,1,1,1
                                    RoundedRectangle: 
                                        size: self.size
                                        pos: self.pos
                                id: virtual_bed_container                            
                                
                            BoxLayout:
                                size_hint_y: 1
                                id: virtual_bed_control_container
    
                                                
                    TabbedPanelItem:
                        background_normal: 'asmcnc/skavaUI/img/tab_job_normal.png'
                        background_down: 'asmcnc/skavaUI/img/tab_job_up.png'
                        id: home_tab
                        
                        BoxLayout:
                            orientation: 'vertical'
                            padding: 20
                            spacing: 20
                            id: job_container
                            canvas:
                                Color: 
                                    rgba: hex('#E5E5E5FF')
                                Rectangle: 
                                    size: self.size
                                    pos: self.pos 
    
                            BoxLayout:
                                size_hint_y: 1
                                padding: 10
                                spacing: 10
                                orientation: 'horizontal'
                                canvas:
                                    Color: 
                                        rgba: 1,1,1,1
                                    RoundedRectangle: 
                                        size: self.size
                                        pos: self.pos
    
                                Button:
                                    size_hint_x: 1
                                    background_color: hex('#F4433600')
                                    on_release: 
                                        root.manager.transition.direction = 'down'
                                        root.manager.current = 'local_filechooser'
                                        self.background_color = hex('#F4433600')
                                    on_press: 
                                        self.background_color = hex('#F44336FF')
                                    BoxLayout:
                                        padding: 0
                                        size: self.parent.size
                                        pos: self.parent.pos
                                        Image:
                                            source: "./asmcnc/skavaUI/img/load_file.png"
                                            center_x: self.parent.center_x
                                            y: self.parent.y
                                            size: self.parent.width, self.parent.height
                                            allow_stretch: True    
                                Button:
                                    size_hint_x: 1
                                    background_color: hex('#F4433600')
                                    on_release: 
                                        root.manager.current = 'template'
                                        self.background_color = hex('#F4433600')
                                    on_press: 
                                        self.background_color = hex('#F44336FF')
                                    BoxLayout:
                                        padding: 0
                                        size: self.parent.size
                                        pos: self.parent.pos
                                        Image:
                                            source: "./asmcnc/skavaUI/img/template.png"
                                            center_x: self.parent.center_x
                                            y: self.parent.y
                                            size: self.parent.width, self.parent.height
                                            allow_stretch: True  
                                
                                Label:
                                    size_hint_x: 4
                                    color: 0,0,0,1
                                    markup: True 
                                    text: 'Load a file...'
                                    halign: 'left'
                                    id: file_data_label 
                                    text: 'Data'

    
                            BoxLayout:
                                size_hint_y: 3
                                spacing: 20
                                orientation: 'horizontal'
                                                      
                                BoxLayout:
                                    padding: 10
                                    size_hint_x: 1
                                    spacing: 10
                                    orientation: 'vertical'
                                    canvas:
                                        Color: 
                                            rgba: 1,1,1,1
                                        RoundedRectangle: 
                                            size: self.size
                                            pos: self.pos
                                    Image:
                                        source: root.no_image_preview_path
                                        id: home_image_preview
                                    Label:
                                        text: "Test"
                                        id: part_info_label
                                        h_align: 'left'
                                                                       
                                BoxLayout:
                                    size_hint_x: 3
                                    padding: 10
                                    orientation: 'vertical'
                                    canvas:
                                        Color: 
                                            rgba: 1,1,1,1
                                        RoundedRectangle: 
                                            size: self.size
                                            pos: self.pos
                                    id: gcode_preview_container
                
            BoxLayout:
                size_hint_x: 0.1 
                id: quick_commands_container
                
        BoxLayout:
            size_hint_y: 0.08 
            id: status_container

""")


class HomeScreen(Screen):

    no_image_preview_path = 'asmcnc/skavaUI/img/image_preview_inverted.png'
    job_q_dir = 'jobQ/'            # where file is copied if to be used next in job

    def __init__(self, **kwargs):

        super(HomeScreen, self).__init__(**kwargs)
        Clock.schedule_once(lambda *args: self.tab_panel.switch_to(self.home_tab))
        
        self.m=kwargs['machine']
        self.sm=kwargs['screen_manager']
        
        # Job tab
        self.gcode_preview_widget = widget_gcode_view.GCodeView()
        self.gcode_preview_container.add_widget(self.gcode_preview_widget)
        
        # Position tab
        self.virtual_bed_container.add_widget(widget_virtual_bed.VirtualBed(machine=self.m, screen_manager=self.sm))

        # Status bar
        self.status_container.add_widget(widget_status_bar.StatusBar(machine=self.m, screen_manager=self.sm))        
        
        # Bed tab
        self.virtual_bed_control_container.add_widget(widget_virtual_bed_control.VirtualBedControl(machine=self.m, screen_manager=self.sm), index=100)
        
        # Move tab
        self.xy_move_widget = widget_xy_move.XYMove(machine=self.m, screen_manager=self.sm)
        self.common_move_widget = widget_common_move.CommonMove(machine=self.m, screen_manager=self.sm)
        self.xy_move_container.add_widget(self.xy_move_widget)
        self.common_move_container.add_widget(self.common_move_widget)
        self.z_move_container.add_widget(widget_z_move.ZMove(machine=self.m, screen_manager=self.sm))
        
        # Settings tab
        self.gcode_monitor_widget = widget_gcode_monitor.GCodeMonitor(machine=self.m, screen_manager=self.sm)
        self.gcode_monitor_container.add_widget(self.gcode_monitor_widget)
        self.network_container.add_widget(widget_network_setup.NetworkSetup(machine=self.m, screen_manager=self.sm))
        self.developer_widget = widget_developer_options.DevOptions(machine=self.m, screen_manager=self.sm)
        self.developer_container.add_widget(self.developer_widget)
        # Quick commands
        self.quick_commands_container.add_widget(widget_quick_commands.QuickCommands(machine=self.m, screen_manager=self.sm))

    job_box = job_envelope.BoundingBox()
    
        
    def on_enter(self):
        
        #### Scan for files in Q, and update info panels
        
        files_in_q = os.listdir(self.job_q_dir)
        filename = ''
        
          
        if files_in_q:
   
            # Search for preview image in Q dir and show
            for filename in files_in_q:
                if filename.split('.')[1] == 'png': 
                    self.home_image_preview.source = self.job_q_dir + filename
                    break
                else:
                    self.home_image_preview.source = self.no_image_preview_path
               
            # Search for nc file in Q dir and process
            for filename in files_in_q:
                   
                if filename.split('.')[1].startswith(('nc','NC','gcode','GCODE')): 
                       
                    # Set label to include filename
                    self.file_data_label.text = '[b]'+ filename + '[/b]'
                       
                    # Search for tool listings and show
                    job_file = open(self.job_q_dir + filename, 'r')
                    for line in job_file:
                        if line.find('(T') >= 0:
                            self.file_data_label.text += '\n' + line.strip()
                    job_file.close()  
                                       
                    # Refresh bounding box object
                    try:
                        self.job_box.set_job_envelope(self.job_q_dir + filename)
                        self.part_info_label.text = ("X: " + str(self.job_box.range_x[1]-self.job_box.range_x[0]) + 
                                                     "\nY: " + str(self.job_box.range_y[1]-self.job_box.range_y[0]) + 
                                                     "\nZ: " + str(self.job_box.range_z[0]))
                    except:
                        print 'Fail: set job envelope'
                    
                    # Draw gcode preview
                    try:
                        self.gcode_preview_widget.draw_file_in_xy_plane(self.job_q_dir + filename)
                    except:
                        print 'Unable to draw gcode'
                           
                    break
                   
                else:
                    self.file_data_label.text = 'Load a file...'
      
     
        
        
