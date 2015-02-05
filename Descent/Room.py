import pygame, os, sys, json
from pygame.locals import *
import random
import Door, Team, character, Grid

class Room(pygame.sprite.Sprite):
	'room in dungeon'
	# Constants
	grid_size = 25

	def load_image(self, image_name):
		''' Image loading taken from examples '''
		try:
			image = pygame.image.load(image_name)
		except pygame.error, message:
			print "Cannot load image: " + image_name
			raise SystemExit, message
		return image.convert_alpha()

	def __init__(self, init_x, init_y, width, height):
		'comment'
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer

		#load image
		#self.image = self.load_image('assets/battlecruiser.gif')s
		#self.image_w = 112
		#self.image_h = 130

		# Shape (Modularize inputs to grid_size)
		x = Room.grid_size * init_x
		y = Room.grid_size * init_y 
		width = Room.grid_size	* width
		height = Room.grid_size * height	
		self.rect = pygame.Rect(x,y,width,height)

		# Mouse Events
		self.highlighted = False
		self.neighbor_highlighted = False

		# Connections
		self.neighboring_rooms = []
		self.connected_rooms = []
		self.doors = []

		# Mechanics
		self.visited = False
		self.visible = False
		self.occupied = False
		self.stairwell = False
		self.stairwell_image = None
		self.active = True

		# Character - NOTE: Rooms should probably NOT have a reference to the JSON.... this is a hack
		self.reference = None

		# Event (TODO: make into a class)
		# 0:none,1:fight,2:decision,3:treasure
		# Ideas: Danger Sense (Priest), Treasue Sense (Dwarf, Arcanist), Body Sense, Blood Sense(Warlock, Blood Priest)
		self.event_num = random.randint(0,3)
		self.event = {0:'none', 1:'fight',2:'decision',3:'treasure'}[self.event_num] # Python is so cool
		# Generate units for fight
		# if self.event == 'fight':
		# 	# Generate Baddies
		# 	team_baddy = Team.Team("baddies")
		# 	npc_count = 5
		# 	npc_rect = pygame.Rect(0,0,4,4)
		# 	while npc_count > 0:
		# 		# x = random.randint(npc_rect.x,npc_rect.x+npc_rect.width)
		# 		# y = random.randint(npc_rect.y,npc_rect.y+npc_rect.height)
		# 		# if not self.grid.tiles[x][y].unit and self.grid.tiles[x][y].is_pathable(None):
		# 			unit = Character.Character(0,0,None, 'baddy1')
		# 			#self.units.append(unit)
		# 			team_baddy.units.append(unit)
		# 			npc_count -= 1

	def set_neighbor(self, room):
		if room not in self.neighboring_rooms:
			self.neighboring_rooms.append(room)
		if self not in room.neighboring_rooms:
			room.neighboring_rooms.append(self)

	def set_connected(self, room):
		if room not in self.connected_rooms:
			self.connected_rooms.append(room)
		if self not in room.connected_rooms:
			room.connected_rooms.append(self)	

	def set_connected_door(self, room, door):
		if room not in self.connected_rooms:
			self.connected_rooms.append(room)
		if self not in room.connected_rooms:
			room.connected_rooms.append(self)	
		if door not in room.doors:
			room.doors.append(door)
		if door not in self.doors:
			self.doors.append(door)

	def occupy(self):
		self.occupied = True
		self.visited = True
		for room in self.connected_rooms:
			room.visible = True

	def is_connected(self, room):
		return self in room.connected_rooms

	def mouse_event(self, event):
		if self.rect.collidepoint(event.pos):
			self.highlighted = True
		else:
			self.highlighted = False

	def update(self):
		# highlight if connected neighbor is highlighted
		self.neighbor_highlighted = False
		for room in self.neighboring_rooms:
			if room.highlighted:
				self.neighbor_highlighted = True
				break

	def wipe(self):
		for room in self.neighboring_rooms:
			room.neighboring_rooms.remove(self)
			self.neighboring_rooms.remove(room)

	def set_stairwell(self):
		self.stairwell = True
		self.stairwell_image = self.load_image("assets/objects/Stairwell.png")

	def generate_doors(self):
		door_loc = {'direction':'none','x':0,'y':0}
		for room in self.neighboring_rooms:
			if not self.is_connected(room):
				if room.rect.x >= self.rect.x + self.rect.width: #right
					door_loc = Door.Door('vertical', room.rect.x/Room.grid_size, \
						random.randint(max(room.rect.y, self.rect.y)/Room.grid_size, \
						min(room.rect.y+room.rect.height, self.rect.y+self.rect.height)/Room.grid_size-1))
					door_loc.rooms= [self, room]
					self.set_connected_door(room,door_loc)
				elif room.rect.y >= self.rect.y + self.rect.height: #top
					door_loc = Door.Door('horizontal', random.randint(max(room.rect.x, self.rect.x)/Room.grid_size, \
						min(room.rect.x+room.rect.width, self.rect.x+self.rect.width)/Room.grid_size-1), \
						(self.rect.y + self.rect.height)/Room.grid_size)
					door_loc.rooms= [self, room]
					self.set_connected_door(room,door_loc)	

	# Draw Room and Doors
	def draw(self, target_surface):
		if self.visible:
			#fill_color = 0x153770
			fill_color = 0x123466
			line_color = 0x111111

			if self.highlighted:
				line_color = 0x995500
			elif self.neighbor_highlighted:
				line_color = 0x663300
			if self.visited:
				fill_color = 0x285083
				for room in self.connected_rooms:
					if room.occupied:
						fill_color = 0x396194
						break
			if self.occupied:
				fill_color = 0x5577aa
			
			# fill
			pygame.draw.rect(target_surface, fill_color, self.rect)
			# border
			pygame.draw.rect(target_surface, line_color, self.rect, 2)
			for door in self.doors:
				door.draw(target_surface)
			for room in self.neighboring_rooms:
				if room.visible:
					for door in room.doors:
						door.draw(target_surface)

			if self.stairwell:
				target_surface.blit(self.stairwell_image, (self.rect.x, self.rect.y))
			# Event Type (TODO: Make Event its own class)
			# 0:none,1:fight,2:decision,3:treasure
			#event_color = {0:0x888888, 1:0xbb4444,2:0xbb6644,3:0xccbb00}[self.event_num]
			#pygame.draw.rect(target_surface, event_color, self.rect.inflate(-20, -20))

			# Draw characters
			if self.occupied and not self.reference:
				with open('json/Player.json') as data_file:    
					self.reference = json.load(data_file)['characters']
				data_file.close()
			if self.reference and self.occupied:
				x_offset = self.rect.x +2
				y_offset = self.rect.y +2
				for name in self.reference:
					if y_offset + 10 < self.rect.y + self.rect.height -2:
						target_surface.blit(pygame.transform.scale(\
							self.load_image(self.reference[name]['image']), (16,32)), (x_offset,y_offset),(0,0,10,10))
						x_offset += 10
						if x_offset + 10 > self.rect.x + self.rect.width -2:
							x_offset = self.rect.x+2
							y_offset += 10


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
	pygame.display.set_caption('Battlecruiser Demo')
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
	clock = pygame.time.Clock()

	#Rooms
	rooms = pygame.sprite.Group()
	rooms.add(Room(2,2,2,3))
	rooms.add(Room(4,8,2,3))

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
			elif event.type == pygame.MOUSEMOTION:
				for room in rooms:
					room.mouse_event(event)

		# Redraw the background
		screen.fill(BACKGROUND_COLOR)
		
		# Update and redraw all sprites
		for room in rooms:
			room.draw(screen)
		

		# Draw the sprites
		pygame.display.update()

		
