import pygame, os, sys, json
from pygame.locals import *
import Room, character, Tile, Grid, Object, Team
import Fight 
import random, astar, time, threading
from Menu import Menu
from Menu import MenuItem

class EventMenu(pygame.sprite.Sprite):
	"menu once you encounter an object"

	def __init__(self, eventType, screen):
		'comment'
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		self.screen = screen

		with open('json/Player.json') as data_file:    
			self.units = json.load(data_file)['characters']
		data_file.close()
		# Load the image
		try:
			self.background = pygame.image.load('dusk.jpg').convert_alpha()
		except pygame.error, message:
			print "Cannot load background image!"
			raise SystemExit, message
		
		self.x = 200
		self.y = 400
		self.color = (0, 0, 0)

		if eventType == "change_level":
			self.change_level()
		elif eventType == "treasure":
			self.treasure()
		elif eventType == "fight":
			self.fight()	
		elif eventType == "character":
			self.character()
		elif eventType == "trickster":
			self.trickster()
		elif eventType == "gold":
			self.gold()
		elif eventType == "mice":
			self.mice()
		elif eventType == "bats":
			self.bats()		
		elif eventType == "light":
			self.light()	
		elif eventType == "rock":
			self.rock()
		elif eventType == "leak":
			self.leak()
		elif eventType == "object":
			self.object()
		elif eventType == "horse":
			self.horse()
		elif eventType == "armour":
			self.armour()
		elif eventType == "clay":
			self.clay()
		else:
			self.description = 	MenuItem(self.screen, "Empty Room", (self.x+175, self.y-250), 50, self.background, (255,0,0))
			self.options = ("OK", "")

		self.active = True
		self.menu = self.makeMenu(self.options)
		

		for self.option in self.options:
			if self.option.text == "Touch":
				self.option.function = self.hurt_one
			elif self.option.text == "Take":
				self.option.function = self.hurt_all
			elif self.option.text == "Run Away":
				self.option.function = self.run_away
			else:
				self.option.function = self.hurt_random

	def makeMenu(self, options):
		
		if pygame.font:
			fontSize = 40
			fontSpace = 6
			self.menuHeight = (fontSize + fontSpace) * len(options)
			startY = self.screen.get_width() / 2 -self.menuHeight / 2
			#startY = room.rect.height * 2 - self.menuHeight / 2  
			self.options = list()
			height = 0
			for option in options:
				centerX = self.screen.get_width() / 2
				centerY = startY + fontSize + fontSpace
				#second round of functions
				if option == "OK":
					newEntry = MenuItem(screen, option, (centerX, centerY), fontSize, self.background, self.color, self.leave_room)
				else:	
					newEntry = MenuItem(screen, option, (centerX, centerY), fontSize, self.background, self.color)
				self.options.append(newEntry)
				startY = startY + fontSize + fontSpace
				height = height + fontSize + fontSpace
				
			self.y = height				

	def draw(self):
		for option in self.options:
			option.draw(self.background, self.screen)

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

#ACTIONS
	def hurt_one(self):
		font = pygame.font.Font(None, 20)
		#print self.units[0].name + " was hurt"
		#screen.blit(font.render(self.units[0].name, 1, (255, 255, 255)), (self.x, self.y))
		#self.units[0].health - 1
		self.options = ("OK", "")
		self.makeMenu(self.options)
		self.description.text = "Someone in your party has been hurt"


	def hurt_all(self):
		print "hurt_all"
		#length = len(self.units)
		#for i in range (0, length):
		#	self.units[i].health - 
		self.options = ("OK", "")
		self.makeMenu(self.options)
		self.description.text = "Everyone in your party has been hurt"


	def hurt_random(self):
		print "hurt_random"
		length = len(self.units) - 1 
		#print self.units[random.randint(0, length)]['name']
		#self.units[random.randint(0, length)].health - 1
		self.options = ("OK", "")
		self.makeMenu(self.options)
		self.description.text = "Someone in your party has been hurt"


	def run_away(self):
		self.options = ("OK", "")
		self.makeMenu(self.options)
		self.description.text = "Ran away to safety"

	def leave_room(self):
		print "left room"

#EVENTS
	def change_level(self):
		# Load the image
		try:
			self.background = pygame.transform.scale(pygame.image.load('assets/stairs.jpg').convert_alpha(), (800,600))
		except pygame.error, message:
			print "Cannot load background image!"
			raise SystemExit, message
		self.description = MenuItem(self.screen, "You have reached the stairs", (self.x+175, self.y-250), 50, self.background, (255,0,0))
		self.options = ("Descend", "Keep Exploring")
		self.color = (255,255,255)

	def treasure(self):
		# Load the image
		try:
			self.background = pygame.transform.scale(pygame.image.load('assets/treasureChest.jpg').convert_alpha(), (800,600))
		except pygame.error, message:
			print "Cannot load background image!"
			raise SystemExit, message
		self.description = MenuItem(self.screen, "Argh you found hidden treasure", (self.x+175, self.y-250), 50, self.background, (255,0,0))
		self.options = ("Touch", "Take", "Avoid")

	def fight(self):
		# Load the image
		try:
			self.background = pygame.transform.scale(pygame.image.load('assets/fight.jpg').convert_alpha(), (800,600))
		except pygame.error, message:
			print "Cannot load background image!"
			raise SystemExit, message
		self.description = MenuItem(self.screen, "Your party is being attacked!", (self.x+175, self.y-250), 50, self.background, (255,0,0))
		self.options = ("Fight", "Run Away")
		self.color = (255,255,255)

	def character(self):
		# Load the image
		try:
			self.background = pygame.transform.scale(pygame.image.load('assets/character.jpg').convert_alpha(), (800,600))
		except pygame.error, message:
			print "Cannot load background image!"
			raise SystemExit, message
		self.description = MenuItem(self.screen, "You have found a living being", (self.x+175, self.y-250), 70, self.background, (255,0,0))
		self.options = ("Engage in conversation", "Run Away")
		self.color = (255,255,255)

	def trickster(self):
		# Load the image
		try:
			self.background = pygame.transform.scale(pygame.image.load('assets/joker.jpg').convert_alpha(), (800,600))
		except pygame.error, message:
			print "Cannot load background image!"
			raise SystemExit, message
		self.description = MenuItem(self.screen, "You see a viscious trickster", (self.x+175, self.y-250), 80, self.background, (255,0,0))
		self.options = ("Roll the die", "Run Away")
		self.color = (0,100,100)

	def gold(self):
		# Load the image
		try:
			self.background = pygame.image.load('assets/gold.jpg').convert_alpha()
		except pygame.error, message:
			print "Cannot load background image!"
			raise SystemExit, message
		self.description = MenuItem(self.screen, "Gold?", (self.x+175, self.y-250), 90, self.background, (255,0,0))
		self.options = ("Take", "Touch", "Leave it alone")

	def mice(self):
		# Load the image
		try:
			self.background = pygame.transform.scale(pygame.image.load('assets/mice.jpg').convert_alpha(), (800,600))
		except pygame.error, message:
			print "Cannot load background image!"
			raise SystemExit, message
		self.description = MenuItem(self.screen, "EW mice", (self.x+175, self.y-250), 90, self.background, (255,0,0))
		self.options = ("Touch", "Take", "Kill", "Let's not get the plague")
	
	def bats(self):
		# Load the image
		try:
			self.background = pygame.transform.scale(pygame.image.load('assets/bat-cave.jpg').convert_alpha(), (800,600))
		except pygame.error, message:
			print "Cannot load background image!"
			raise SystemExit, message
		self.color = (255,255,255)
		self.description = MenuItem(self.screen, "You've awoken the bats!", (self.x+175, self.y-250), 90, self.background, (255,0,0))
		self.options = ("Run Away", "Stay and get attacked")

	def light(self):
		self.description = 	MenuItem(self.screen, "The lights have gone out and you can't see!", (self.x+175, self.y-250), 50, self.background, (255,0,0))
		self.options = ("Charge Ahead", "Run Away")

	def rock(self):
		self.description = 	MenuItem(self.screen, "There is a boulder blocking your path", (self.x+175, self.y-250), 50, self.background, (255,0,0))
		self.options = ("Crush", "Move", "Run Away")

	def leak(self):
		self.description = 	MenuItem(self.screen, "There seems to be a leak in the ceiling", (self.x+175, self.y-250), 50, self.background, (255,0,0))
		self.options = ("Patch", "I don't care", "Run Away")

	def object(self):
		self.description = 	MenuItem(self.screen, "You can't quite make it out, but there is an object ahead", (self.x+175, self.y-250), 40, self.background, (255,0,0))
		self.options = ("Touch", "Take", "Run Away")

	def horse(self):
		self.description = 	MenuItem(self.screen, "Wow it's a horse in the dungeon!", (self.x+175, self.y-250), 50, self.background, (255,0,0))
		self.options = ("Adopt", "Pet", "I don't care", "Run Away")

	def armour(self):
		self.description = 	MenuItem(self.screen, "You have come upon some rusty old armour", (self.x+175, self.y-250), 50, self.background, (255,0,0))
		self.options = ("Take", "Examine", "I don't care", "Run Away")

	def clay(self):
		self.description = 	MenuItem(self.screen, "The walls have worn away to expose some clay soil", (self.x+175, self.y-250), 40, self.background, (255,0,0))
		self.options = ("Mold", "Take for Later", "Run Away")

if __name__ == "__main__":
	# Check if sound and font are supported
	if not pygame.font:
		print "Warning, fonts disabled"
	if not pygame.mixer:
		print "Warning, sound disabled"
		
	# Constants
	FPS = 50
	SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
	BACKGROUND_COLOR = (0, 100, 100)
	
	# Initialize Pygame, the clock (for FPS), and a simple counter
	pygame.init()
	pygame.display.set_caption('Event Demo')
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
	clock = pygame.time.Clock()
	
	room = Room.Room(0,0,4,4)
	#fight = Fight.Fight(room)

	#choose which event you want to happen
	myEvent = EventMenu("clay", screen)


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
				
		myEvent.handleEvent(event)

		# Redraw the background
		screen.blit(myEvent.background, (0,0))
		
		# Update and redraw event
		myEvent.draw()
		myEvent.description.draw(myEvent.background, myEvent.screen)
		#print myEvent.description.text

		# Draw the sprites
		pygame.display.flip()
