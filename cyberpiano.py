import pygame
import serial
import os, sys
from cp_obj import *
from mingus.midi import fluidsynth 

#---------------------Caption-----------------------------
pygame.init()
size=[800,600]
screen=pygame.display.set_mode(size)
pygame.display.set_caption("CyberPiano")
programIcon = pygame.image.load('icon.png')
pygame.display.set_icon(programIcon)
clock=pygame.time.Clock()


#---------------------Colors-----------------------------
white = (255, 255, 255)
black = (  0,   0,   0)
bg =    (100, 100, 100)


files = os.listdir(os.path.abspath("soundfonts/"))


done=False
cur_sf2 = 0
cur_port = 0
instrument = 0
selected_port = False
loaded_sf = False
m_cl = False
last_note = 0


# Check system
if sys.platform.startswith('win'):
    ports = ['COM%s' % (i + 1) for i in range(1, 256)]
    driver = "dsound"
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    ports = glob.glob('/dev/tty[A-Za-z]*')
    driver = "alsa"
    
synth = fluidsynth.FluidSynthSequencer()
synth.init()
synth.start_audio_output(driver)


#--------------------------------Buttons-----------------------------------------    
but_port = [Button(screen, 250, 25, 35, 35, white, "<", 32, black), 
            Button(screen, 300, 25, 35, 35, white, ">", 32, black),
            Button(screen, 350, 25, 150, 35, white, "Connect", 32, black)]

but_sf = [Button(screen, 25, 210, 100, 100, white, "<", 72, black), 
          Button(screen, 145, 210, 100, 100, white, ">", 72, black),
          Button(screen, 25, 330, 220, 100, white, "Load", 48, black)]

but_ins = [Button(screen, 275, 210, 100, 100, white, "<", 72, black), 
          Button(screen, 395, 210, 100, 100, white, ">", 72, black)]
 

while done==False:
    screen.fill(bg)
    
    
    # ---- Events start -----------
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        if event.type == pygame.MOUSEBUTTONDOWN: 
            m_cl=True
	
    
    
    mouse = pygame.mouse.get_pos()
    
    if m_cl:
        # Port select
        if but_port[0].overed(mouse):
            cur_port -= 1
            
        if but_port[1].overed(mouse):
            cur_port += 1
            
        if but_port[2].overed(mouse) and not selected_port:  
            try:
                ser = serial.Serial(ports[cur_port], 115200)
                but_port[2].color = (0, 255, 0)
                but_port[2].text = "Connected"
                selected_port = True
            except:
                but_port[2].color = (255, 0, 0)
                
        #SF2 select
        if but_sf[0].overed(mouse):
            cur_sf2 = (cur_sf2-1) % len(files)
            but_sf[2].color = white
            
        if but_sf[1].overed(mouse):
            cur_sf2 = (cur_sf2+1) % len(files)
            but_sf[2].color = white
         
        if but_sf[2].overed(mouse): 
            synth.load_sound_font('soundfonts/' + files[cur_sf2])
            but_sf[2].color = (0, 255, 0)
            instrument = 0
            synth.set_instrument(0, 0)
            

         
         #Instrument select   
        if but_ins[0].overed(mouse):
            instrument = (instrument-1) % 256
            synth.set_instrument(0, instrument)
             
        if but_ins[1].overed(mouse):
            instrument = (instrument+1) % 256 
            synth.set_instrument(0, instrument)
                
    m_cl = False
    
    # Drawning
    draw_text(screen, "Preset:", 32, 25, 100)
    draw_text(screen, files[cur_sf2][:-4], 32, 25, 150)
    draw_text(screen, "Port: "+ports[cur_port], 32, 25, 25)
    draw_text(screen, "Note: "+str(last_note), 32, 525, 100)
    draw_text(screen, "Insrument: "+str(instrument), 32, 525, 150)
    
    for i in but_port: i.draw()
    for i in but_sf: i.draw()  
    for i in but_ins: i.draw() 
    pygame.display.flip()
    
    # Read piano
    if selected_port:
        if(ser.in_waiting >0):
            cmd, pitch, velocity = ser.read(), ser.read(), ser.read()
            if (cmd[0]==144):
                if (velocity[0]==127):
                    last_note = pitch[0]
                    synth.play_event(pitch[0],0,100)
                    
                if (velocity[0]==0):
                    synth.play_event(pitch[0],0,0)
      
    
                
    
	
pygame.quit()
