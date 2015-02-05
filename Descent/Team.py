import pygame, os, sys
from pygame.locals import *
import Room, Tile, character, Grid, Object
import random, astar, time, threading

class Team(pygame.sprite.Sprite):
	'comment'
	def __init__(self, name, player = False):
		self.units = []
		self.player = player
		self.name = name
	def add_unit(self, unit):
		if unit not in self.units:
			self.units.append(unit)
			unit.team = self