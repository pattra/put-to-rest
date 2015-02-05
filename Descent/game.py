import pygame, os, sys, math, random, json
from pygame.locals import *
import Room, Fight, createparty, floor, Event2
from Menu import Menu
from Menu import MenuItem
import textwrap

def load_image(image_name):
		''' Image loading taken from examples '''
		try:
			image = pygame.image.load(image_name)
		except pygame.error, message:
			print "Cannot load image: " + image_name
			raise SystemExit, message
		return image.convert_alpha()

class Game(pygame.sprite.Sprite):

	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		self.menu_options = []
		self.party_menu = None
		self.rect =  pygame.Rect(0,0,800,600)
		self.background = None
		self.title_font = None
		self.active = True
		self.floor = None
		self.event = None
		self.surface = screen

		self.gametext = {}
		with open('json/Text.json') as data_file:    
			self.gametext = json.load(data_file)['main']
		data_file.close()

		self.party = None
		with open('json/Player.json') as data_file:    
			self.party = json.load(data_file)
		data_file.close()

		self.floor_data = None
		with open('json/Floor.json') as data_file:    
			self.floor_data = json.load(data_file)
		data_file.close()

		self.background_image = load_image("assets/Background.png")
		self.background_image = pygame.transform.scale((self.background_image), (800,600))
		self.make_main_menu()

	def make_main_menu(self):
		# Load the image
		self.background = None
		color = (255, 255, 255)
		if pygame.font:
			fontSize = 24
			fontSpace = 6
			menuHeight = (fontSize + fontSpace) * 2
			startY = 150
			height = 0

			centerX = 120
			centerY = startY + fontSize + fontSpace
			newEntry = MenuItem("New Game", (400, 250), fontSize, \
				self.background, color, self.new_game, None, (255,0,0))
			self.menu_options.append(newEntry)

			if self.party and self.floor_data:
				newEntry = MenuItem("Continue", (400, 300), fontSize, \
					self.background, color, self.continue_game, None, (255,0,0))
			else:
				newEntry = MenuItem("Continue", (400, 300), fontSize, \
					self.background, (100,100,100), self.continue_game, None, (100,100,100))
			self.menu_options.append(newEntry)
			self.title_font = pygame.font.Font('assets/ui/ftl01.ttf', 60)

	def new_game(self,junk = None):
		self.event = Event2.Event(self.background_image, self.gametext['intro'], ['Continue...'], [self.partyCreate])
		self.event.options[0].position = (self.event.options[0].position[0],self.event.options[0].position[1]+25)
		
	def partyCreate(self):
		self.event = None
		self.party_menu = createparty.CreateParty(screen)

	def continue_game(self,junk = None):
		if self.party and self.floor_data:
			self.party_menu = None
			self.floor = floor.Floor(20,20,self.party)
			self.floor.generate_rooms(self.floor_data)

	def draw(self, surface):
		if self.party_menu:
			self.party_menu.draw(surface)
		elif self.event:
			self.event.draw(surface)
		elif self.floor:
			self.floor.draw(surface)
		else:
			# Background
			color = 0x222222
			pygame.draw.rect(surface, color, self.rect)
			surface.blit(self.background_image, (0,0))

			game_over_label = self.title_font.render("Put to Rest" ,True, (255,0,0))
			screen.blit(game_over_label, (215, 100))

			for option in self.menu_options:
				option.draw(self.background, surface)

	def mouse_event(self, event):
		if self.party_menu:
			self.party_menu.handleEvent(event)
		elif self.event:
			self.event.mouse_event(event)
		elif self.floor:
			self.floor.mouse_event(event)
		else:
			if event.type == pygame.MOUSEMOTION and self.active == True:
				for option in self.menu_options:
					option.highlighted = False
				for option in self.menu_options:
					# check if current event is in the text area
					if option.rect.collidepoint(event.pos):
						option.highlight()
			elif event.type == pygame.MOUSEBUTTONDOWN: 
				for option in self.menu_options:
					option.mouse_click()

	def key_event(self, event):
		if self.floor:
			self.floor.key_event(event)

	def toMenu(self):
		self.event = None
		self.clearSave

	def clearSave(self):
		with open('json/Player.json', 'w') as outfile:
			json.dump({}, outfile)
		outfile.close()

	def update(self):
		# Check if chars created
		if self.party_menu:
			self.party_menu.update()
			if self.party_menu.finished:
				self.party = self.party_menu.party
				self.party_menu = None
				self.floor = floor.Floor(20,20,self.party)
				self.floor.generate_rooms()
		elif self.floor:
			self.floor.update()
			if self.floor.game_over:
				self.floor = None
				self.event = Event2.Event(self.background_image, self.gametext['lose'], ['The End?'], [self.toMenu])
			elif self.floor.win:
				self.floor = None
				self.event = Event2.Event(self.background_image, self.gametext['win'], ['To be continued...'], [self.toMenu])


if __name__ == "__main__":
	# Check if sound and font are supported
	if not pygame.font:
		print "Warning, fonts disabled"
	if not pygame.mixer:
		print "Warning, sound disabled"
		
	# Constants
	FPS = 50
	SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
	BACKGROUND_COLOR = (0, 0, 0)
	
	# Initialize Pygame, the clock (for FPS), and a simple counter
	pygame.init()
	pygame.display.set_caption('Put to Rest')
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
	clock = pygame.time.Clock()

	# Control
	game = Game()

	pygame.mixer.music.load('assets/music/explore.mp3')
	pygame.mixer.music.play(-1)

	# Game loop
	while True:
		time_passed = clock.tick(FPS)
		
		# Event handling here (to quit)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				else:
					game.key_event(event)
			elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
				game.mouse_event(event)
		
		# UPDATE
		game.update()

		# Redraw the background
		screen.fill(BACKGROUND_COLOR)
		# DRAW
		game.draw(screen)

		# Draw the sprites
		pygame.display.update()
