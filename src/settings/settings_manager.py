'''
Created 5 March 2020
@author: Letty
Module to get and store settings info
'''

import sys,os

class Settings(object):
    
    sw_version = ''
    sw_hash = ''
    sw_branch = ''
    latest_sw_version = ''
    platform_version = ''
    pl_hash = ''
    pl_branch = ''
    latest_platform_version = ''
    fw_version = ''
    latest_fw_version = ''
    
    def __init__(self):
        
        self.refresh_latest_platform_version()
        self.refresh_platform_version()
        self.refresh_latest_sw_version()
        self.refresh_sw_version()
        
    def refresh_sw_version(self):
        self.sw_version = str((os.popen("git describe --always").read()).split('-')[0])
        self.sw_hash = str(os.popen("git rev-parse --short HEAD").read())
        self.sw_branch = str(os.popen("git branch | grep \*").read())

    def refresh_latest_sw_version(self):
        self.latest_sw_version = str(os.popen("cd /home/pi/easycut-smartbench/ && git fetch --tags --quiet && git describe --tags `git rev-list --tags --max-count=1`").read())

    def refresh_platform_version(self):
        self.platform_version = str(os.popen("cd /home/pi/console-raspi3b-plus-platform/ && git describe --always").read())
        self.pl_hash = str(os.popen("cd /home/pi/console-raspi3b-plus-platform/ && git rev-parse --short HEAD").read())
        self.pl_branch = str(os.popen("cd /home/pi/console-raspi3b-plus-platform/ && git branch | grep \*").read())

    def refresh_latest_platform_version(self):
        self.latest_platform_version = str(os.popen("cd /home/pi/console-raspi3b-plus-platform/ && git fetch --tags --quiet && git describe --tags `git rev-list --tags --max-count=1`").read())

    def get_sw_update(self):
        
        if sys.platform != 'win32':
            if self.latest_sw_version != self.sw_version:
        ##      Update SW according to latest release:
                os.system('sudo sed -i "s/check_config=False/check_config=True/" /home/pi/easycut-smartbench/src/config.txt')
                sed_sw_version = 'sudo sed -i "s/version=' + str(self.sw_version) + '/version=' + str(self.latest_sw_version) + '/" /home/pi/easycut-smartbench/src/config.txt'
                os.system(sed_sw_version)
                os.system('sudo sed -i "s/power_cycle_alert=False/power_cycle_alert=True/" /home/pi/easycut-smartbench/src/config.txt')
                os.system("cd /home/pi/easycut-smartbench/ && git checkout " + self.latest_sw_version)
            else: print "Software already up to date"