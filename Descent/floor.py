import pygame, os, sys, math, json
from pygame.locals import *
import Room, Fight, Event2
import random

#TODO: Organize fight / room inside game loop
#NOTE: I can make all highlight detection more efficent by only checking rooms / tiles underneath the cursor
def get_distance(p1, p2):
	return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

class Floor(pygame.sprite.Sprite):
	'floor of dungeon'
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

	def __init__(self, width, height, party):
		'comment'
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer

		# Modularize inputs and build rect
		width = Floor.grid_size	* width
		height = Floor.grid_size * height	
		self.rect = pygame.Rect(0,0,width,height)

		self.show_grid = False

		self.rooms = []
		self.rooms_graph = {}
		self.occupied_room = None
		self.path_to_room = []

		self.fight = None
		self.event = None
		self.game_over = False
		self.win = False

		# party
		self.party = party

		# Determines the difficulty of fights on the floor
		self.level = 1
		self.maxlevel = 5

	def draw(self, surface):
		if self.fight:
			self.fight.draw(surface)
		elif self.event:
			self.event.draw(surface)
		else:
			# Backgroud
			color = 0x222222
			pygame.draw.rect(surface, color, self.rect)

			# Grid
			if self.show_grid:
				color = 0x009999
				for i in xrange(0,self.rect.width, Floor.grid_size):
					pygame.draw.line(surface, color, (i,self.rect.x), (i,self.rect.x+self.rect.width), 1)
				for j in xrange(0,self.rect.height, Floor.grid_size):
					pygame.draw.line(surface, color, (self.rect.y,j), (self.rect.y+self.rect.height,j), 1)
			# Rooms
			for room in self.rooms:
				room.draw(surface)

			# Path to Room
			color = 0xbbbbbb
			# Draw Path from center of room 1 to door to center of room 2
			if self.path_to_room:
				#color = {0:0x888888, 1:0xbb4444,2:0xbb6644,3:0xccbb00}[self.path_to_room[len(self.path_to_room)-1].event_num]
				for i in range(len(self.path_to_room)-1):
					for door in self.path_to_room[i].doors:
						if self.path_to_room[i+1] in door.rooms:
							pygame.draw.line(surface,color, self.path_to_room[i].rect.center, door.rect.center, 4)
							pygame.draw.line(surface,color, door.rect.center, self.path_to_room[i+1].rect.center, 4)
							break
		
		# if self.path_to_room:
		# 	cur_door = None
		# 	next_door = None
		# 	room_center = None
		# 	for door in self.path_to_room[0].doors:
		# 		if self.path_to_room[1] in door.rooms:
		# 			cur_door = door
		# 			break
		# 	pygame.draw.line(surface,color, self.path_to_room[0].rect.center, cur_door.rect.center, 4)
		# 	for i in range(1,len(self.path_to_room)-1):
		# 		room_center = self.path_to_room[i].rect.center
		# 		for door in self.path_to_room[i].doors:
		# 			if self.path_to_room[i+1] in door.rooms:
		# 				next_door = door
		# 				break
		# 		if get_distance(cur_door.rect.center,room_center) < get_distance(cur_door.rect.center,next_door.rect.center):
		# 			pygame.draw.line(surface,color, cur_door.rect.center, room_center, 4)
		# 			pygame.draw.line(surface,color, room_center, next_door.rect.center, 4)
		# 		else:
		# 			pygame.draw.line(surface,color, cur_door.rect.center, next_door.rect.center, 4)	
		# 		cur_door = next_door					

	def update(self):
		if self.level > self.maxlevel:
			self.win = True
		elif self.fight:
			self.fight.update()
			if self.fight.over_lose:
				self.game_over = True
			if self.fight.over:
				self.fight = None
				self.save_to_file()

		elif self.event:
			# EVENTSTUFF
			# PUT THE UPDATE FOR EVENT HERE
			# Self.event.update...
			# then remove pass
			pass
		else:
			for room in self.rooms:
				room.update()
			

	def mouse_event(self, event):
		if self.fight:
			self.fight.mouse_event(event)
		# EVENTSTUFF
		# PUT THE EVENT Mouse Handing HERE
		# elif self.event:
		# self.event.mouse_event(event)
		else:
			if event.type == pygame.MOUSEMOTION:
				highlighted_room = None
				for room in self.rooms:
					room.mouse_event(event)
					if room.highlighted and room.visible:
						highlighted_room = room
				#Create path from room to other rooms
				# TODO: ONLY DO IT IF ITS HIGHLIGHTING A NEW ROOM!!!!!!!
				if highlighted_room:
					if not self.path_to_room or self.path_to_room[len(self.path_to_room)-1] != highlighted_room:
						self.path_to_room = self.find_path( self.occupied_room, highlighted_room, True, [])
				else: 
					self.path_to_room = []
			elif event.type == pygame.MOUSEBUTTONDOWN:
				highlighted_room = None
				for room in self.rooms:
					if room.highlighted and room.visible:
						highlighted_room = room
						break
				if highlighted_room:
					self.occupy_room(highlighted_room)


	def key_event(self, event):
		if event.key == K_SPACE:
					if self.event:
						self.event = None
					else:
						if self.occupied_room:
							# EVENTSTUFF
							# PUT THE EVENT HERE
							# self.event = ...
							# Then remove pass below
							pass

		elif self.fight:
			self.fight.key_event(event)
		# if event.key == K_SPACE:
		# 			if self.fight:
		# 				self.fight = None
		# 			else:
		# 				if self.occupied_room:
		# 					self.enter_fight(self.occupied_room)
		# elif self.fight:
		# 	self.fight.key_event(event)


	def place_room(self, x, y, width, height):
		new_room = Room.Room(x,y,width,height)
		bad_placement = False
		if self.rect.contains(new_room.rect):
			for room in self.rooms:
				if room.rect.colliderect(new_room):
					bad_placement = True
					break
			if not bad_placement:
				self.rooms.append(new_room)
				self.connectRoomToNeighbors(new_room)
		else:
			return (True, 0)
		return (not bad_placement, new_room)

	def connectRoomToNeighbors(self, the_room):
		for room in self.rooms:
			if room != the_room:
				if room.rect.inflate(2,0).colliderect(the_room) or room.rect.inflate(0,2).colliderect(the_room):
					room.set_neighbor(the_room)

	def occupy_room(self, room, first_room = False):
		if self.occupied_room:
			self.occupied_room.occupied = False
		self.occupied_room = room
		already_visited = self.occupied_room.visited
		self.occupied_room.occupy()
		self.occupied_room.visible = True
		# Clear path
		self.path_to_room = []

		# Chance of fight:
		if not already_visited and not first_room:
			#if random.randint(0,100) < 34:
			#	self.enter_event()
			if random.randint(0,100) < 34:
				self.enter_fight(self.occupied_room)
			else:
				self.save_to_file()
			#self.enter_event()

		# Stairwell
		if self.occupied_room.stairwell:
			self.level += 1 
			if self.level > 5:
				self.win = True
			else:
				self.generate_rooms()


	def generate_rooms(self, floor_data = None):
		# Clear old rooms
		if self.rooms:
			for room in self.rooms:
				room.wipe()
				room.kill()
				self.rooms.remove(room)
			self.rooms = []

		# Generate rooms by algorithm if not file exists
		if not floor_data:
			max_neighbors = 3
			room_count = 30
			fail_safe = room_count * 20 #for preventing infinite loop
			cur_room = Room.Room(15,15,2,2)
			self.rooms.append(cur_room)
			while len(self.rooms) < room_count and fail_safe > 0:
				fail_safe -= 1
				cur_room = random.choice(self.rooms)
				if len(cur_room.neighboring_rooms) < max_neighbors:
					side = random.randint(0,1)
					width = random.randint(1,4)
					height = random.randint(1,4)
					x, y = (0,0)
					if side == 0: #left
						y = cur_room.rect.y/Floor.grid_size + random.randint(-height+1,cur_room.rect.height/Floor.grid_size-1)
						x = cur_room.rect.x/Floor.grid_size - width
					if side == 1: #top
						x = cur_room.rect.x/Floor.grid_size + random.randint(-width+1,cur_room.rect.width/Floor.grid_size-1)
						y = cur_room.rect.y/Floor.grid_size - height
					placed, placed_room = self.place_room(x,y,width,height)
					if not placed:
						if len(placed_room.neighboring_rooms) > max_neighbors:
							placed_room.wipe()
							placed_room.kill()
			for room in self.rooms:
				room.generate_doors()

			# Place stairwell
			for i in range(0,100):
				cur_room = random.choice(self.rooms)
				# If far enough away
				path = self.find_path(cur_room,self.rooms[0], False, [])
				if path:
					if len(path)>5:
						cur_room.set_stairwell()
						break

			# Place team in initial room
			self.occupy_room(self.rooms[0], True)

		else:
			rooms_data = floor_data['rooms']
			for room_key in rooms_data:
				room_data = rooms_data[room_key]
				not_placed, placed_room = \
				self.place_room(room_data['x'],room_data['y'],room_data['width'],room_data['height'])
				if not_placed:
					placed_room.visited = room_data['visited']
					placed_room.visible = room_data['visible']
					placed_room.occupied = room_data['occupied']
					if room_data['stairwell']:
						placed_room.set_stairwell()
			for room in self.rooms:
				room.generate_doors()
			for room in self.rooms:
				if room.occupied:
					self.occupy_room(room, True)
					break


	def find_path(self, start, end, visible_only, path=[]):
		path = path + [start]
		if start == end:
			return path
		if start not in self.rooms: # if not graph.has_key(start):
			return None
		shortest = None
		for node in start.connected_rooms:
			if not visible_only or (node.visible and node.visited) or node == end:
				if node not in path:
					newpath = self.find_path(node, end, visible_only, path)
					if newpath:
						if not shortest or len(newpath) < len(shortest):
							shortest = newpath
		return shortest

	def enter_fight(self, room):
		self.fight = Fight.Fight(room, self.party, self.level)

	#def enter_event(self):
	#	self.event = Event2.Event(None)

	def save_to_file(self):
		data = {"rooms":{}}

		room_key = 0
		for room in self.rooms:
			data['rooms']['room' + str(room_key)] = {"x":room.rect.x/Floor.grid_size,\
			"y": room.rect.y/Floor.grid_size, "width": room.rect.width/Floor.grid_size,\
			"height": room.rect.height/Floor.grid_size, "visited":room.visited,\
			"visible": room.visible, "occupied":room.occupied, "stairwell":room.stairwell}
			room_key += 1
		jsonFile = open("json/Floor.json", "w+")
		jsonFile.write(json.dumps(data))
		jsonFile.close()


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

	#Rooms
	floor = Floor(20,20)
	floor.generate_rooms()

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
					floor.key_event(event)
			elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
				floor.mouse_event(event)


		# Redraw the background
		screen.fill(BACKGROUND_COLOR)
		
		# Update and redraw all spritess
		floor.update()
		floor.draw(screen)

		# Draw the sprites
		pygame.display.update()

		
