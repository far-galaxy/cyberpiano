import pygame
import serial
import os

#from mingus.midi import fluidsynth 

pygame.init()
size=[800,600]
screen=pygame.display.set_mode(size)
pygame.display.set_caption("CyberPiano")

done=False
clock=pygame.time.Clock()

white = (255,255,255)
black = (0,0,0)

screen.fill(white)

files = os.listdir(os.path.abspath("soundfonts/"))
number_file = 0

font_name = pygame.font.match_font('calibri')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, black)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

while done==False:
    # ---- Events start -----------
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
			
    draw_text(screen, files[number_file], 28, 100, 100)
    pygame.display.flip()
	
	
pygame.quit()
