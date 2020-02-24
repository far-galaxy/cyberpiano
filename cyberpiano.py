import pygame
import serial
import os, sys
from cp_obj import *

from mingus.midi import fluidsynth 

pygame.init()
size=[800,600]
screen=pygame.display.set_mode(size)
pygame.display.set_caption("CyberPiano")

done=False
clock=pygame.time.Clock()

white = (255,255,255)
black = (0,0,0)

screen.fill((100,100,100))

files = os.listdir(os.path.abspath("soundfonts/"))

cur_sf2 = 0
cur_port = 0
selected_port = False

if sys.platform.startswith('win'):
    ports = ['COM%s' % (i + 1) for i in range(1, 256)]
    driver = "dsound"
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    ports = glob.glob('/dev/tty[A-Za-z]*')
    driver = "alsa"
    
    
#'/dev/ttyUSB0'
#ser = serial.Serial(ports[0], 115200)

font_name = pygame.font.match_font('calibri')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, black)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surf.blit(text_surface, text_rect)
    
    
but_port = [Button(screen, 250, 25, 35, 35, white, "<", 32, black), 
            Button(screen, 300, 25, 35, 35, white, ">", 32, black),
            Button(screen, 350, 25, 125, 35, white, "Connect", 32, black)]

but_sf = [Button(screen, 450, 100, 35, 35, white, "<", 32, black), 
            Button(screen, 500, 100, 35, 35, white, ">", 32, black),
            Button(screen, 550, 100, 125, 35, white, "Load", 32, black)]
 
m_cl = False
last_note = 0
while done==False:
    screen.fill((100,100,100))
    # ---- Events start -----------
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        if event.type == pygame.MOUSEBUTTONDOWN: 
            m_cl=True
	
    draw_text(screen, "Port: "+ports[cur_port], 32, 25, 25)
    mouse = pygame.mouse.get_pos()
    
    if m_cl:
        # Port select
        if but_port[0].overed(mouse):
            cur_port -= 1
            
        if but_port[1].overed(mouse):
            cur_port += 1
            
        if but_port[2].overed(mouse):  
            try:
                ser = serial.Serial(ports[cur_port], 115200)
                but_port[2].color = (0, 255, 0)
                selected_port = True
            except:
                but_port[2].color = (255, 0, 0)
                
        #SF2 select
        if but_sf[0].overed(mouse):
            cur_sf2 = (cur_sf2-1) % len(files)
            
        if but_sf[1].overed(mouse):
            cur_sf2 = (cur_sf2+1) % len(files)   
         
        if but_sf[2].overed(mouse):   
            fluidsynth.init('soundfonts/' + files[cur_sf2], driver)
            but_sf[2].color = (0, 255, 0)
                
                
    m_cl = False
    
    draw_text(screen, files[cur_sf2], 32, 25, 100)
    
    
    for i in but_port:
        i.draw()
    for i in but_sf:
        i.draw()    
    
    if selected_port:
        if(ser.in_waiting >0):
            cmd, pitch, velocity = ser.read(), ser.read(), ser.read()
            if (cmd[0]==144):
                if (velocity[0]==127):
                    last_note = pitch[0]
                    fluidsynth.play_Note(pitch[0],0,100)
                    
                if (velocity[0]==127):
                    fluidsynth.play_Note(pitch[0],0,0)
      
    draw_text(screen, "Note: "+str(last_note), 32, 500, 25)
                
    pygame.display.flip()
	
pygame.quit()
