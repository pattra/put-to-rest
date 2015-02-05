import pygame, os, sys, json
from pygame.locals import *
import Room, Tile, character, Grid, Object, Team, FightInterface
import random, astar, time, threading


class Fight(pygame.sprite.Sprite):
	'comment'
	#Constants
	grid_size = 25
	#TODO: MOVE THIS TO A JSON U LAZY BASTARD
	baddies_by_level = [['ghost_melee_1','ghost_ranged_1'],['ghost_melee_2','ghost_ranged_2'],\
	['ghost_melee_3','ghost_ranged_3'],['ghost_melee_4','ghost_ranged_4'],['ghost_melee_5','ghost_ranged_5']]

	def load_image(self, image_name):
		''' Image loading taken from examples '''
		try:
			image = pygame.image.load(image_name)
		except pygame.error, message:
			print "Cannot load image: " + image_name
			raise SystemExit, message
		return image.convert_alpha()

	def __init__(self, room, party, level=1):
		'comment'
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer

		# Create rect 
		x, y = 50, 50
		width = room.rect.width / Fight.grid_size * 5
		height = room.rect.height / Fight.grid_size * 5

		# Range Normalizing of fight size
		old_min, old_max = 5, 20
		new_min, new_max = 10,20
		old_range = (old_max-old_min)
		new_range = (new_max-new_min)
		width = (((width - old_min) * new_range) / old_range) + new_min
		height = (((height - old_min) * new_range) / old_range) + new_min
		self.rect = pygame.Rect(x,y,Fight.grid_size * width,Fight.grid_size * height)

		# Tiles
		self.grid = Grid.Grid(self.rect)
		self.tiles = self.grid.tiles
		self.highlighted_tile = None

		# Level - determines characters and difficulty
		self.level = level

		# Party members
		self.party = party

		# Complete - indicates to floor to exit fight
		self.over = False
		self.over_lose = False

		# Generate Tiles
		for i in range(0,self.grid.cols):
			for j in range(0,self.grid.rows):
				self.tiles[i][j] = Tile.Tile(self.rect.x, self.rect.y, i ,j )


		# Give Tiles Types - and ensure pathing
		to_expand = None
		for i in range(0,self.grid.cols):
			for j in range(0,self.grid.rows):
				if random.random() < .1: 
					self.tiles[i][j].set_type('pit')
					if random.random() <.5:
						to_expand = self.tiles[min(len(self.tiles)-1, max(0,i+random.randint(-1,1)))] \
							[min(len(self.tiles[0])-1, max(0,j+random.randint(-1,1)))]
						to_expand.set_type('pit')
				if random.random() < .05: 
					self.tiles[i][j].set_type('rubble')
				if not astar.astar(self.grid, self.tiles[0][0], \
					self.tiles[self.grid.cols-1][self.grid.rows-1]):
					self.tiles[i][j].set_type('plain')
					if to_expand:
						to_expand.set_type('plain')

		# # Expand Pits
		# for i in range(0,self.grid.cols):
		# 	for j in range(0,self.grid.rows):
		# 		if self.tiles[i][j].type == 'pit':
		# 			if random.random() <.5:
		# 				self.tiles[min(len(self.tiles)-1, max(0,i+random.randint(-1,1)))] \
		# 					[min(len(self.tiles[0])-1, max(0,j+random.randint(-1,1)))].set_type('pit')
		# Place Objects
		self.objects = []
		obj_count = int(round((self.grid.cols*self.grid.rows)/15))
		attempts = 0
		max_attempts = obj_count * 2.5
		while obj_count > 0 and attempts < max_attempts:
			attempts += 1
			x = random.randint(0,self.grid.cols-1)
			y = random.randint(0,self.grid.rows-1)
			to_place = Object.Object(x,y,self.grid, 'dungeon')
			tile = self.grid.tiles[x][y]
			if not tile.unit and to_place.can_place(tile):
				to_place.set_tile(tile)
				self.objects.append(to_place)
				obj_count -= 1
				# Ensure path
				if not astar.astar(self.grid, self.tiles[0][0], \
					self.tiles[self.grid.cols-1][self.grid.rows-1]):
					to_place.wipe_tiles()
					self.objects.remove(to_place)
					obj_count += 1

		'''Place Units'''
		self.units = []
		self.dead_units = []
		# Player Characters 
		player_team = Team.Team('player', True)
		player_rect = pygame.Rect(len(self.tiles) -4,len(self.tiles[0]) -4,3,3)
	#	with open('json/Player.json') as data_file:    
	#		player_char_list = json.load(data_file)['characters']
	#	data_file.close()
		player_char_list = self.party['characters']
		for char in player_char_list:
			#TODO: Make sure they get placed in a pathable region
			while True:
				x = random.randint(player_rect.x,player_rect.x+player_rect.width)
				y = random.randint(player_rect.y,player_rect.y+player_rect.height)
				if not self.grid.tiles[x][y].unit and self.grid.tiles[x][y].is_pathable(None):
					unit = character.Character(char,player_team,self.party,'Player.json')
					unit.init_to_grid(self.grid,x,y)
					self.units.append(unit)
					break

		# NPC Characters
		team_baddy = Team.Team("baddies")
		npc_count = random.randint(1,7)
		npc_rect = pygame.Rect(0,0,7,7)
		while npc_count > 0:
			x = random.randint(npc_rect.x,npc_rect.x+npc_rect.width)
			y = random.randint(npc_rect.y,npc_rect.y+npc_rect.height)
			if not self.grid.tiles[x][y].unit and self.grid.tiles[x][y].is_pathable(None):
				unit = character.CharacterAI(Fight.baddies_by_level[self.level-1][random.randint(0,1)],team_baddy)
				unit.init_to_grid(self.grid,x,y)
				unit.fight_units = self.units
				self.units.append(unit)
				npc_count -= 1

		# Roll For Initiative !!
		initiative = {}
		for unit in self.units:
			initiative[unit] = unit.initiative + random.randint(0,20)
		self.units.sort(key = lambda x : initiative[x])
		# Set selected unit as first
		self.current_unit_index = 0
		self.current_unit = None
		self.set_selected_unit(self.units[self.current_unit_index])

		# Interface 
		self.interface = FightInterface.FightInterface(self)

	def draw(self, surface):
		# Backgroud
		color = 0x222222
		pygame.draw.rect(surface, color, self.rect)

		# Draw Tiles
		for i in range(0,self.grid.cols):
			for j in range(0,self.grid.rows):
				self.tiles[i][j].draw(surface)

		# Grid
		# if self.grid.show_grid:
		# 	color = 0x555555#0x777777
		# 	for i in xrange(self.rect.x,self.rect.x+self.rect.width+1, Fight.grid_size):
		# 		pygame.draw.line(surface, color, (i,self.rect.y), (i,self.rect.y+self.rect.height), 1)
		# 	for j in xrange(self.rect.y,self.rect.y+self.rect.height+1, Fight.grid_size):
		# 		pygame.draw.line(surface, color, (self.rect.x,j), (self.rect.x+self.rect.width,j), 1)

		# Sort by Y for drawing purposes then draw
		objects_and_units = self.objects + self.units
		for unit in sorted(objects_and_units, key=lambda x : x.rect.y):
			unit.draw(surface)

		# Clear tile of range indicators
		# for i in range(0,self.grid.cols):
		# 	for j in range(0,self.grid.rows):
		# 		self.tiles[i][j].vision_range = False
		# 		self.tiles[i][j].movement_range = False
		# 		self.tiles[i][j].attack_range = False

		# Interface
		self.interface.draw(surface)

	def set_selected_unit(self, unit):
		char_tile = unit.current_tile
		if self.current_unit:
			self.current_unit.selected = False
		self.current_unit = unit
		self.set_current_tile(char_tile)
		self.current_unit.set_tile(char_tile)
		self.current_unit.selected = True
		self.current_unit.give_turn()

	def set_current_tile(self, tile):
		self.current_tile = tile
		self.path_to_tile = None

	# Move object or unit from tile to another
	def move(self, from_tile, to_tile):
		if from_tile.unit:
			to_tile.set_unit(from_tile.unit)
			from_tile.unit = None
			if self.current_tile == from_tile:
				self.set_current_tile(to_tile)

	def mouse_event(self, event):
		if event.type == pygame.MOUSEMOTION:
			# Mousing over a tile
			for i in range(0,self.grid.cols):
				for j in range(0,self.grid.rows):
					tile = self.tiles[i][j]
					tile.mouse_event(event)
					if self.tiles[i][j].highlighted:
						self.highlighted_tile = tile
			if self.highlighted_tile: 
				self.current_unit.set_highlighted_tile(self.highlighted_tile)
		for unit in self.units:
			unit.mouse_event(event)

	def key_event(self, event):
		if event.key == K_TAB:
			self.current_unit_index += 1
			self.current_unit_index %= len(self.units)
			self.set_selected_unit(self.units[self.current_unit_index])

	def update(self):
		# Update Units
		player_has_units_left = False
		for unit in self.units:
			unit.update()
			# handle dead
			if unit.health <= 0:
				unit.die()
				unit.kill()
			else:
				if unit.team.player:
					player_has_units_left = True
		for unit in self.units:
			if not unit.alive:
				self.units.remove(unit)
				self.dead_units.append(unit)

		# Determine Character Turn
		if not self.current_unit.alive or not self.current_unit.turn:
			self.current_unit_index += 1
			self.current_unit_index %= len(self.units)
			self.set_selected_unit(self.units[self.current_unit_index])

		# Check if fight is over
		baddies_left = False
		for unit in self.units:
			if not unit.team.player:
				baddies_left = True
		if not baddies_left:
			self.over = True
			# Save units
			for unit in self.units:
				unit.save_to_file()
			for unit in self.dead_units:
				if unit.team.player:
					unit.save_to_file()
		if not player_has_units_left:
			self.over_lose = True

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
	pygame.display.set_caption('Floor Demo')
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
	clock = pygame.time.Clock()
	room = Room.Room(0,0,4,4)
	fight = Fight(room)
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
					fight.key_event(event)
			#elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
			#	floor.mouse_event(event)


		# Redraw the background
		screen.fill(BACKGROUND_COLOR)
		
		# Update and redraw all sprites
		fight.draw(screen)

		# Draw the sprites
		pygame.display.update()

		
