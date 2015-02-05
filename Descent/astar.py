import math
import Tile

def astar(graph,start,goal):
	if start.unit:
		unit = start.unit
	else:
		unit = None
	if start == goal:
		return [start,goal]
	closedset = set()   # The set of nodes already evaluated.
	openset = set([start])   # The set of tentative nodes to be evaluated, initially containing the start node
	came_from = {}   # The map of navigated nodes.
	# Cost fron start along best known path
	g_score = {}
	g_score[start] = 0
	# Estimated total cost from start to goal through y.
	f_score = {}
	f_score[start] = g_score[start] + heuristic_cost_estimate(start, goal)
	while len(openset) > 0:
		# the node in openset having the lowest f_score[] value
		current = min(openset, key = lambda node: f_score[node])
		if current == goal:
			return reconstruct_path(came_from,goal)
		# remove current from openset
		openset.remove(current)
		# add current to closedset
		closedset.add(current)
		for neighbor in graph.neighboring_tiles(current):
			if neighbor in closedset:
				continue
			tentative_g_score = g_score[current] + dist_between(current,neighbor)
			if neighbor not in openset or tentative_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = tentative_g_score
				f_score[neighbor] = g_score[neighbor] + heuristic_cost_estimate(neighbor, goal)
				#special
				if not unit or neighbor in unit.movement_range:
					if neighbor not in openset:
						openset.add(neighbor)
	return []

def dist_between(a, b):
	#return abs(a.grid_x - b.grid_x) + ()
	return math.sqrt((a.grid_x-b.grid_x)**2 + (a.grid_y-b.grid_y)**2)

def heuristic_cost_estimate (current, goal):
	#TODO: include in here slow terrain, jumps, etc
	cost = math.sqrt((current.grid_x-goal.grid_x)**2 + (current.grid_y-goal.grid_y)**2)
	return cost

def reconstruct_path(came_from, current_node):
	if came_from[current_node] in came_from:
		p = reconstruct_path(came_from, came_from[current_node])
		return (p + [current_node])
	else:
		return [current_node]