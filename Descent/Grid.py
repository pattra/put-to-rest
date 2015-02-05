import pygame, os, sys
from pygame.locals import *
import Room, Tile, character
import random, astar, math

# Manages the grid and movement for the fight, calculating shortest paths and movement ranges and such
class Grid(pygame.sprite.Sprite):
	grid_size = 25
	vision = False
	def __init__(self, rect):
		# Create rect 
		self.rect = rect

		# Tiles
		self.show_grid = True
		self.cols = self.rect.width/Grid.grid_size
		self.rows = self.rect.height/Grid.grid_size
		self.tiles = [[None for j in range(self.rows)] for i in range(self.cols)]

	#TODO: rename to indicate that it returns WALKABLE neighboring tiles
	def neighboring_tiles(self, tile):
		neighbors = []
		x,y = tile.grid_x, tile.grid_y
		for i in xrange(x-1,x+2,2):
			if len(self.tiles) > i and i >= 0 and len(self.tiles[0]) > y and y >= 0:
				tile = self.tiles[i][y]
				if tile.is_pathable(None):
					neighbors.append(tile)

		for j in xrange(y-1,y+2,2):
			if len(self.tiles) > x and x >= 0 and len(self.tiles[0]) > j and j >= 0:
				tile = self.tiles[x][j]
				if tile.is_pathable(None):
					neighbors.append(tile)
		return neighbors


	def get_movement_range(self, character_tile):
		character = character_tile.unit
		max_dist = character.speed
		dist = {} # walking distance from character
		stack = []
		move_range = [character_tile]
		perimeter = []
		for tile in self.neighboring_tiles(character_tile) :
				dist[tile] = 1
				stack.append(tile)
		while len(stack) > 0:
			tile = stack[0]
			stack.remove(tile)
			if tile not in move_range:
				move_range.append(tile)
				if dist[tile] < max_dist:
					for neighbor in self.neighboring_tiles(tile):
						#SPECIAL:
						if not Grid.vision or neighbor in character.vision_range:
							if neighbor not in move_range:
								dist[neighbor] = dist[tile] + 1 
								stack.append(neighbor)
		return move_range

	def get_vision_range(self,character_tile):
		unit = character_tile.unit
		vision_range = [character_tile]
		for i in xrange(0, 361, 3): 
			ax = math.sin(i)#sintable[i] # Get precalculated value sin(x / (180 / pi))
			ay = math.cos(i)#costable[i] # cos(x / (180 / pi))

			x,y = character_tile.grid_x, character_tile.grid_y

			for z in range(unit.vision): # Cast the ray
				x += ax
				y += ay
				rx, ry = int(round(x)), int(round(y))
				if rx < 0 or ry < 0 or rx > self.cols-1 or ry > self.rows-1: # If ray is out of range
					break
				# Stop ray if it hits wall.
				if self.tiles[rx][ry].vision_past: 
					if self.tiles[rx][ry] not in vision_range:
						vision_range.append(self.tiles[rx][ry])
				else:
					break
				
		return vision_range                    

	def get_attack_range(self,character_tile):
		unit = character_tile.unit
		attack_range = []
		for i in xrange(0, 361, 3): 
			ax = math.sin(i)#sintable[i] # Get precalculated value sin(x / (180 / pi))
			ay = math.cos(i)#costable[i] # cos(x / (180 / pi))

			x,y = character_tile.grid_x, character_tile.grid_y

			for z in range(unit.min_range):
				x += ax
				y += ay
			for z in xrange(unit.min_range,unit.max_range): # Cast the ray
				x += ax
				y += ay
				rx, ry = int(round(x)), int(round(y))
				if rx < 0 or ry < 0 or rx > self.cols-1 or ry > self.rows-1: # If ray is out of range
					break
				# Stop ray if it hits wall???
				if self.tiles[rx][ry]: 
					if self.tiles[rx][ry] not in attack_range:
						attack_range.append(self.tiles[rx][ry])
				else:
					break
				
		return attack_range 

	def get_attackable_spot(self,attacker_tile, target_tile):
		attacker = attacker_tile.unit
		variance = attacker.max_range - attacker.min_range 
		angle = self.angle_between(attacker_tile.grid_x,attacker_tile.grid_y,\
			target_tile.grid_x,target_tile.grid_y)
		for i in xrange(- 6, 6, 3): 
			a = angle + i
			ax = math.sin(a)#sintable[i] # Get precalculated value sin(x / (180 / pi))
			ay = math.cos(a)#costable[i] # cos(x / (180 / pi))
			x,y = target_tile.grid_x, target_tile.grid_y
			# Cast the ray
			for z in range(attacker.min_range):
				x += ax
				y += ay
			for z in range(variance):
				x += ax
				y += ay
				rx, ry = int(round(x)), int(round(y))   
				if rx < 0 or ry < 0 or rx > self.cols-1 or ry > self.rows-1: # If ray is out of range
						return None
				potential_tile = self.tiles[rx][ry]
				if potential_tile:
					if potential_tile in attacker.movement_range:
						return potential_tile
		return None

	def angle_between(self,x1,y1,x2,y2):
		dx = x2 - x1
		dy = y2 - y1
		rads = math.atan2(-dy,dx)
		rads %= 2*math.pi
		degs = math.degrees(rads)
		return degs

