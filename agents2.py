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
		if key == 98: #'b'
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

		### YOUR CODE GOES ABOVE HERE ###



	def update(self, delta):
		Healer.update(self, delta)
		BehaviorTree.update(self, delta)
	
	
	def start(self):
		# Build the tree
		spec = healerTreeSpec(self)
		tree = myHealerBuildTree(self)
		if spec is not None and (isinstance(spec, list) or isinstance(spec, tuple)):
			self.myHealerBuildTree(spec)
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

