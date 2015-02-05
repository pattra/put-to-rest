import pygame, os, sys
from pygame.locals import *
import Room

class Tile(pygame.sprite.Sprite):
	'comment'
	#Constants
	grid_size = 25
	#type_color = {'plain' : 0x444444, 'pit' : 0x111111, 'rubble' : 0x888888, 'stuff':0x444444 } #stuff 0x664411
	type_color = {'plain' : 0x252525, 'pit' : 0x000000, 'rubble' : 0x585858, 'stuff':0x141414 } #stuff 0x664411
	type_walkable = {'plain' : True, 'pit' : False, 'rubble' : False, 'stuff':False }
	type_vision_past = {'plain' : True, 'pit' : True, 'rubble' : False, 'stuff':False }

	def load_image(self, image_name):
		''' Image loading taken from examples '''
		try:
			image = pygame.image.load(image_name)
		except pygame.error, message:
			print "Cannot load image: " + image_name
			raise SystemExit, message
		return image.convert_alpha()

	def __init__(self, offset_x, offset_y, grid_x,grid_y):
		'comment'
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer

		#load image
		#self.image = self.load_image('assets/battlecruiser.gif')
		#self.image_w, self.image_h = self.image.get_size()

		# Create rect 
		width = Tile.grid_size
		height = Tile.grid_size
		x, y = offset_x + grid_x * Tile.grid_size, offset_y + grid_y * Tile.grid_size
		self.rect = pygame.Rect(x,y,width,height)

		# Info
		self.grid_x = grid_x
		self.grid_y = grid_y
		self.type = 'plain'
		self.object = None
		self.unit = None
		self.vision_past = True

		# Graphics
		self.crate_image = self.load_image('assets/Crates1.png')

		# Interface
		self.highlighted = False
		self.movement_range = []
		self.vision_range = []
		self.attack_range = []

	# Is the tile pathable with respect to the given unit	
	def is_pathable(self,unit):
		if self.type == 'pit' or self.type == 'rubble' : #REPLACE PIT/RUBBLE WITH OBJECTS
			return False
		if self.object:
			return self.object.pathable
		return True

	def set_type(self, tile_type):
		self.type = tile_type
		self.walkable = Tile.type_walkable[self.type]
		self.vision_past = Tile.type_vision_past[self.type]

	def set_unit(self, unit):
		self.unit = unit
		self.unit.rect.x, self.unit.rect.y = self.rect.x, self.rect.y

	def mouse_event(self, event):
		if self.rect.collidepoint(event.pos):
			self.highlighted = True
		else:
			self.highlighted = False

	def draw(self, surface):
		# Backgroud
		color = Tile.type_color[self.type]
		pygame.draw.rect(surface, color, self.rect)
		if self.type == 'stuff':
			surface.blit(self.crate_image, (self.rect.x+1, self.rect.y+3))
		if self.highlighted:
			color = 0x777700
			pygame.draw.rect(surface, color, self.rect, 3)

		# Movement Range - current unit if its a player
		for unit in self.movement_range:
			if unit.turn and unit.team.player:
				color =  0x0000bb # dont delete: beutiful beige0xccbbaa
				s = pygame.Surface(self.rect.size)
				s.set_alpha(80)
				s.fill(color)
				surface.blit(s,self.rect.topleft)
				break
		# Vision Range - all player unit's vision
		if not self.type == 'pit':
			for unit in self.vision_range:
				if unit.team.player:
					color = 0xaaaa99
					s = pygame.Surface(self.rect.size)
					s.set_alpha(50)
					s.fill(color)
					surface.blit(s,self.rect.topleft)
					break
		# Attack Range - current unit if its a player
		for unit in self.attack_range:
			if unit.turn and unit.team.player:
				if unit.heal > 0: # Indicate heal
					color =  0x00bb00
					if unit.damage > 0: #Indicate heal and attack
						color =  0xbbbb00
				else:
					color =  0xbb0000
				s = pygame.Surface(self.rect.size)
				s.set_alpha(80)
				s.fill(color)
				surface.blit(s,self.rect.topleft)
				break

	def draw_popups(self, surface):
		if self.unit:
			#pygame.draw.rect(surface, 0xbbbbbb, self.rect)
			self.unit.draw(surface)
