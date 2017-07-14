# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
from time import sleep
import wiringpi2 as wiringpi
import midi
import sys

outpin = 21




class TrackData(object):
    """midi track data"""
    events = []
    def __init__(self, events):
        for event_id in range(len(events)):
            self.events.append(events[event_id])

   

class MidiData(object):
    """mid data"""

    resolution = 480
    tracks = []

    def __init__(self, midi_file_path):
        midifile = open(midi_file_path, 'rb')
        self.pattern = midi.read_midifile(midifile)

        self.resolution = self.pattern.resolution
        print( "format is " + str(self.pattern.format))
        
        self.__set_tracks()

    
    def __set_tracks(self):
        for track_id in range(len(self.pattern)):
            track = TrackData(self.pattern[track_id])
            self.tracks.append(track)

    
class MidiSequencer(object):
    tempo = 0
    
    def __init__(self, mididata):
        self.mididata = mididata
        self.tempo = 0

    def execute_event(self, event):
        #print("event type : " + str(type(event)))

        waitSecond = event.tick * (float(self.tempo)/self.mididata.resolution) / 1000000

        #print("test : " + str(float(event.tick)/self.mididata.resolution))
        #print("event.tick : " + str(event.tick))
        #print("resolution: " + str(self.mididata.resolution))
        #print("tempo : " + str(self.tempo))
        #print("wait second : " + str(waitSecond))
        sleep(waitSecond)


        if(isinstance(event, midi.EndOfTrackEvent)):
            return False

        elif(isinstance(event, midi.SetTempoEvent)):
            ms = event.data[0] * pow(16, 4) 
            ms += event.data[1] * pow(16, 2)
            ms += event.data[2]
            self.tempo = ms
            print ("tempo = " + str(ms) + " ms") 

        elif(isinstance(event, midi.NoteOnEvent)):
            velocity = event.data[0]
            pitch = event.data[1]
            wiringpi.softToneWrite(outpin, pitch)
            print("pitch : " + str(pitch))

        elif(isinstance(event, midi.NoteOffEvent)):
            wiringpi.softToneWrite(outpin, 0)

        else:
            print ("ignore this event : " + str(type(event)))

        return True
    








def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(outpin, GPIO.OUT)
    
    wiringpi.wiringPiSetupGpio()
    wiringpi.softToneCreate(outpin)

def close():
    GPIO.cleanup()
    quit()




midifile = "/home/pi/1.mid"


argvs = sys.argv
argc = len(argvs)

if(argc == 2):
    midifile = argvs[1]

elif(argc > 2):
    print "usage: <.mid file>"
    quit()



initialize()

mididata = MidiData(midifile)
sequencer = MidiSequencer(mididata)

for track_id in range(len(mididata.tracks)):
    print("track_id : " + str(track_id))
    if(track_id > 0):
        break;
    track = mididata.tracks[track_id]
    
    #print("track event count = : " + str(len(track.events)))

    for event_id in range(len(track.events)):
        #print("event_id : " + str(event_id))
        event = track.events[event_id]
        sequencer.execute_event(event)            
        
close()




