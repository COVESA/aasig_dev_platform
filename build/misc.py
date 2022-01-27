'''
Created on Mar 11, 2022

@author: vladyslav_goncharuk
@brief: Custom automation scenarios for various projects
'''

from paf.paf_impl import Task

class update_diagrams(Task):

    def __init__(self):
        super().__init__()
        self.set_name(update_diagrams.__name__)

    def execute(self):
        self.subprocess_must_succeed("rm -rf /home/vladyslav_goncharuk/Projects/epam/aosp-vhal/md/puml/diagrams; mkdir -p /home/vladyslav_goncharuk/Projects/epam/aosp-vhal/md/puml/diagrams;")
        self.subprocess_must_succeed("adb root")
        self.subprocess_must_succeed('adb shell "pidof epam_android.hardware.automotive.vehicle@2.0-service | xargs kill -SIGUSR1"')
        self.subprocess_must_succeed('cd /home/vladyslav_goncharuk/Projects/epam/aosp-vhal/md/puml/diagrams; adb shell find "/data/vendor/epam/vehicle" -iname "*.puml" | tr -d \'\015\' | while read line; do adb pull "$$line"; done;')
        self.subprocess_must_succeed('java -jar /usr/share/plantuml/plantuml.jar -tsvg ~/Projects/epam/aosp-vhal/md/puml/diagrams/*')