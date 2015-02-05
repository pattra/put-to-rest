import pygame, os, sys
from pygame.locals import *
import Fight, Room, character, Tile, Grid, Object, Team
import random, astar, time, threading

class FightInterface(pygame.sprite.Sprite):
	'Comment'
	def load_image(self, image_name):
		try:
			image = pygame.image.load(image_name)
		except pygame.error, message:
			print "Cannot load image: " + image_name
			raise SystemExit, message
		return image.convert_alpha()

	def __init__(self, fight):
		self.fight = fight
		self.turnwindow = Rect((630, 300), (115, 25*7))
		self.statwindow = Rect((590, 10), (200, 150))
		self.font = pygame.font.Font('assets/ui/ftl01.ttf', 12)
		
	def draw(self, screen):
		# screen, color, rectangle((left, top), (width, height))
		
		# pygame.draw.rect(screen, (255,255,255), self.statwindow)

		self.drawCurrent(screen, self.fight.units, self.fight.current_unit_index)
		self.drawTurns(screen, self.fight.units, self.fight.current_unit_index)

	def drawCurrent(self, screen, units, current_unit_index):
		xpos = 600
		ypos = 20

		if current_unit_index < len(units):
			unit = units[current_unit_index]
			unit.draw_stats(screen,xpos,ypos)

	def drawTurns(self, screen, units, current_unit_index):
		# write data in turn window
		xpos = self.turnwindow.x
		ypos = self.turnwindow.y
		width = self.turnwindow.width

		# pygame.draw.rect(screen, (100,100,100), self.turnwindow)

		num_units = len(units)
		y_offset = 25
		max_y =	self.turnwindow.y+self.turnwindow.height

		cropped_image = pygame.Surface((10,10))
		index = current_unit_index
		color_drop = 0 
		color_drop_inc = 15
		for i in range (0, num_units):
			if ypos < max_y:
				unit = units[index]
				pygame.draw.rect(screen, (50,50,50), (xpos,ypos+4,width-10,17))
				pygame.draw.rect(screen, (50,50,50), (xpos,ypos+4,width-10,17),4)
				# portrait backdrop
				if unit.team.player:
					pygame.draw.rect(screen, (15,18,225), (xpos,ypos,25,25))
				else:
					pygame.draw.rect(screen, (215,8,4), (xpos,ypos,25,25))
				screen.blit(pygame.transform.scale(unit.image,(32,64)), (xpos+1, ypos), (0,0,25,25))
				screen.blit(self.font.render(unit.name, 1, (255, 255, 255)), (xpos+31, ypos+3))
				pygame.draw.rect(screen, (150-color_drop,150-color_drop,150-color_drop), (xpos,ypos,25,25), 3)
				color_drop+=color_drop_inc
				ypos = ypos + y_offset
				index += 1
				index %= num_units
			pygame.draw.rect(screen, (200,200,100), (self.turnwindow.x,self.turnwindow.y,25,25), 3)


if __name__ == "__main__":
	FPS = 50
	SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
	BACKGROUND_COLOR = (255, 255, 255)

	pygame.init()
	pygame.display.set_caption('Fight Interface')
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
	clock = pygame.time.Clock()

	room = Room.Room(0,0,4,4)
	fight = Fight.Fight(room, 1)
	menu = FightInterface(screen, fight)
	current_unit_index = 0

	while True:
		time_passed = clock.tick(FPS)

		# Event handling here
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()

		fight.draw(screen)
		menu.draw(fight.units, current_unit_index)

		pygame.display.flip()
		