import pygame, os, sys, json, random
from pygame.locals import *
import Room, Tile, Fight, astar

class Object(pygame.sprite.Sprite):
	'comment'
	#Constants
	grid_size = 25

	def load_image(self, image_name):
		''' Image loading taken from examples '''
		try:
			image = pygame.image.load(image_name)
		except pygame.error, message:
			print "Cannot load image: " + image_name
			raise SystemExit, message
		return image.convert_alpha()

	def __init__(self, x,y, grid, object_id):
		'comment'
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		with open('json/Objects.json') as data_file: 
			json_data =	json.load(data_file)
			dungeon = json_data[object_id]
			manual = json_data[random.choice(dungeon)]
		data_file.close()
		# Load Image
		self.image = \
			self.load_image(manual['image'][random.randint(0,len(manual['image'])-1)])
		self.image_w, self.image_h = self.image.get_size()
		scale = 1.0
		self.image = pygame.transform.scale((self.image), ( int(round(self.image_w*scale)), int(round(self.image_h*scale))))
		self.image_w, self.image_h = self.image.get_size()
		# Generate Dark Image
		self.dark_image = self.image.copy()
		arr = pygame.surfarray.pixels3d(self.dark_image)
		arr[:,:,0],arr[:,:,1],arr[:,:,2] = 20,20,20
		# Image offset
		self.x_off = manual['x_off']
		self.y_off = manual['y_off']

		# Create Rectangle
		self.grid_width, self.grid_height =  manual['width'], manual['height']
		self.width =  manual['width'] * Object.grid_size
		self.height = manual['height'] * Object.grid_size
		self.rect = pygame.Rect(0,0,self.width,self.height)

		# Stats
		self.destructable = manual['destructable']
		self.pathable = manual['pathable']

		# Placement
		self.grid = grid
		self.current_tiles = []
		#self.set_tile(grid.tiles[x][y])

		# Interface
		# self.highlighted_tile = None
		# self.selected = False

	def set_tile(self, tile):
		self.rect.topleft = tile.rect.topleft
		x,y  = tile.grid_x, tile.grid_y
		self.wipe_tiles()
		self.current_tiles = []
		for i in range(x,min(self.grid.cols, x+self.grid_width)):
			for j in range(y,min(self.grid.rows,y+self.grid_height)):
				self.grid.tiles[i][j].object = self
				self.current_tiles.append(self.grid.tiles[i][j])

	def wipe_tiles(self):
		if self.current_tiles:
			for tile in self.current_tiles:
				tile.object = None

	def can_place(self, tile):
		x,y  = tile.grid_x, tile.grid_y
		if x+ self.grid_width > self.grid.cols or y+ self.grid_height > self.grid.rows:
			return False
		for i in range(x,x+self.grid_width):
			for j in range(y,y+self.grid_height):
				if not self.grid.tiles[i][j].is_pathable(None) and not self.grid.tiles[i][j].unit:
					return False
		return True
	# def mouse_event(self, event):
	# 	if self.selected:
	# 		if event.type == pygame.MOUSEBUTTONDOWN:	
	# 			if self.action == 'idle':
	# 				if self.highlighted_tile in self.movement_range:
	# 					self.move(self.path_to_tile)
	
	def draw(self, surface):
		# if self.selected:
		# 	# Draw Path from current_tile to highlighted_tile
		# 	if self.path_to_tile:
		# 		color = 0x9999bb
		# 		#pygame.draw.line(surface,color, self.current_tile.rect.center, self.path_to_tile[0].rect.center, 4)
		# 		pygame.draw.line(surface,color, self.rect.center, self.path_to_tile[0].rect.center, 4)
		# 		for i in range(len(self.path_to_tile)-1):
		# 			pygame.draw.line(surface,color, self.path_to_tile[i].rect.center, self.path_to_tile[i+1].rect.center, 4)	

		# Darken Unseen Tiles
		visible = 0
		# All tiles occupied by object must be visible to player characters
		for tile in self.current_tiles:
			for unit in tile.vision_range:
				if unit.team.player:
					visible += 1
					break
		if visible == len(self.current_tiles):
			surface.blit(self.image, (self.rect.x+ self.x_off, self.rect.y+ self.y_off))
		else:
			surface.blit(self.dark_image, (self.rect.x+ self.x_off, self.rect.y+ self.y_off))



	# def update(self):





	

