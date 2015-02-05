import pygame, os, sys, json, random
from pygame.locals import *
import Room, Tile, Fight, astar, Character
reload(Character)

class CharacterAI(Character.Character):

	
	def give_turn(self):
		super(Character.Character,self).give_turn()
		# AI Script
		if not self.team or not self.team.player:
			# for tile in self.movement_range
			# 	if tile.unit:
			# 		if unit.team != self.team:
			# 			target = tile.unit
			# 			x = 
			#AI STUFF
			x = max(0,min(self.grid.cols-1, self.current_tile.grid_x + random.randint(-2,2)))
			y = max(0,min(self.grid.rows-1, self.current_tile.grid_y + random.randint(-2,2)))
			self.path_to_tile = astar.astar(self.grid, self.current_tile,\
			self.grid.tiles[x][y])
			self.move(self.path_to_tile)

	def find_free_spot_near(self,x,y):
		pass