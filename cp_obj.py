import pygame

class Button():
    def __init__ (self, surf, x, y, w, h, color, text, st, ct):
        self.surf = surf
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.text = text
        self.st = st
        self.ct = ct
        
    def draw(self):
        but = pygame.Rect((self.x, self.y), (self.w, self.h))
        pygame.draw.rect(self.surf, self.color, but)
        
        font = pygame.font.Font(pygame.font.match_font('calibri'), self.st)
        text_surface = font.render(self.text, True, self.ct)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.x+(self.w/2), self.y+(self.h/2))
        self.surf.blit(text_surface, text_rect)
        
    def overed(self, pos):
        if self.x+self.w > pos[0] > self.x and self.y+self.h > pos[1] > self.y:
            return True
        else:
            return False
        
        