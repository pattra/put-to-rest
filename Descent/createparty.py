import pygame, os, sys, json
from pygame.locals import *
import Room, character, Tile, Grid, Object, Team
import random, astar, time, threading
from Menu import Menu
from Menu import MenuItem
import textwrap

class CreateParty(pygame.sprite.Sprite):
	''' Party creation screen '''
	def load_image(self, image_name):
		try:
			image = pygame.image.load(image_name)
		except pygame.error, message:
			print "Cannot load image: " + image_name
			raise SystemExit, message
		return image.convert_alpha()

	def __init__(self, screen):
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		self.screen = screen
		self.font = pygame.font.Font('assets/ui/ftl01.ttf', 16)

		self.x = 200
		self.y = 400
		self.names = ["Blacksmith", "Miner", "Magician", "Conjurer", "Thief", "Trapper", "Priest", "Blood Priestess", "Reset", "Confirm"]

		# character descriptions
		self.desc_window = Rect((250,100), (510,460))
		self.desc_contents = Rect((265, 110), (480, 440))
		
		self.gametext = {}
		with open('json/Text.json') as data_file:    
			self.gametext = json.load(data_file)['main']
		data_file.close()

		self.desc = self.gametext['charselect']

		self.reference = {}
		with open('json/Characters.json') as data_file:    
			self.reference = json.load(data_file)
		data_file.close()

		self.stats = {}
		with open ('json/Assets.json') as data_file:
			stats = json.load(data_file)['stats']
		data_file.close()

		num_stats = len(stats)
		for i in range (0, num_stats):
			self.stats[i] = pygame.transform.scale(self.load_image(stats[i]),(22,22))

		self.stat_window = Rect((265, 300), (120,165))

		self.party = {}
		self.data = {}
		self.active = True
		self.finished = False
		self.overload = False
		self.noparty = False

		self.background_image = self.load_image("assets/Background.png")
		self.background_image = pygame.transform.scale((self.background_image), (800,600))

		self.options = []
		self.menu = self.makeMenu()

	def makeMenu(self):
		# Load the image
		self.background = None
		color = (100, 100, 100)
		if pygame.font:
			fontSize = 24
			fontSpace = 6
			menuHeight = (fontSize + fontSpace) * 2
			startY = 220

			height = 0
			for name in self.names:
				centerX = 130
				centerY = startY + fontSize + fontSpace
				newEntry = MenuItem(name, (centerX, centerY), fontSize, self.background, color, self.select, name, (255,255,255))
				startY = startY + fontSize + fontSpace
				height = height + fontSize + fontSpace
				self.options.append(newEntry)
			self.y = height

	def select(self, option):
		if option == "Confirm":
			self.confirm()
		elif option == "Reset":
			self.data.clear()
		elif len(self.data) == 4:
			name = option.lower().replace (" ", "_")
			if name in self.data:
				self.data.pop(name, None)
		else:
			#generate base stats
			self.noparty = False
			name = option.lower().replace (" ", "_")

			numnames = len(self.reference[name]['names']) - 1
			charname = self.reference[name]['names'][random.randint(0, numnames)]

			if name in self.data:
				self.data.pop(name, None)
			else:
				self.data[name] = {}
				for key in self.reference[name]:
					if key == 'names':
						self.data[name]['name'] = charname
					else:
						self.data[name][key] = self.reference[name][key]
		self.overload = (len(self.data) == 4)

	def confirm(self):
		if len(self.data) != 0:
			with open('json/Player.json', 'w') as outfile:
				self.party['characters'] = self.data
				self.party['level'] = 1
				json.dump(self.party, outfile)
			outfile.close()
			self.finished = True
		else:
			self.noparty = True

	def draw(self, screen):
		screen.blit(self.background_image, (0,0))
		desc = self.desc 

		if self.overload == True:
			desc = "Five's a crowd. Remove someone from your party before picking someone else."
		if self.noparty == True:
			desc = "Even lone wolves have at least one in the party."

		# Draw transparent backdrop for text
		s = pygame.Surface(self.desc_window.size)
		s.set_alpha(90)
		s.fill(0x555555)
		screen.blit(s,self.desc_window.topleft)
		name = "summary"

		for option in self.options:
			option.draw(self.background, screen)
			if option.highlighted == True:
				if option.text != "Confirm" and option.text != "Reset":
					name = option.text.lower().replace (" ", "_")
					desc = self.reference[name]['desc']
					screen.blit(pygame.transform.scale(self.load_image(self.reference[name]['image']), (64,128)), (100,100))

		self.drawStats(screen, name)
		textwrap.textWrap(self.screen, desc, self.desc_contents, (255,255,255), self.font)

		# Draw characters in party thus far
		x_off = 250 + ( len(self.data)*42 + 510)/2 -42
		for char in self.data:
			screen.blit(pygame.transform.scale(self.load_image(self.reference[char]['image']), (32,64)), (x_off,36))
			x_off -=42

	def drawStats(self, screen, unit):
		text = self.font.render('BASE STATS', 1, (255,255,255))

		font = pygame.font.Font('assets/ui/ftl01.ttf', 16)
		screen.blit(text,self.stat_window.topleft)
		num_stats = len(self.stats)
		ypos = self.stat_window.top + 30
		yoff = 30
		xpos = self.stat_window.left
		x_stat = xpos+30

		stats = self.reference['condensed'][unit]

		# print icons
		for i in range (0, num_stats):
			screen.blit(self.stats[i], (xpos,ypos))
			text = font.render(str(stats[i]), 1, (255,255,255))
			screen.blit(text,(x_stat,ypos-4))
			ypos += yoff

	def handleEvent(self, event):
		if event.type == pygame.MOUSEMOTION and self.active == True:
			eventX = event.pos[0]
			eventY = event.pos[1]
			for option in self.options:
				option.highlighted = False
			for option in self.options:
               	# check if current event is in the text area
				if option.rect.collidepoint(event.pos):
					option.highlight()
		elif event.type == pygame.MOUSEBUTTONDOWN: 
			for option in self.options:
				option.mouse_click()

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
	pygame.display.set_caption('Event Demo')
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
	clock = pygame.time.Clock()
	
	room = Room.Room(0,0,4,4)

	party = CreateParty(screen)

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
		party.handleEvent(event)

		# Redraw the background
		screen.fill(BACKGROUND_COLOR)
		
		# Update and redraw all sprites
		party.draw(screen)

		# Draw the sprites
		pygame.display.update()
