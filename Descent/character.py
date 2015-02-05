import pygame, os, sys, json, random
from pygame.locals import *
import Room, Tile, Fight, astar
#TODO: Make action their own class

class Character(pygame.sprite.Sprite):
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

	def __init__(self, unit, team, party = None, player_file = None):
		'comment'
		pygame.sprite.Sprite.__init__(self) #call Sprite intializer
		# Read Character Data File
		self.unit = unit
		self.player_file = player_file
		self.party = party
		if self.party:
			manual = self.party['characters'][unit]
		else:
			with open('json/Characters.json') as data_file:    
				manual = json.load(data_file)[unit]
			data_file.close()
		self.manual = manual

		# Load Images
		self.image = self.load_image(manual['image'])
		self.image_w, self.image_h = self.image.get_size()
		scale = 1.0
		self.image = pygame.transform.scale((self.image), \
			( int(round(self.image_w*scale)), int(round(self.image_h*scale))))
		self.image_w, self.image_h = self.image.get_size()
		self.projectile_image = self.load_image(manual['projectile_image'])
	
		# Generate Dark Image
		self.dark_image = self.image.copy()
		arr = pygame.surfarray.pixels3d(self.dark_image)
		arr[:,:,0],arr[:,:,1],arr[:,:,2] = 20,20,20
		# Create Rectangle
		width = Character.grid_size
		height = Character.grid_size
		self.rect = pygame.Rect(0,0,width,height)

		# Stats
		self.speed = manual['speed']
		self.vision = manual['vision']
		self.health = manual['health']
		self.max_health = manual['max_health']
		self.initiative = manual['initiative']

		self.min_range = manual['min_range']
		self.max_range = manual['max_range']
		if manual.get('experience'):
			self.experience = manual['experience']
			self.experience_to_level = manual['experience_to_level']
			self.level = manual['level']
		else:
			self.experience = 0
			self.experience_to_level = 100
			self.level = 1

		self.alive = True

		# TODO: check if dead
		#if self.manual['alive'] == 1:
		#	self.alive = True
		#else:
		#	self.alive = False

		# print manual['alive']

		#if manual['alive'] == 1:
		#	self.alive = True
		#else:
		#	self.alive = False

		# Todo (far in the future) replace this stat with weapons, items, spells, etc
		self.damage = manual['damage']
		self.heal = None
		if manual.get('heal'):
			self.heal = manual['heal']

		# Name
		if manual.get('name'):
			self.name = manual['name']
		else:
			self.name = manual['names'][random.randint(0,len(manual['names'])-1)]

		# Actions
		self.action = 'idle'
		self.actionQueue = []
		self.team = team
		self.team.add_unit(self)
		self.actions_points = {'move':1,'attack':1}
		self.current_action_points = self.actions_points.copy()
		self.turn = False

		# Movement
		self.grid = None
		self.current_tile = None
		self.path_to_tile = []
		self.movement_range = []
		self.vision_range = []
		self.attack_range = []
		# if grid:
		# 	self.set_tile(grid.tiles[x][y])

		# Interface
		self.highlighted_tile = None
		self.selected = False

		# Stat Screen
		self.font = pygame.font.Font('assets/ui/ftl01.ttf', 12)
		self.damage_image = pygame.transform.scale(self.load_image('assets/ui/damage.png'), (23,23))
		self.heal_image = pygame.transform.scale(self.load_image('assets/ui/heal.png'),(22,22))
		self.range_image = pygame.transform.scale(self.load_image('assets/ui/range.png'),(20,20))
		self.vision_image = pygame.transform.scale(self.load_image('assets/ui/vision.png'),(20,20))
		self.speed_image = pygame.transform.scale(self.load_image('assets/ui/boots.png'),(18,18))
		self.initiative_image = pygame.transform.scale(self.load_image('assets/ui/init.png'),(19,19))

		# Sound
		self.attack_sound = None
		if str(self.unit) == 'thief' or 'ghost_melee' in str(self.unit):
			self.attack_sound = pygame.mixer.Sound("assets/sounds/sword2.wav")

		# AI
		self.fight_units = []

	def die(self):
		self.alive = False
		self.current_tile.unit = None

	def set_highlighted_tile(self, tile):
		self.highlighted_tile = tile

	def init_to_grid(self,grid,x,y):
		self.grid = grid
		self.set_tile(grid.tiles[x][y])

	def set_tile(self, tile):
	
		self.rect.topleft = tile.rect.topleft
		if self.current_tile:
			self.current_tile.unit = None
		self.current_tile = tile

		# BIG UH OH IF THIS HAPPENS
		if not self.current_tile.unit:
			self.current_tile.unit = self

	def give_turn(self):
		self.turn = True
		self.current_action_points = self.actions_points.copy()
		self.update_action_tiles()

	def move(self, path):
		if self.turn:
			self.actionQueue.append({'action':'walk', 'path':path})
			if self.action == 'idle':
				self.action = 'active'

	def attack(self, target_tile):
		if self.turn:
			self.actionQueue.append({'action':'attack', 'projectile':True, 'target_tile':target_tile,\
				'projectile_x':self.rect.x, 'projectile_y':self.rect.y})
			self.action = 'active'
			if self.attack_sound:
				self.attack_sound.play()

	# Deal Damage
	def affect_health(self, dealer, amount):
		diff = self.health
		self.health += amount
		if self.health > self.max_health:
			self.health = self.max_health
		diff = diff - self.health
		# Prevent getting exp for not doing anything...
		if diff != 0:
			dealer.affect_experience(50)

	def affect_experience(self, amount):
		self.experience += amount
		if self.experience >= self.experience_to_level:
			self.experience %= self.experience_to_level
			self.experience_to_level *= 1.5
			self.level += 1
			# "level_gain" :{"health":1,"damage":0.5,"initiative":0.5},
			if self.manual.get('level_gain'):
				for stat in self.manual['level_gain']:
					if self.__dict__.get(stat):
						self.__dict__[stat] += self.manual['level_gain'][stat]

		elif self.experience < 0 and self.level > 0:
			self.level -= 1

	def mouse_event(self, event):
		if self.selected and self.turn:
			if event.type == pygame.MOUSEBUTTONDOWN:	
				if self.action == 'idle':
					# Move stage
					if self.movement_range:
						if self.highlighted_tile in self.movement_range and \
						(self.highlighted_tile.unit == self or not self.highlighted_tile.unit):
							self.move(self.path_to_tile)
					# Attack stage
					elif self.attack_range:
						if self.highlighted_tile in self.attack_range:
							self.attack(self.highlighted_tile)
	
	def draw(self, surface):
		if self.selected and self.turn:
			# Draw Path from current_tile to highlighted_tile
			if self.path_to_tile:
				color = 0x9999bb
				#pygame.draw.line(surface,color, self.current_tile.rect.center, self.path_to_tile[0].rect.center, 4)
				pygame.draw.line(surface,color, self.rect.center, self.path_to_tile[0].rect.center, 4)
				for i in range(len(self.path_to_tile)-1):
					pygame.draw.line(surface,color, self.path_to_tile[i].rect.center, self.path_to_tile[i+1].rect.center, 4)	
		# Check if a player unit can see this
		seen_by_player_unit = False
		for unit in self.current_tile.vision_range:
			if unit.team.player:
				seen_by_player_unit = True
				break
		if seen_by_player_unit:
			surface.blit(self.image, (self.rect.x+5, self.rect.y-8))
		else:
			surface.blit(self.dark_image, (self.rect.x+5, self.rect.y-8))

		# Draw Projectile
		if len(self.actionQueue) > 0:
			current_action = self.actionQueue[0]
			if 'projectile' in current_action:
				projectile_x = current_action['projectile_x']
				projectile_y = current_action['projectile_y']
				surface.blit(self.projectile_image, (projectile_x+8, projectile_y+8))

		# Highlighted
		if self.current_tile.highlighted:
			# Draw health bar
			color = 0xaaaaaa
			pygame.draw.rect(surface, color, (self.rect.x,self.rect.y-16,self.rect.width+1,4), 3)
			color = 0x888888
			pygame.draw.rect(surface, color, (self.rect.x+1,self.rect.y-15,self.rect.width,3), 3)	
			if self.health > 0:
				color = 0xaa0000
				pygame.draw.rect(surface, color, (self.rect.x+1,self.rect.y-15,self.rect.width*(self.health/float(self.max_health)),3), 3)	
	
	def draw_stats(self,screen, x, y):
		xpos, ypos = x,y

		bigw = 60
		bigh = 128
		xoffset = 10
		yoffset = 30
		newline = 20

		line1 = "Active Character"
		line2 = self.name
		line3 = "Lvl: " + str(self.level)

		# scale image to be larger
		screen.blit(pygame.transform.scale(self.image, (64,128)), (xpos, ypos))
		screen.blit(self.font.render(line1, 1, (225, 225, 225)), (xpos+bigw+xoffset+3, ypos+yoffset))
		screen.blit(self.font.render(line2, 1, (225, 225, 225)), (xpos+bigw+xoffset+3, ypos+yoffset+newline))
		if self.team.player:
			screen.blit(self.font.render(line3, 1, (225, 225, 225)), (xpos+bigw+xoffset+73, ypos+yoffset+newline))
		
		xpos = xpos + bigw + xoffset
		ypos = ypos + yoffset + (newline*2)
		heartoffset = 16

		# # draw current health
		# health = self.health
		# maxhealth = self.max_health
		# half = False
		# for i in range (0, int(health)):
		# 	screen.blit(self.heart, (xpos, ypos))
		# 	xpos = xpos + heartoffset
		# if int((health*10) % 10) == 5:
		# 	screen.blit(self.half, (xpos, ypos))
		# 	xpos = xpos + heartoffset
		# 	half = True
		# for i in range (0, int(maxhealth - health)):
		# 	screen.blit(self.empty, (xpos, ypos))
		# 	xpos = xpos + heartoffset

		# draw health
		xpos = x+75
		ypos = y+80
		pygame.draw.rect(screen, (100,100,100), (xpos,ypos,100,10))
		if self.health > 0:
			pygame.draw.rect(screen, (200,80,80), \
				(xpos,ypos,100* self.health/float(self.max_health),10))
			pygame.draw.rect(screen, (200,80,80), \
				(xpos,ypos,100* self.health/float(self.max_health),10), 3)
		pygame.draw.rect(screen, (100,100,100), (xpos,ypos,100,10), 3)


		# draw exp
		if self.team.player:
			xpos = x+75
			ypos = y+100
		
			
			pygame.draw.rect(screen, (100,100,100), (xpos,ypos,100,10))
			if self.experience > 0:
				pygame.draw.rect(screen, (80,100,200), \
					(xpos,ypos,100* self.experience/float(self.experience_to_level),10))
				pygame.draw.rect(screen, (80,100,200), \
					(xpos,ypos,100* self.experience/float(self.experience_to_level),10), 3)
			pygame.draw.rect(screen, (100,100,100), (xpos,ypos,100,10), 3)

		# Draw stats
		xpos = x+30
		ypos = y+140
		spacing = 40
		y_offset = 21
		text_y = -2
		if self.damage > 0:
			screen.blit(self.damage_image, (xpos, ypos))
			screen.blit(self.font.render(str(self.damage), 1, (225, 225, 225)), (xpos+spacing, ypos+text_y))
			ypos +=y_offset
		if self.heal > 0:
			screen.blit(self.heal_image, (xpos, ypos))
			screen.blit(self.font.render(str(self.heal), 1, (225, 225, 225)), (xpos+spacing, ypos+text_y))
			ypos +=y_offset
		screen.blit(self.range_image, (xpos, ypos))
		screen.blit(self.font.render(str(self.min_range) +" - "+str(self.max_range), 1, (225, 225, 225)), (xpos+spacing, ypos+text_y))
		ypos +=y_offset
		screen.blit(self.speed_image, (xpos+2, ypos))
		screen.blit(self.font.render(str(self.speed), 1, (225, 225, 225)), (xpos+spacing, ypos+text_y))
		ypos +=y_offset
		screen.blit(self.vision_image, (xpos, ypos))
		screen.blit(self.font.render(str(self.vision), 1, (225, 225, 225)), (xpos+spacing, ypos+text_y))
		ypos +=y_offset
		screen.blit(self.initiative_image, (xpos+2, ypos))
		screen.blit(self.font.render(str(self.initiative), 1, (225, 225, 225)), (xpos+spacing, ypos+text_y))
	
	def update(self):
		if self.selected:
			if self.action == 'idle' and self.movement_range:
				if self.highlighted_tile in self.movement_range:
					# if there is no path made already or the path isnt the same path already made
					if not self.path_to_tile or self.path_to_tile[len(self.path_to_tile)-1] != self.highlighted_tile:
						self.path_to_tile = astar.astar(self.grid, self.current_tile, self.highlighted_tile)

		# Action Queue
		if self.turn and len(self.actionQueue) > 0:
			current_action = self.actionQueue[0]
			self.action = current_action['action']
			if current_action['action'] == 'walk':
				path = current_action['path']
				if path:
					tile = path[0]
					if self.rect.x == tile.rect.x and self.rect.y == tile.rect.y:
						self.set_tile(tile)
						path.remove(tile)
					else:
						if self.rect.x != tile.rect.x:
							self.rect.x -= max(-self.speed, min(self.speed, self.rect.x-tile.rect.x))
						if self.rect.y != tile.rect.y:
							self.rect.y -= max(-self.speed, min(self.speed, self.rect.y-tile.rect.y))
					# Action complete
					if len(path) <= 0:
						self.actionQueue.remove(current_action)
						self.current_action_points['move'] -= 1
					# Update Movement Range since new location 
					# Note move this into completion event if u want this to only happen at end of action
					# self.update_action_tiles()
					#self.attack_range = self.grid.get_attack_range(self.current_tile)
				else: # Don't know why this would happen, but just in case - maybe make a catch
					self.actionQueue.remove(current_action)
					self.current_action_points['move'] -= 1
				self.update_action_tiles()
			elif current_action['action'] == 'attack':
				target_tile =  current_action['target_tile']
				if current_action['projectile_x'] ==  target_tile.rect.x \
				and current_action['projectile_y'] ==  target_tile.rect.y:
					# If unit there, deal projectile damage
					if target_tile.unit:
						if self.heal and target_tile.unit.team == self.team:
					 		target_tile.unit.affect_health(self, self.heal)
					 	else:
					 		target_tile.unit.affect_health(self, -self.damage)
					self.actionQueue.remove(current_action)
					self.current_action_points['attack'] -= 1
				else:
					if current_action['projectile_x'] != target_tile.rect.x:
						current_action['projectile_x'] -= \
						max(-self.speed*.75, min(self.speed*.75, current_action['projectile_x']-target_tile.rect.x))
					if current_action['projectile_y'] != target_tile.rect.y:
						current_action['projectile_y'] -= \
						max(-self.speed*.75, min(self.speed*.75, current_action['projectile_y']-target_tile.rect.y))
		else: 
			self.action = 'idle'
			# Turn Evaluation
			if self.turn:
				actions_left = False
				for action in self.current_action_points:
					if self.current_action_points[action] > 0:
						actions_left = True
						break
				self.turn = actions_left

	def update_action_tiles(self):
		# Wipe old
		if self.movement_range:
			for tile in self.movement_range:
				tile.movement_range.remove(self)
		if self.vision_range:
			for tile in self.vision_range:
				tile.vision_range.remove(self)
		if self.attack_range:
			for tile in self.attack_range:
				tile.attack_range.remove(self)

		if self.alive:
			self.vision_range = self.grid.get_vision_range(self.current_tile)
			if self.current_action_points['move'] > 0:
				self.movement_range = self.grid.get_movement_range(self.current_tile)
				self.attack_range = None
			else:
				self.movement_range = None
				if self.current_action_points['attack'] > 0:
					self.attack_range = self.grid.get_attack_range(self.current_tile)
					# If no units to interact with, skip attack phase
					if self.team.player:
						something_to_interact = False
						for tile in self.attack_range:
							if (self.attack > 0 and tile.unit and not tile.unit.team.player) or \
								(self.heal > 0 and tile.unit and tile.unit.team.player):
								something_to_interact = True
						if not something_to_interact:
							self.attack_range = None
							self.current_action_points['attack'] -= 1
				else:
					self.attack_range = None

			# Update new
			if self.movement_range:
				for tile in self.movement_range:
					tile.movement_range.append(self)
			if self.vision_range:
				for tile in self.vision_range:
					tile.vision_range.append(self)
			if self.attack_range:
				for tile in self.attack_range:
					tile.attack_range.append(self)

	def save_to_file(self):
		if self.alive == True:
			self.manual['speed'] = self.speed 
			self.manual['vision'] = self.vision 
			self.manual['health'] = self.health
			self.manual['max_health'] = self.max_health
			self.manual['initiative'] = self.initiative
			self.manual['min_range'] = self.min_range
			self.manual['max_range'] = self.max_range
			self.manual['experience'] = self.experience
			self.manual['experience_to_level'] = self.experience_to_level
			self.manual['level'] = self.level
			if self.alive == True:
				self.manual['alive'] = 1
			else:
				self.manual['alive'] = 0

			jsonFile = open("json/" + str(self.player_file), "r")
			data = json.load(jsonFile)
			jsonFile.close()

			data['characters'][self.unit] = self.manual

			jsonFile = open("json/" + str(self.player_file), "w+")
			jsonFile.write(json.dumps(data))
			jsonFile.close()



class CharacterAI(Character):
	
	# def give_turn(self):
	# 	super(CharacterAI,self).give_turn()
	# 	# AI Script -- Determine where to move
	# 	if not self.team or not self.team.player:
	# 		# unit_in_range = False
	# 		# for tile in self.movement_range:
	# 		# 	if tile.unit:
	# 		# 		if tile.unit.team != self.team:
	# 		# 			target_tile = self.find_free_spot_near(tile)
	# 		# 			if target_tile:
	# 		# 					self.path_to_tile = astar.astar(self.grid, self.current_tile,target_tile)
	# 		# 					self.move(self.path_to_tile)
	# 		# 					unit_in_range = True
	# 		# 					break
	# 		# if not unit_in_range:
	# 		# 	while True:
	# 		# 		tile = random.choice(self.movement_range)
	# 		# 		if not tile.unit and tile.is_pathable(self):
	# 		# 			self.path_to_tile = astar.astar(self.grid, self.current_tile,tile)
	# 		# 			self.move(self.path_to_tile)
	# 		# 			break;
			
					
	def update(self):
		super(CharacterAI,self).update()
		# AI Script -- Determine what to attack
		if self.turn and self.action == 'idle':
			if self.current_action_points["move"] > 0:
				unit_in_range = False
				for unit in self.fight_units:
					if unit.team != self.team:
						attack_tile = self.grid.get_attackable_spot(self.current_tile,unit.current_tile)
						if attack_tile and not attack_tile.unit:
							self.path_to_tile = astar.astar(self.grid, self.current_tile,attack_tile)
							self.move(self.path_to_tile)
							unit_in_range = True
							break
				
				if not unit_in_range:
					attempts_max = 50
					attempts = 0
					while True and attempts < attempts_max:
						attempts += 1
						tile = random.choice(self.movement_range)
						if not tile.unit and tile.is_pathable(self):
							self.path_to_tile = astar.astar(self.grid, self.current_tile,tile)
							self.move(self.path_to_tile)
							break
					if attempts >= attempts_max:
						self.path_to_tile = astar.astar(self.grid, self.current_tile,self.current_tile)
						self.move(self.path_to_tile)
			else:
				if self.current_action_points["attack"] > 0:
					unit_in_range = False
					if self.attack_range and len(self.attack_range) > 0:
						# print str(self.current_tile.grid_x) + ":"+ str(self.current_tile.grid_y)
						for tile in self.attack_range:
							# print str(tile.grid_x) + ":"+ str(tile.grid_y)
							if tile.unit:
								# print "unit in my range:" + str(tile.unit.name)
								if tile.unit.team.player:
									self.attack(tile)
						if not unit_in_range:
							self.current_action_points["attack"] -= 1
					else:
						self.current_action_points["attack"] -= 1

	def find_free_spot_near(self,tile):
		for i in range(tile.grid_x-1,tile.grid_x+1):
			for j in range(tile.grid_y-1,tile.grid_y+1):
				tile = self.grid.tiles[i][j]
				if tile:
					if tile.is_pathable(self) and (not tile.unit):
						return tile
		return None

