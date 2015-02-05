import pygame, os, sys, math, random, json
from pygame.locals import *
from Menu import Menu
from Menu import MenuItem
import textwrap

# creates a standardized word box for in-game text and dialogue

class Event(pygame.sprite.Sprite):

    def __init__(self, background, text = None, opt_names = None, opt_fns = None):
        self.background = background
        self.text = text
        self.opt_names = opt_names
        self.opt_fns = opt_fns

        #self.party = {}
        #with open('json/Player.json') as data_file:    
        #    self.reference = json.load(data_file)['characters']

        #if not self.text:
        #    self.reference = {}
        #    with open('json/Text.json') as data_file:    
        #        self.reference = json.load(data_file)['events']

        #    self.text = self.reference['relic']['intro']
        #    self.opt_names = self.reference['relic']['options']
        #    self.outcomes = self.reference['relic']['outcomes']
        #    self.prob = self.reference['relic']['prob']
        #    self.opt_fns = [self.roll, self.roll, self.roll]

        self.desc_window = Rect((75,75), (645, 445))
        self.desc_contents = Rect((105, 95), (600, 405))

        self.font = pygame.font.Font('assets/ui/ftl01.ttf', 16)
        self.color = (255, 255, 255)

        self.options = []
        self.optionsMenu()

        self.active = True

    def roll(self):
        outcome = random.randint(0, 100)
        if outcome > self.prob[0]:
            self.heal()
        elif outcome > self.prob[1]:
            self.hurt()
        else:
            self.killplayer()

    def heal(self):
        self.text = self.reference['relic']['outcomes'][0]
        print self.text

    def hurt(self):
        pass

    def killplayer(self):
        pass

    def draw(self, surface):
        if self.background:
            surface.blit(self.background, (0,0))

        s = pygame.Surface(self.desc_window.size)
        s.set_alpha(90)
        s.fill(0x555555)
        surface.blit(s, self.desc_window.topleft)
        textwrap.textWrap(surface, self.text, self.desc_contents, self.color, self.font)

        for option in self.options:
            option.draw(None, surface)

    def optionsMenu(self):
        color = (255, 255, 255)
        fontSize = 16
        xpos = 400
        ypos = 450
        space = 40

        numopts = len(self.opt_names)
        for i in range (0, numopts):
            newEntry = MenuItem(self.opt_names[i], (xpos, ypos), fontSize, self.background, color, self.opt_fns[i], None, (255,0,0))
            self.options.append(newEntry)
            ypos += space

    def mouse_event(self, event):
        if event.type == pygame.MOUSEMOTION and self.active == True:
            for option in self.options:
                option.highlighted = False
            for option in self.options:
                # check if current event is in the text area
                if option.rect.collidepoint(event.pos):
                    option.highlight()
        elif event.type == pygame.MOUSEBUTTONDOWN: 
            for option in self.options:
                option.mouse_click()
