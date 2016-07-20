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
from cover_and_shadow_functions import *


############################################
### MOBAWorld2
def roomForFormation(point, MOBAWorld):
    # Complete this
    worldlines = MOBAWorld.getLines()

    for line in worldlines:
        if minimumDistance(line, point) < 150:
            return False
    return True


class MOBAWorld2(MOBAWorld):
    def getBaseShadows(self):
        ###################### Our Code Here
        all_bases = self.getBases()
        enemy_base_index = numpy.argmax([base.position[0] for base in all_bases])
        enemy_base = all_bases[enemy_base_index]
        manual_obstacles = self.getObstacles()
        manual_obstacle_shadowParams = [ShadowParams(manual_obstacle, origin=enemy_base.position, gui_modifier=(1, -1))
                                        for manual_obstacle in manual_obstacles]

        self.obstacleShadows = manual_obstacle_shadowParams;


    def doKeyDown(self, key):
        MOBAWorld.doKeyDown(self, key)
        if key == K_e:  # 'e'
            if isinstance(self.agent, PlayerHero):
                self.agent.bark()
        return None


    def getCoverNodes(self):
        ###################### Our Code Here
        all_bases = self.getBases()
        enemy_base_index = numpy.argmax([base.position[0] for base in all_bases])
        enemy_base = all_bases[enemy_base_index]

        cover_nodes = []
        for shadow in self.obstacleShadows:
            cover_nodes.append(GamePoint_From_RelativePolarCoordinate((shadow[0], shadow[1]), enemy_base.position))
            # preliminary_point_polar = (shadow[0] + 200,shadow[2]+(shadow[1]-shadow[2]/2))
            # search_radius = 200
            # point_found = False
            # iteration_counter = 0
            # while not point_found and iteration_counter < 100:
            # 	test_r = numpy.random.randint(preliminary_point_polar[0] - search_radius,high = preliminary_point_polar[0] + search_radius)
            # 	test_theta = 0.5*(numpy.random.random() - 0.5)*(shadow[1]-shadow[2]/2) + preliminary_point_polar[1]
            #
            # test_cartesian = GamePoint_From_RelativePolarCoordinate((test_r,test_theta),enemy_base.position)
            #
            # if (roomForFormation(test_cartesian,self)):
            # point_found = True
            # cover_nodes.append(test_cartesian)
            # iteration_counter +=1;
        self.obstacleCoverNodes = cover_nodes


    def update(self, delta):
        MOBAWorld.update(self, delta)
        for point in self.obstacleCoverNodes:
            drawCross(self.background, point, color=(0, 255, 0), size=15, width=4)
            drawCross(self.background, (100, 100), color=(0, 255, 0))


#############################################

class Barker():
    def bark(self):
        pass

    def hearBark(self, thebark):
        pass


############################################

class PlayerHero(Hero, Barker):
    def __init__(self, position, orientation, world, image=AGENT, speed=SPEED, viewangle=360, hitpoints=HEROHITPOINTS,
                 firerate=FIRERATE, bulletclass=BigBullet, dodgerate=DODGERATE, areaeffectrate=AREAEFFECTRATE,
                 areaeffectdamage=AREAEFFECTDAMAGE):
        Hero.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass,
                      dodgerate, areaeffectrate, areaeffectdamage)
    def die(self):
        return None
    # def die(self):
    #     Hero.die(self)
    #     mybase = self.world.getBaseForTeam(self.getTeam())
    #     offset = (mybase.getLocation()[0] - self.getLocation()[0],
    #               mybase.getLocation()[1] - self.getLocation()[1])
    #     self.move(offset)
    #     self.level = 0

    def bark(self):
        Barker.bark(self)
        thebark = None
        ### Set thebark to whatever is the contextually relevant thing (probably a string)
        ### YOUR CODE GOES BELOW HERE ###

        '''
        Rules:
        Automatic: If enemies in range, heros attack, healer hides/heals
                    If pc far away, go to formation
                    If pc health low, healer heals, heros go to

        Barked: If Hero in cover, go to cover

        '''

        ### YOUR CODE GOES ABOVE HERE ###
        for n in self.world.getNPCsForTeam(self.getTeam()):
            if isinstance(n, Barker):
                n.hearBark(thebark)


##############################################
### Healer

class Healer(MOBAAgent, Barker):
    def __init__(self, position, orientation, world, image=GRUNT, speed=SPEED, viewangle=360, hitpoints=HITPOINTS,
                 firerate=FIRERATE, bulletclass=SmallBullet, healrate=HEALRATE):
        MOBAAgent.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate,
                           bulletclass)
        self.healRate = healrate
        self.healTimer = 0
        self.canHeal = True

    def die(self):
        MOBAAgent.die(self)
        self.world.addNPC(self)
        mybase = self.world.getBaseForTeam(self.getTeam())
        offset = (mybase.getLocation()[0] - self.getLocation()[0],
                  mybase.getLocation()[1] - self.getLocation()[1])
        self.move(offset)
        self.start()

    def update(self, delta=0):
        MOBAAgent.update(self, delta)
        if self.canHeal == False:
            self.healTimer = self.healTimer + 1
            if self.healTimer >= self.healRate:
                self.canHeal = True
                self.healTimer = 0

    def heal(self, agent):
        if self.canHeal:
            if isinstance(agent, MOBAAgent) and distance(self.getLocation(),
                                                         agent.getLocation()) < self.getRadius() + agent.getRadius():
                agent.hitpoints = agent.maxHitpoints
                self.canHeal = False

    def areaEffectHeal(self):
        if self.canareaeffect:
            self.canareaeffect = False
            pygame.draw.circle(self.world.background, (0, 0, 255),
                               (int(self.getLocation()[0]), int(self.getLocation()[1])), int(self.getRadius() * 2), 1)
            for x in self.getNPCsForTeam(self.team):
                if distance(self.getLocation(), x.getLocation()) < (self.getRadius() * AREAEFFECTRANGE) + (
                x.getRadius()):
                    x.hitpoints += (self.areaEffectDamage)
            return True
        return False


###################################################
### MyHealer

class MyHealer(Healer, BehaviorTree):
    def __init__(self, position, orientation, world, image=GRUNT, speed=SPEED, viewangle=360, hitpoints=HITPOINTS,
                 firerate=FIRERATE, bulletclass=SmallBullet, healrate=HEALRATE):
        Healer.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass,
                        healrate)
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
        # pause beavhior tree?
        self.stop()
        # only goes to heal the healer if he barks at us
        hero = self.world.agent
        self.navigateTo(hero.getLocation())
        self.heal(hero)
        ### YOUR CODE GOES ABOVE HERE ###


##########################################################

class MyCompanionHero(Hero, BehaviorTree, Barker):
    def __init__(self, position, orientation, world, image=AGENT, speed=SPEED, viewangle=360, hitpoints=HEROHITPOINTS,
                 firerate=FIRERATE, bulletclass=BigBullet, dodgerate=DODGERATE, areaeffectrate=AREAEFFECTRATE,
                 areaeffectdamage=AREAEFFECTDAMAGE):
        Hero.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass,
                      dodgerate, areaeffectrate, areaeffectdamage)
        BehaviorTree.__init__(self)
        self.states = []
        self.startState = None
        self.id = None
        ### YOUR CODE GOES BELOW HERE ###

    def die(self):
        Hero.die(self)
        self.world.addNPC(self)
        mybase = self.world.getBaseForTeam(self.getTeam())
        offset = (mybase.getLocation()[0] - self.getLocation()[0],
                  mybase.getLocation()[1] - self.getLocation()[1])
        self.move(offset)
        self.level = 0
        self.start()


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

    def execute(self, delta=0):
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
    spec = [Selector, [LeftSideDaemon, Formation]]  # , TacticalCover]
    # LANSSIE STUFF
    # spec = [(Selector, 'staring the healer'),
    #             [(HealerDaemon, 'can the healer heal yet'),
    #                 [(Sequence, 'healing team'), (HealClosestTeammate, 'Healing Teammate')]
    #             ],
    #             [(Sequence, 'doing basic movement'), (FindCover, 'finding cover')]
    #         ]
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
        world = self.agent.world

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

    def getHero(self, npc_list):
        hero = None
        for i in npc_list:
            if isinstance(i, PlayerHero):
                return i
        return None

    def enter(self):
        BTNode.enter(self)
        self.timer = 50

        # nodes to navigate to; these are points around the main character
        # ... right now, this is a placeholder...
        #  should be calculated on update for the hero; the id of the
        # heros indexes the nodes list
        hero = self.getHero(self.agent.world.getNPCsForTeam(self.agent.getTeam()))
        nodes = hero.nodes
        orientations = [self.agent.orientation, self.agent.orientation, self.agent.orientation]

        self.formation_node = nodes[self.agent.id]
        self.orientation = orientations[self.agent.id]

        self.agent.turnToAngle(self.orientation)
        self.agent.navigateTo(self.formation_node)
        return None

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)

        # region Formation Variables
        hero = self.getHero(self.agent.world.getNPCsForTeam(self.agent.getTeam()))
        self.formation_node = hero.nodes[self.agent.id]
        self.orientation = hero.orientation
        # endregion

        self.agent.turnToAngle(self.orientation)
        if self.agent.navigator.doneMoving():
            return True
        else:
            # executing
            self.timer = self.timer - 1
            if self.timer <= 0 or distance(self.agent.position, self.formation_node) > 5:
                self.timer = 50
                self.agent.navigateTo(self.formation_node)
            return None
        return ret


# LANSSIE HEALER THINGS
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
        # temporary go to base, but should go to nearest obstacle cover area
        self.agent.navigateTo(self.agent.world.getBaseForTeam(self.agent.getTeam()).getLocation())

    def execute(self):
        ret = BTNode.execute(self, delta)
        # if self.agent.getHitpoints() > self.agent.getMaxHitpoints():
        #     # fail executability conditions
        #     print "exec", self.id, "false"
        #     return False
        # elif self.agent.getHitpoints() == self.agent.getMaxHitpoints():
        #     # Exection succeeds
        #     print "exec", self.id, "true"
        #     print 'IM GOING TO RETREAT'
        #     return True
        # else:
        #     # executing
        #     return None
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

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None or self.target.isAlive() == False:
            # failed execution conditions
            print "exec", self.id, "false"
            return False
        # elif distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE:
        #     # succeeded
        #     print 'IM FINDING TEAM NOW'
        #     print "exec", self.id, "true"
        #     return True
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

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        hero = None
        # Get a reference to the enemy hero
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())

        if self.canHeal:
            return self.getChild(0).execute(delta)
        else:
            # check if timer is < time it takes to get to the player?
            return False
            # Check didn't fail, return child's status
            # return self.getChild(0).execute(delta)
        return ret


###############################
### BEHAVIOR CLASSES FROM IAN:
'''
def treeSpec(agent):
    myid = str(agent.getTeam())
    spec = None
    ### YOUR CODE GOES BELOW HERE ###
    spec=[(DodgeDaemon,'DD'),[(AEDaemon,'AED'),\
                    [(Selector,'Sel1'),\
                        (Retreat,0.3,'Retreat'),\
                        [(HitpointDaemon,0.3,'HPD'),\
                            [(Selector,'Sel2'),\
                                [(BuffDaemon,0,'BD'),[(Sequence,'Seq1'),(ChaseHero,'ChaseHero'),(KillHero,'KillHero')]],\
                            [(HeroPresentDaemon),[(Sequence,'Seq2'),(ChaseMinion,'ChaseM'),(KillMinion,'KillM')]],[(Sequence,'Seq3'),(ChaseHero,'ChaseHero'),(KillHero,'KillHero')]]\
                        ]\
                    ]\
                ]\
            ]\
'''


##################
### Taunt
###
### Print disparaging comment, addressed to a given NPC
### Parameters:
###   0: reference to an NPC
###   1: node ID string (optional)

class Taunt(BTNode):
    ### target: the enemy agent to taunt

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.target = None
        # First argument is the target
        if len(args) > 0:
            self.target = args[0]
        # Second argument is the node ID
        if len(args) > 1:
            self.id = args[1]

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target is not None:
            print "Hey", self.target, "I don't like you!"
        return ret


##################
### MoveToTarget
###
### Move the agent to a given (x, y)
### Parameters:
###   0: a point (x, y)
###   1: node ID string (optional)

class MoveToTarget(BTNode):
    ### target: a point (x, y)

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.target = None
        # First argument is the target
        if len(args) > 0:
            self.target = args[0]
        # Second argument is the node ID
        if len(args) > 1:
            self.id = args[1]

    def enter(self):
        BTNode.enter(self)
        self.agent.navigateTo(self.target)

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None:
            # failed executability conditions
            print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target) < self.agent.getRadius():
            # Execution succeeds
            print "exec", self.id, "true"
            return True
        else:
            # executing
            return None
        return ret


##################
### Retreat
###
### Move the agent back to the base to be healed
### Parameters:
###   0: percentage of hitpoints that must have been lost to retreat
###   1: node ID string (optional)


class Retreat(BTNode):
    ### percentage: Percentage of hitpoints that must have been lost

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.percentage = 0.5
        # First argument is the factor
        if len(args) > 0:
            self.percentage = args[0]
        # Second argument is the node ID
        if len(args) > 1:
            self.id = args[1]

    def enter(self):
        BTNode.enter(self)
        self.agent.navigateTo(self.agent.world.getBaseForTeam(self.agent.getTeam()).getLocation())
        self.timer = 50

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.agent.getHitpoints() > self.agent.getMaxHitpoints() * self.percentage:
            # fail executability conditions
            print "exec", self.id, "false"
            return False
        elif self.agent.getHitpoints() == self.agent.getMaxHitpoints():
            # Exection succeeds
            print "exec", self.id, "true"
            return True
        else:
            # executing
            self.timer -= 1
            if self.timer <= 0:
                self.timer = 50
                self.agent.navigateTo(self.agent.world.getBaseForTeam(self.agent.getTeam()).getLocation())
            return None
        return ret


##################
### ChaseMinion
###
### Find the closest minion and move to intercept it.
### Parameters:
###   0: node ID string (optional)


class ChaseMinion(BTNode):
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
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        if len(enemies) > 0:
            best = None
            dist = 0
            for e in enemies:
                if isinstance(e, Minion):
                    d = distance(self.agent.getLocation(), e.getLocation())
                    if best == None or d < dist:
                        best = e
                        dist = d
            self.target = best
        if self.target is not None:
            navTarget = self.chooseNavigationTarget()
            if navTarget is not None:
                self.agent.navigateTo(navTarget)

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None or self.target.isAlive() == False:
            # failed execution conditions
            print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE - 3:
            # succeeded
            print "exec", self.id, "true"
            return True
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
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        if len(enemies) > 0:
            best = None
            dist = 0
            for e in enemies:
                if isinstance(e, Minion):
                    d = distance(self.agent.getLocation(), e.getLocation())
                    if best == None or d < dist:
                        best = e
                        dist = d
            self.target = best
        if self.target is not None:
            return self.target.getLocation()
        else:
            return None


##################
### KillMinion
###
### Kill the closest minion. Assumes it is already in range.
### Parameters:
###   0: node ID string (optional)


class KillMinion(BTNode):
    ### target: the minion to shoot

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.target = None
        # First argument is the node ID
        if len(args) > 0:
            self.id = args[0]

    def enter(self):
        BTNode.enter(self)
        # self.agent.stopMoving()
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        if len(enemies) > 0:
            best = None
            dist = 0
            for e in enemies:
                if isinstance(e, Minion):
                    d = distance(self.agent.getLocation(), e.getLocation())
                    if best == None or d < dist:
                        best = e
                        dist = d
            self.target = best
            self.old = self.target.getLocation()
            self.destinations = getDestinationsInRadius(self.agent, BIGBULLETRANGE, self.target.getLocation())
            self.dest = getRandomDestination(self.destinations)

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None or distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE:
            # failed executability conditions
            print "exec", self.id, "false"
            return False
        elif self.target.isAlive() == False:
            # succeeded
            print "exec", self.id, "true"
            return True
        else:
            # executing
            for d in self.destinations:
                drawCross(self.agent.world.background, d, (0, 200, 0), 2)
            if (distance(self.agent.getLocation(), self.dest) <= 2.0 * self.agent.getMaxRadius() or rayTraceWorld(
                    self.agent.getLocation(), self.dest, self.agent.world.getLines()) != None) and self.destinations:
                self.dest = getRandomDestination(self.destinations)
            if self.dest:
                drawCross(self.agent.world.background, self.dest, (200, 0, 0), 4, 2)
                self.agent.navigateTo(self.dest)
            if self.agent.canAreaEffect() and distance(self.agent.getLocation(),
                                                       self.target.getLocation()) <= AREAEFFECTRANGE:
                self.agent.areaEffect()
            else:
                self.shootAtTarget()
            return None
        return ret

    def shootAtTarget(self):
        if self.agent is not None and self.target is not None:
            self.agent.turnToFace(self.target.getLocation())
            self.agent.shoot()


##################
### ChaseHero
###
### Move to intercept the enemy Hero.
### Parameters:
###   0: node ID string (optional)

class ChaseHero(BTNode):
    ### target: the hero to chase
    ### timer: how often to replan

    def ParseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.target = None
        self.timer = 50
        # First argument is the node ID
        if len(args) > 0:
            self.id = args[0]

    def enter(self):
        BTNode.enter(self)
        self.timer = 50
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        for e in enemies:
            if isinstance(e, Hero):
                self.target = e
                navTarget = self.chooseNavigationTarget()
                if navTarget is not None:
                    self.agent.navigateTo(navTarget)

                return None

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None or self.target.isAlive() == False:
            # fails executability conditions
            print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE - 3:
            # succeeded
            print "exec", self.id, "true"
            return True
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


##################
### KillHero
###
### Kill the enemy hero. Assumes it is already in range.
### Parameters:
###   0: node ID string (optional)


class KillHero(BTNode):
    ### target: the minion to shoot

    def ParseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.target = None
        # First argument is the node ID
        if len(args) > 0:
            self.id = args[0]

    def enter(self):
        BTNode.enter(self)
        # self.agent.stopMoving()
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        for e in enemies:
            if isinstance(e, Hero):
                self.target = e
                self.destinations = getDestinationsInRadius(self.agent, BIGBULLETRANGE, self.target.getLocation())
                self.dest = getRandomDestination(self.destinations)
                self.old = self.target.getLocation()

                return None

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None or distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE:
            # failed executability conditions
            if self.target == None:
                print "foo none"
            else:
                print "foo dist", distance(self.agent.getLocation(), self.target.getLocation())
            print "exec", self.id, "false"
            return False
        elif self.target.isAlive() == False:
            # succeeded
            print "exec", self.id, "true"
            return True
        else:
            # executing
            for d in self.destinations:
                drawCross(self.agent.world.background, d, (0, 200, 0), 2)
            if self.dest:
                self.agent.navigateTo(self.dest)
            if distance(self.agent.getLocation(), self.dest) <= 2.0 * self.agent.getMaxRadius() and self.destinations:
                self.destinations = getDestinationsInRadius(self.agent, BIGBULLETRANGE, self.target.getLocation())
                self.dest = getRandomDestination(self.destinations)

            if self.agent.canAreaEffect() and distance(self.agent.getLocation(),
                                                       self.target.getLocation()) <= AREAEFFECTRANGE:
                self.agent.areaEffect()
            else:
                self.shootAtTarget()
            return None
        return ret

    def shootAtTarget(self):
        if self.agent is not None and self.target is not None:
            self.agent.turnToFace(self.target.getLocation())
            self.agent.shoot()


##################
### HitpointDaemon
###
### Only execute children if hitpoints are above a certain threshold.
### Parameters:
###   0: percentage of hitpoints that must have been lost to fail the daemon check
###   1: node ID string (optional)


class HitpointDaemon(BTNode):
    ### percentage: percentage of hitpoints that must have been lost to fail the daemon check

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.percentage = 0.5
        # First argument is the factor
        if len(args) > 0:
            self.percentage = args[0]
        # Second argument is the node ID
        if len(args) > 1:
            self.id = args[1]

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.agent.getHitpoints() < self.agent.getMaxHitpoints() * self.percentage:
            # Check failed
            print "exec", self.id, "fail"
            return False
        else:
            # Check didn't fail, return child's status
            return self.getChild(0).execute(delta)
        return ret


##################
### BuffDaemon
###
### Only execute children if agent's level is significantly above enemy hero's level.
### Parameters:
###   0: Number of levels above enemy level necessary to not fail the check
###   1: node ID string (optional)

class BuffDaemon(BTNode):
    ### advantage: Number of levels above enemy level necessary to not fail the check

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.advantage = 0
        # First argument is the advantage
        if len(args) > 0:
            self.advantage = args[0]
        # Second argument is the node ID
        if len(args) > 1:
            self.id = args[1]

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        hero = None
        # Get a reference to the enemy hero
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        for e in enemies:
            if isinstance(e, Hero):
                hero = e
                break
        if hero == None or self.agent.level <= hero.level + self.advantage:
            # fail check
            print "exec", self.id, "fail"
            return False
        else:
            # Check didn't fail, return child's status
            return self.getChild(0).execute(delta)
        return ret


#################################
### MY CUSTOM BEHAVIOR CLASSES

### Effective Dodge Bullets
class DodgeDaemon(BTNode):
    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        # First argument is the node ID
        if len(args) > 0:
            self.id = args[0]

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.agent.canDodge():
            bullets = self.agent.getVisibleType(Bullet)
            for b in bullets:
                if distance(self.agent.getLocation(),
                            b.getLocation()) < self.agent.getMaxRadius() and b.getOwner() != self.agent:
                    destinations = getDestinationsOnRadius(self.agent, 3 * self.agent.getMaxRadius(),
                                                           self.agent.getLocation())
                    if destinations:
                        direction = getRandomDestination(destinations)
                        if direction != None:
                            self.agent.turnToFace(direction)
                            self.agent.dodge(self.agent.orientation)
        return self.getChild(0).execute(delta)


### Effective AE
class AEDaemon(BTNode):
    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        # First argument is the node ID
        if len(args) > 0:
            self.id = args[0]

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.agent.canAreaEffect():
            enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
            enemy = getNearestEnemy(self.agent, enemies)
            if distance(self.agent.getLocation(), enemy.getLocation()) <= AREAEFFECTRANGE + enemy.getRadius():
                self.agent.areaEffect()
        return self.getChild(0).execute(delta)


### Checks for the presence of a Hero
class HeroPresentDaemon(BTNode):
    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        # First argument is the node ID
        if len(args) > 0:
            self.id = args[0]

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        hero = None
        # Get a reference to the enemy hero
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        for e in enemies:
            if isinstance(e, Hero):
                hero = e
                break
        if hero != None and distance(self.agent.getLocation(), hero.getLocation()) < 1.05 * BIGBULLETRANGE:
            # fail check
            print "exec", self.id, "fail"
            return False
        else:
            # Check didn't fail, return child's status
            return self.getChild(0).execute(delta)
        return ret


## Retreat to Healer
class TacticalRetreat(BTNode):
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
        allies = self.agent.world.getNPCsForTeam(self.agent.getTeam())
        if len(allies) > 0:
            for a in allies:
                if isinstance(a, Healer):
                    self.target = a.getLocation()
        if self.target is not None:
            navTarget = self.chooseNavigationTarget()
            if navTarget is not None:
                self.agent.navigateTo(navTarget)

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None or self.target.isAlive() == False:
            # failed execution conditions
            print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target.getLocation()) < self.agent.getMaxRadius():
            # succeeded
            print "exec", self.id, "true"
            return True
        else:
            # executing
            self.timer = self.timer - 1
            if self.timer <= 0:
                self.timer = 50
                self.reset()
            return None
        return ret

    def chooseNavigationTarget(self):
        if self.target is not None:
            return self.target.getLocation()
        else:
            return None


#################################
### MY UTILS

def getNearestEnemy(agent, enemy_minions):
    closest = enemy_minions[0]
    for enemy in enemy_minions:
        if distance(agent.getLocation(), enemy.getLocation()) < distance(agent.getLocation(), closest.getLocation()):
            closest = enemy
    return closest


def getVisibleEnemyType(agent, Class):
    all_Class = agent.getVisibleType(Class)
    enemy_Class = []
    for thing in all_Class:
        if thing.getTeam() != agent.getTeam():
            enemy_Class.append(thing)
    return enemy_Class


def getVisibleTeammates(agent, my_minions):
    my_team = agent.getVisibleType(my_minions)
    teammates = []
    for thing in my_minions:
        if thing.getTeam() == agent.getTeam():
            teammates.append(thing)
    return teammates


def getDestinationsInRadius(agent, radius, target):
    all_destinations = agent.getPossibleDestinations()
    destinations = []
    for dest in all_destinations:
        if distance(dest, target) <= 0.95 * radius and distance(dest, target) >= 0.7 * radius:
            destinations.append(dest)
    return destinations


def getDestinationsOnRadius(agent, radius, target):
    all_destinations = agent.getPossibleDestinations()
    destinations = []
    for dest in all_destinations:
        if distance(dest, target) <= radius and distance(dest, target) >= 0.1 * radius:
            destinations.append(dest)
    return destinations


def getRandomDestination(destinations):
    random_destination = random.choice(destinations)
    return random_destination




