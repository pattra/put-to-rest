import pygame, sys, os, random
from pygame.locals import * 

class MenuItem(pygame.font.Font):

    def __init__(self, text, position, fontSize, background, color, function = None, fun_args = None, litecolor = None):
        pygame.font.Font.__init__(self, 'assets/ui/ftl01.ttf', fontSize)
        self.text = text
        self.highlighted = False
        self.color = color
        self.rect = pygame.rect.Rect(position[0],position[1],5,5)
        #self.textSurface = self.render(self.text, 1, self.color, background)
        self.position = position #self.textSurface.get_rect(centerx = position[0], centery = position[1])
        self.function = function
        self.fun_args = fun_args
        self.litecolor = litecolor

    def highlight(self):
        self.highlighted = True

    def draw(self, background, screen):
        ''' Draw the text on the screen '''
        color = self.color
        if self.highlighted:
            if self.litecolor:
                color = self.litecolor
            else:
                color = (0, 0, 255)
        textSurface = self.render(self.text, 1, color)
        self.rect = textSurface.get_rect(centerx = self.position[0], centery = self.position[1])
        screen.blit(textSurface, self.rect)

    def mouse_click(self):
        if self.highlighted:
            if self.function:
                if self.fun_args:
                    self.function(self.fun_args)
                else:
                    self.function()


class Menu:

    MENUCLICKEDEVENT = USEREVENT + 1

    def __init__(self, menuEntries, menuCenter=None):
        '''
        The constructer uses a list of string for the menu entries,
        which need  to be created
        and a menu center if non is defined, the center of the screen is used
        '''
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        # Load the image
        try:
            self.background = pygame.image.load('dusk.jpg').convert_alpha()
        except pygame.error, message:
            print "Cannot load background image!"
            raise SystemExit, message
        #self.background = pygame.Surface(screen.get_size())
        #self.background = self.background.convert()
        #self.background.fill((0, 0, 0))
        self.active = False
        color = (255, 255, 255)

        if pygame.font:
            fontSize = 43
            fontSpace = 6
            menuHeight = (fontSize + fontSpace) * len(menuEntries)
            startY = self.background.get_height() / 2 - menuHeight / 2  
            self.menuEntries = list()

            for menuEntry in menuEntries:
                centerX = self.background.get_width() / 2
                centerY = startY + fontSize + fontSpace
                newEntry = MenuItem(screen, menuEntry, (centerX, centerY), fontSize, self.background, color)
                self.menuEntries.append(newEntry)
                #newEntry.draw(self.background, screen)
                #self.background.blit(newEntry.textSurface, newEntry.position)
                startY = startY + fontSize + fontSpace

    def draw_items(self, screen):
        for menuEntry in self.menuEntries:
            menuEntry.draw(self.background, screen)

    def drawMenu(self, screen):
        self.active = True  
        self.draw_items(screen)         

    def handleEvent(self, event):
        if event.type == pygame.MOUSEMOTION and self.active == True:
            eventX = event.pos[0]
            eventY = event.pos[1]
            for menuItem in self.menuEntries:
                menuItem.highlighted = False
            for menuItem in self.menuEntries:
                # check if current event is in the text area 
                if menuItem.rect.collidepoint(event.pos): 
                    menuItem.highlight()
        elif event.type == pygame.MOUSEBUTTONDOWN: 
            for menuItem in self.menuEntries:
                menuItem.mouse_click()

            
if __name__ == '__main__':
    # pygame initialization
    width = 900
    height = 590

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Main Menu')
    pygame.mouse.set_visible(1)

    # Load the image
    try:
        background = pygame.image.load('dusk.jpg').convert_alpha()
        width = background.get_width()
        height = background.get_height()
    
    except pygame.error, message:
        print "Cannot load background image!"
        raise SystemExit, message

    #background = pygame.Surface(screen.get_size())
    #background = background.convert()
    #background.fill((0, 0, 0))
    clock = pygame.time.Clock()
    
    # draw background
    screen.blit(background, (0, 0))
    pygame.display.flip()
    
    # code for our menu 
    ourMenu = ("Start Game", "Settings", "Quit")

    gameTitle = MenuItem(screen, "Dungeon", (width/2, height/4), 200, background, (255, 0, 0))
 
    myMenu = Menu(ourMenu)
    myMenu.drawMenu(screen)

    # main loop for event handling and drawing
    while True:
        clock.tick(60)

        # Handle Input Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        myMenu.handleEvent(event)

                
        screen.blit(background, (0, 0))    
        if myMenu.active == True:
            myMenu.drawMenu(screen)
            gameTitle.draw(background, screen)
        else:
            background.fill((0, 0, 0))
               
        
        pygame.display.flip()

