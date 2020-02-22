import serial
from mingus.midi import fluidsynth 
fluidsynth.init('/home/pi/sf/piano.sf2',"alsa")


filename = 'kick.wav'

ser = serial.Serial('/dev/ttyUSB0', 115200)



while 1: 
    if(ser.in_waiting >0):
        cmd, pitch, velocity = ser.read(), ser.read(), ser.read()
        if (cmd[0]==144):
            if (velocity[0]==127):
                fluidsynth.play_Note(pitch[0],0,100)

                