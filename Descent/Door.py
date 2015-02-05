import pygame, os, sys
from pygame.locals import *
import Room

class Door(pygame.sprite.Sprite):
	'comment'
	#Constants
	grid_size = 25
	door_length = grid_size -9
	door_thickness = 3

	def load_image(self, image_name):
		''' Image loading taken from examples '''
		try:
			image = pygame.image.load(image_name)
		except pygame.error, message:
			print "Cannot load image: " + image_name
			raise SystemExit, message
		return image.convert_alpha()

	def __init__(self, direction, init_x, init_y):
		'comment'
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer

		#load image
		#self.image = self.load_image('assets/battlecruiser.gif')
		#self.image_w, self.image_h = self.image.get_size()

		# Create rect and adjust so its centered on grids
		if direction == 'vertical':
			x = Door.grid_size * init_x -1
			y = Door.grid_size * init_y +4
			width = Door.door_thickness 
			height = Door.door_length
		else: #horizontal
			x = Door.grid_size * init_x +4
			y = Door.grid_size * init_y -1
			height = Door.door_thickness
			width = Door.door_length
		self.rect = pygame.Rect(x,y,width,height)

		# Rooms Management
		self.rooms = []

	def draw(self, target_surface):
		door_color = 0x448800
		for room in self.rooms:
			if room.highlighted:
				door_color = 0x66bb22
				break
		pygame.draw.rect(target_surface, door_color, self.rect)
		#if self.direction == 'vertical':
		#	pygame.draw.rect(target_surface, door_color, (door['x']*Room.grid_size -1,\
		#		door['y']*Room.grid_size +5, 3, Room.door_size))
		#else:
		#	pygame.draw.rect(target_surface, door_color, (door['x']*Room.grid_size + 5,\
		#		door['y']*Room.grid_size -1 , Room.door_size, 3))