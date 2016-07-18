'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *
from agents import *
from moba4 import *
from behaviortree import *



############################################
### MOBAWorld2

class MOBAWorld2(MOBAWorld):

	def doKeyDown(self, key):
		MOBAWorld.doKeyDown(self, key)
		if key == K_e: #'b'
			if isinstance(self.agent, PlayerHero):
				self.agent.bark()

#############################################

class Barker():

	def bark(self):
		pass

	def hearBark(self, thebark):
		pass

############################################

class PlayerHero(Hero, Barker):
	
	def __init__(self, position, orientation, world, image = AGENT, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
		Hero.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)

	def die(self):
		Hero.die(self)
		mybase = self.world.getBaseForTeam(self.getTeam())
		'''
		offset = (mybase.getLocation()[0]-self.getLocation()[0],
		mybase.getLocation()[1]-self.getLocation()[1])
		self.move(offset)
		self.level = 0
		'''
		### Replace the player's avatar with a ghost avatar
		ghost = GhostAgent(GHOST, self.getLocation(), 0, SPEED, self.world, HITPOINTS, FIRERATE, None)
		ghost.setNavigator(Navigator())
		ghost.team = 0
		if self in self.world.movers:
			self.world.movers.remove(self)
		if self in self.world.sprites:
			self.world.sprites.remove(self)
		self.world.sprites.add(ghost)
		self.world.movers.append(ghost)
		self.world.agent = ghost

	def bark(self):
		Barker.bark(self)
		thebark = None
		### Set thebark to whatever is the contextually relevant thing (probably a string)
		### YOUR CODE GOES BELOW HERE ###

		### YOUR CODE GOES ABOVE HERE ###
		for n in self.world.getNPCsForTeam(self.getTeam()):
			if isinstance(n, Barker):
				n.hearBark(thebark)



##############################################
### Healer

class Healer(MOBAAgent, Barker):

	def __init__(self, position, orientation, world, image = GRUNT, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet, healrate = HEALRATE):
		MOBAAgent.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.healRate = healrate
		self.healTimer = 0
		self.canHeal = True


	def update(self, delta = 0):
		MOBAAgent.update(self, delta)
		if self.canHeal == False:
			self.healTimer = self.healTimer + 1
			if self.healTimer >= self.healRate:
				self.canHeal = True
				self.healTimer = 0

	def heal(self, agent):
		if self.canHeal:
			if isinstance(agent, MOBAAgent) and distance(self.getLocation(), agent.getLocation()) < self.getRadius() + agent.getRadius():
				agent.hitpoints = agent.maxHitpoints
				self.canHeal = False



###################################################
### MyHealer

class MyHealer(Healer, BehaviorTree):

	def __init__(self, position, orientation, world, image = GRUNT, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet, healrate = HEALRATE):
		Healer.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, healrate)
		BehaviorTree.__init__(self)
		self.states = []
		self.startState = None
		### YOUR CODE GOES BELOW HERE ###
		self.team = self.getTeam()

		### YOUR CODE GOES ABOVE HERE ###



	def update(self, delta):
		Healer.update(self, delta)
		BehaviorTree.update(self, delta)
	
	
	def start(self):
		# Build the tree
		spec = healerTreeSpec(self)
		tree = myHealerBuildTree(self)
		if spec is not None and (isinstance(spec, list) or isinstance(spec, tuple)):
			self.buildTree(spec)
		elif tree is not None:
			self.setTree(tree)
		elif len(self.states) > 0 and self.startState is not None:
			self.changeState(self.startState)
		# Start the agent
		Healer.start(self)
		BehaviorTree.start(self)
	
	
	def stop(self):
		Healer.stop(self)
		BehaviorTree.stop(self)

	def bark(self):
		Barker.bark(self)
		### YOUR CODE GOES BELOW HERE

		### YOUR CODE GOES ABOVE HERE

	def hearBark(self, thebark):
		Barker.hearBark(self, thebark)
		### YOUR CODE GOES BELOW HERE ###
		#pause beavhior tree?
		self.stop()
		#only goes to heal the healer if he barks at us
		hero = self.world.agent
		self.navigateTo(hero.getLocation())
		self.heal(hero)
		### YOUR CODE GOES ABOVE HERE ###

##########################################################

class MyCompanionHero(Hero, BehaviorTree, Barker):

	def __init__(self, position, orientation, world, image = AGENT, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
		Hero.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)
		BehaviorTree.__init__(self)
		self.states = []
		self.startState = None
		self.id = None
		### YOUR CODE GOES BELOW HERE ###

		### YOUR CODE GOES ABOVE HERE ###
	
	def bark(self):
		Barker.bark(self)
		### YOUR CODE GOES BELOW HERE
	
		### YOUR CODE GOES ABOVE HERE

	
	def update(self, delta):
		Hero.update(self, delta)
		BehaviorTree.update(self, delta)
	
	
	def start(self):
		# Build the tree
		spec = healerTreeSpec(self)
		tree = myCompanionBuildTree(self)
		if spec is not None and (isinstance(spec, list) or isinstance(spec, tuple)):
			self.buildTree(spec)
		elif tree is not None:
			self.setTree(tree)
		elif len(self.states) > 0 and self.startState is not None:
			self.changeState(self.startState)
		# Start the agent
		Hero.start(self)
		BehaviorTree.start(self)
	
	
	def stop(self):
		Hero.stop(self)
		BehaviorTree.stop(self)


	def bark(self):
		Barker.bark(self)
		### YOUR CODE GOES BELOW HERE

		### YOUR CODE GOES ABOVE HERE

	def hearBark(self, thebark):
		Barker.hearBark(self, thebark)
		### YOUR CODE GOES BELOW HERE
		### YOUR CODE GOES ABOVE HERE


##########################################################
### IDLE STATE

class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###

		### YOUR CODE GOES ABOVE HERE ###
		return None



###########################
### SET UP BEHAVIOR TREE


def healerTreeSpec(agent):
	myid = str(agent.getTeam())
	spec = None
	### YOUR CODE GOES BELOW HERE ###
	# spec = [Selector, [HealthDaemon, HealCompanion],[LeftSideDaemon, Formation], TacticalCover]
	spec = [Selector, [LeftSideDaemon, Formation]]#, TacticalCover]
	#LANSSIE STUFF
	# spec = [(Selector, 'staring the healer'), 
	# 			[(HealerDaemon, 'can the healer heal yet'), 
	# 				[(Sequence, 'healing team'), (HealClosestTeammate, 'Healing Teammate')]
	# 			],
	# 			[(Sequence, 'doing basic movement'), (FindCover, 'finding cover')]
	# 		]
	### YOUR CODE GOES ABOVE HERE ###
	return spec

def myHealerBuildTree(agent):
	myid = str(agent.getTeam())
	root = None
	### YOUR CODE GOES BELOW HERE ###
	
	### YOUR CODE GOES ABOVE HERE ###
	return root

def companionTreeSpec(agent):
	myid = str(agent.getTeam())
	spec = None
	### YOUR CODE GOES BELOW HERE ###
	
	### YOUR CODE GOES ABOVE HERE ###
	return spec

def myCompanionBuildTree(agent):
	myid = str(agent.getTeam())
	root = None
	### YOUR CODE GOES BELOW HERE ###
	
	### YOUR CODE GOES ABOVE HERE ###
	return root

### Helper function for making BTNodes (and sub-classes of BTNodes).
### type: class type (BTNode or a sub-class)
### agent: reference to the agent to be controlled
### This function takes any number of additional arguments that will be passed to the BTNode and parsed using BTNode.parseArgs()
def makeNode(type, agent, *args):
	node = type(agent, args)
	return node



##########################################################
### YOUR STATES AND BEHAVIORS GO HERE

# FINDING COVER AS THE DEFAULT STATE OF BEING FOR HEALERS AND POSSIBLY OTHER MINIONS?
class FindCover(BTNode):
	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		self.timer = 50
		# First argument is the factor
		if len(args) > 0:
			self.percentage = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def enter(self):
		BTNode.enter(self)
		#temporary go to base, but should go to nearest obstacle cover area
		self.agent.navigateTo(self.agent.world.getBaseForTeam(self.agent.getTeam()).getLocation())

	def execute(self):
		ret = BTNode.execute(self, delta)
		# if self.agent.getHitpoints() > self.agent.getMaxHitpoints():
		# 	# fail executability conditions
		# 	print "exec", self.id, "false"
		# 	return False
		# elif self.agent.getHitpoints() == self.agent.getMaxHitpoints():
		# 	# Exection succeeds
		# 	print "exec", self.id, "true"
		# 	print 'IM GOING TO RETREAT'
		# 	return True
		# else:
		# 	# executing
		# 	return None
		return ret
class LeftSideDaemon(BTNode):
	### percentage: percentage of hitpoints that must have been lost to fail the daemon check

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.percentage = 0.4
		# First argument is the factor
		if len(args) > 0:
			self.percentage = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def execute(self, delta=0):
		ret = BTNode.execute(self, delta)
		world  = self.agent.world

		# currently, no logic implemented
		return self.getChild(0).execute(delta)

		return ret


class Formation(BTNode):

	### target: the hero to chase
	### timer: how often to replan
	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		self.timer = 50
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]
	def getHero(self,npc_list):
		hero = None
		for i in npc_list:
			if isinstance(i,PlayerHero):
				return i
		return None
	def enter(self):
		BTNode.enter(self)
		self.timer = 50

		#nodes to navigate to; these are points around the main character
		# ... right now, this is a placeholder...
		#  should be calculated on update for the hero; the id of the
		# heros indexes the nodes list
		hero = self.getHero(self.agent.world.getNPCsForTeam(self.agent.getTeam()))
		nodes = hero.nodes
		orientations = [self.agent.orientation,self.agent.orientation,self.agent.orientation]

		self.formation_node = nodes[self.agent.id]
		self.orientation = orientations[self.agent.id]

		self.agent.turnToAngle(self.orientation)
		self.agent.navigateTo(self.formation_node)
		return None

	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)

		#region Formation Variables
		hero = self.getHero(self.agent.world.getNPCsForTeam(self.agent.getTeam()))
		self.formation_node = hero.nodes[self.agent.id]
		self.orientation = hero.orientation
		#endregion

		self.agent.turnToAngle(self.orientation)
		if self.agent.navigator.doneMoving():
			return True
		else:
			# executing
			self.timer = self.timer - 1
			if self.timer <= 0 or distance(self.agent.position,self.formation_node) > 5:
				self.timer = 50
				self.agent.navigateTo(self.formation_node)
			return None
		return ret

class HealClosestTeammate(BTNode):

	### target: the minion to chase
	### timer: how often to replan

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		self.timer = 50
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]

	def enter(self):
		BTNode.enter(self)
		self.timer = 50
		team = self.agent.world.getNPCsForTeam(self.agent.getTeam())
		if len(team) > 0:
			best = None
			HP = 0
			for e in team:
				if isinstance(e, Minion):
					hp = e.getHitpoints()
					if best == None or HP > hp:
						best = e
						HP = hp
			self.target = best
		if self.target is not None:
			navTarget = self.chooseNavigationTarget()
			if navTarget is not None:
				self.agent.navigateTo(navTarget)


	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target == None or self.target.isAlive() == False:
			# failed execution conditions
			print "exec", self.id, "false"
			return False
		# elif distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE:
		# 	# succeeded
		# 	print 'IM FINDING TEAM NOW'
		# 	print "exec", self.id, "true"
		# 	return True
		else:
			# executing
			self.timer = self.timer - 1
			if self.timer <= 0:
				self.timer = 50
				navTarget = self.chooseNavigationTarget()
				if navTarget is not None:
					self.agent.navigateTo(navTarget)
			return None
		return ret

#LANSSIE HEALER THINGS
# FINDING COVER AS THE DEFAULT STATE OF BEING FOR HEALERS AND POSSIBLY OTHER MINIONS?
class FindCover(BTNode):
	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		self.timer = 50
		# First argument is the factor
		if len(args) > 0:
			self.percentage = args[0]
		# Second argument is the node ID
		if len(args) > 1:
			self.id = args[1]

	def enter(self):
		BTNode.enter(self)
		#temporary go to base, but should go to nearest obstacle cover area
		self.agent.navigateTo(self.agent.world.getBaseForTeam(self.agent.getTeam()).getLocation())

	def execute(self):
		ret = BTNode.execute(self, delta)
		# if self.agent.getHitpoints() > self.agent.getMaxHitpoints():
		# 	# fail executability conditions
		# 	print "exec", self.id, "false"
		# 	return False
		# elif self.agent.getHitpoints() == self.agent.getMaxHitpoints():
		# 	# Exection succeeds
		# 	print "exec", self.id, "true"
		# 	print 'IM GOING TO RETREAT'
		# 	return True
		# else:
		# 	# executing
		# 	return None
		return ret

class HealClosestTeammate(BTNode):

	### target: the minion to chase
	### timer: how often to replan

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.target = None
		self.timer = 50
		# First argument is the node ID
		if len(args) > 0:
			self.id = args[0]

	def enter(self):
		BTNode.enter(self)
		self.timer = 50
		team = self.agent.world.getNPCsForTeam(self.agent.getTeam())
		if len(team) > 0:
			best = None
			HP = 0
			for e in team:
				if isinstance(e, Minion):
					hp = e.getHitpoints()
					if best == None or HP > hp:
						best = e
						HP = hp
			self.target = best
		if self.target is not None:
			navTarget = self.chooseNavigationTarget()
			if navTarget is not None:
				self.agent.navigateTo(navTarget)


	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		if self.target == None or self.target.isAlive() == False:
			# failed execution conditions
			print "exec", self.id, "false"
			return False
		# elif distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE:
		# 	# succeeded
		# 	print 'IM FINDING TEAM NOW'
		# 	print "exec", self.id, "true"
		# 	return True
		else:
			# executing
			self.timer = self.timer - 1
			if self.timer <= 0:
				self.timer = 50
				navTarget = self.chooseNavigationTarget()
				if navTarget is not None:
					self.agent.navigateTo(navTarget)
			return None
		return ret

	def chooseNavigationTarget(self):
		if self.target is not None:
			return self.target.getLocation()
		else:
			return None

class HealerDaemon(BTNode):

	### HEALS IF WE CAN 

	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.advantage = 0
		# First argument is the advantage
		if len(args) > 0:
			self.id = args[0]

	def execute(self, delta = 0):
		ret = BTNode.execute(self, delta)
		hero = None
		# Get a reference to the enemy hero
		enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())

		if self.canHeal:
			return self.getChild(0).execute(delta)
		else:
			#check if timer is < time it takes to get to the player?
			return False
			# Check didn't fail, return child's status
			# return self.getChild(0).execute(delta)
		return ret
	