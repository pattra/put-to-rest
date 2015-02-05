#TODO: ACTIONS 
# make base class extended by each type of action
# targetable types, range, aoe, effects
# json interpret for each 


class Action:

	def __init__(self, caster, loadJSON = None):
		self.caster = caster
		self.action = None
		self.finished = True
		if loadJSON:
			self.load_action(loadJSON)


	# Calle each update of unit
	def execute_action(self):
		pass

	def load_action(self):
		pass


	def health(self, target, amount):s
		target.health += amount

	def move_to(self, target, location):
		grid = self.caster.grid







