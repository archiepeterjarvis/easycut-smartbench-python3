'''
Created on 25 Feb 2019

@author: Letty
'''
import kivy
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, StringProperty # @UnresolvedImport
from kivy.uix.widget import Widget
from __builtin__ import file
from kivy.clock import Clock

import sys, os
from os.path import expanduser
from shutil import copy
from datetime import datetime
import re

from asmcnc.comms import serial_connection
from asmcnc.comms import usb_storage
#from asmcnc.skavaUI import screen_home


# Kivy UI builder:
Builder.load_string("""

<LoadingScreen>:

    load_button:load_button

    canvas:
        Color: 
            rgba: hex('#0d47a1')
        Rectangle: 
            size: self.size
            pos: self.pos
             
    BoxLayout:
        orientation: 'horizontal'
        padding: 70
        spacing: 70
        size_hint_x: 1

        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 1
            spacing: 20
             
            Label:
                size_hint_y: 1
                font_size: '40sp'
                text: '[b]Loading File...[/b]'
                markup: True
 
            Label:
                text_size: self.size
                font_size: '20sp'
                halign: 'center'
                valign: 'top'
                text: 'Something about the file loading; file-name maybe'
                
            Label:
                text_size: self.size
                font_size: '18sp'
                halign: 'center'
                valign: 'middle'
                text: 'ENSURE THAT THE MACHINE IS CLEAR.'
            Label:
                text_size: self.size
                font_size: '18sp'
                halign: 'center'
                valign: 'top'
                text: 'More text'
                
            BoxLayout:
                orientation: 'horizontal'
                padding: 130, 0
            
                Button:
                    size_hint_y:0.9
                    id: load_button
                    size: self.texture_size
                    valign: 'top'
                    halign: 'center'
                    disabled: False
                    background_color: hex('#a80000FF')
#                    on_release: 
                        #root.load_file()

                        
                    BoxLayout:
                        padding: 5
                        size: self.parent.size
                        pos: self.parent.pos
                        
                        Label:
                            #size_hint_y: 1
                            font_size: '20sp'
                            text: 'Load File'
                            
""")

job_cache_dir = './jobCache/'    # where job files are cached for selection (for last used history/easy access)
job_q_dir = './jobQ/'            # where file is copied if to be used next in job

def log(message):
    timestamp = datetime.now()
    print (timestamp.strftime('%H:%M:%S.%f' )[:12] + ' ' + message)

class LoadingScreen(Screen):  
          
# Right lets get this working first and then just shove everything in the File Chooser probably      

    def __init__(self, **kwargs):
        super(LoadingScreen, self).__init__(**kwargs)
        self.sm=kwargs['screen_manager']
        self.m=kwargs['machine']
        self.job_gcode=kwargs['job']
        self.s = serial_connection.SerialConnection(self, self.sm)
        loading_file_name=[]
        
    def on_enter(self):    
               
        # CAD file processing sequence
        self.job_gcode = []
        objectifile = self.objectifiled(self.loading_file_name)        # put file contents into a python object (objectifile)
        self.check_grbl_stream(objectifile)
        self.job_gcode = objectifile
        print self.job_gcode
        # self.m.s.stream_file()
     #   self.write_file_to_JobQ(objectifile)
        
     #   self.preview(objectifile)   # LEAVE OUT
     
     # Instead pass file back to home:
        self.quit_to_home()

    def quit_to_home(self):
        self.sm.get_screen('home').job_gcode = self.job_gcode
        self.sm.current = 'home'
        print('home')

 
    def objectifiled(self, job_file_path):

        log('> load_job_file')
        
        preloaded_job_gcode = []

        job_file = open(job_file_path, 'r')     # open file and copy each line into the object
        
        # clean up code as it's copied into the object
        for line in job_file:
            # Strip comments/spaces/new line and capitalize:
            l_block = re.sub('\s|\(.*?\)', '', (line.strip()).upper())  
            
            if l_block.find('%') == -1 and l_block.find('M6') == -1:    # Drop undesirable lines
                preloaded_job_gcode.append(l_block)  #append cleaned up gcode to object
                
        job_file.close()
        
        log('< load_job_file')
        return preloaded_job_gcode        # a.k.a. objectifile

# NO LONGER REQUIRED -------------------------------------------------------------------------------------  
#     def clean_up_objectifile(self, objectifile):
#         
#         # write cleaned up GRBL to a new file
#         new_file = open(job_q_dir+'LoadedGCode.nc','w')
#         clean_objectifile = []
#         
#         for line in objectifile:
#         # stolen from serial -----------------------
# 
#             # Refine GCode
#             l_block = re.sub('\s|\(.*?\)', '', line.upper()) # Strip comments/spaces/new line and capitalize
#             print(line)
# 
#             if l_block.find('%') == -1 and l_block.find('M6') == -1:  # Drop undesirable lines
#                 new_file.write(l_block)
#                 clean_objectifile.append(l_block)
#          # ----------------------------------------
#         new_file.close()
#         return objectifile
# ------------------------------------------------------------------------------------------------------
 
    def check_grbl_stream(self, objectifile):
       
       # steal from router
       
       # If it doesn't work, need to break it somehow. 
       return objectifile
   
        
    def write_file_to_JobQ(self, objectifile):
        
        files_in_q = os.listdir(job_q_dir) # clean Q
        if files_in_q:
            for file in files_in_q:
                os.remove(job_q_dir+file)

        # write cleaned up g-code to new file
        new_file = open(job_q_dir+'LoadedGCode.nc','w')
        for line in objectifile:
            new_file.write(line)
            new_file.write('\n')
        new_file.close()

        # Move over the preview image (??)
#         if self.preview_image_path:
#             if os.path.isfile(self.preview_image_path):
                
                # ... to Q
#             copy(self.preview_image_path, job_q_dir) # "copy" overwrites same-name file at destination
        
#     def preview(self, objectifile):
#         
#         # can I pass the preview back to the screen_home preview widget? 
#         log(' preview')
#         pass


# this might be necessary but I don't know what it does yet.
    def load_gcode_list(self, filename, gcode_mgr_list):
        
        log ('> get_non_modal_gcode thread')
        #time.sleep(2)
        #for x in range(10000000):
        #    x = x + 1
            #if x % 10000 == 0:
            #    sleep(0.0001)
        #log ('counted')

        gcode_list = self.gcode_preview_widget.get_non_modal_gcode(self.job_q_dir + filename)

        for line in gcode_list:
            gcode_mgr_list.append(line)

        log ('< get_non_modal_gcode thread ' + str(len(gcode_list)))
        return gcode_list
    
    
# OLD ----------------------------------
    
    def stream_file(self):

    #### Scan for files in Q, and update info panels

        files_in_q = os.listdir(self.job_q_dir)
        filename = ''
    
        if files_in_q:
    
            # Search for nc file in Q dir and process
            for filename in files_in_q:
    
                if filename.split('.')[1].startswith(('nc','NC','gcode','GCODE')):
    
                    try:
                        self.m.stream_file(self.job_q_dir + filename)
                    except:
                        print 'Fail: could not stream_file ' + str(self.job_q_dir + filename)
# ----------------------------------
        
# Questions: where does this object need to go? Where do we put it/keep it?
# A: At the moment we don't -> we just move the file and use that explicitly in jobQ I bet.

# Possible: 
#    - Global persistent object that is used instead.
#    - Write to new jobQ file that's all cleaned up and ready to go. << Gonna do this for now.