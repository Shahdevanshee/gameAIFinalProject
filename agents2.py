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
    #region Old Shadow Stuff
    '''
    def getBaseShadows(self):
        ###################### Our Code Here
        all_bases = self.getBases()
        enemy_base_index = numpy.argmax([base.position[0] for base in all_bases])
        enemy_base = all_bases[enemy_base_index]
        manual_obstacles = self.getObstacles()
        manual_obstacle_shadowParams = [ShadowParams(manual_obstacle, origin=enemy_base.position, gui_modifier=(1, -1))
                                        for manual_obstacle in manual_obstacles]

        self.obstacleShadowParameters = manual_obstacle_shadowParams;
    def getCoverNodes(self):
        ###################### Our Code Here
        all_bases = self.getBases()
        enemy_base_index = numpy.argmax([base.position[0] for base in all_bases])
        enemy_base = all_bases[enemy_base_index]

        cover_nodes = []
        shadow_nodes = []
        for shadow in self.obstacleShadowParameters:
            shadow_nodes.append(GamePoint_From_RelativePolarCoordinate((shadow[0], shadow[1]), enemy_base.position))
            shadow_nodes.append(GamePoint_From_RelativePolarCoordinate((shadow[0], shadow[2]), enemy_base.position))

            avg_theta = (shadow[1] + shadow[2]) / 2
            diff = np.abs(shadow[1] - avg_theta) / 2

            high_theta = avg_theta + diff
            low_theta = avg_theta - diff

            point_counter = 0
            while point_counter < 10:
                r = np.random.randint(shadow[0] + 50, shadow[0] + 100)
                theta_new = (np.random.random() - 0.5) * diff + low_theta

                test_cartesian = GamePoint_From_RelativePolarCoordinate((r, theta_new), enemy_base.position)

                cover_nodes.append(test_cartesian)
                point_counter += 1

        self.obstacleCoverNodes_Randomized = cover_nodes
        self.shadowCartesianParameters = shadow_nodes

    def getShadows(self):
        all_bases = self.getBases()
        enemy_base_index = numpy.argmax([base.position[0] for base in all_bases])
        enemy_base = all_bases[enemy_base_index]

        grid = self.computeFreeLocations_ByRadius(10.0)

        shadow_centroids = []
        # shadows are indexed by shadow centroids
        shadows = {}

        for obstacle_shadow in self.obstacleShadowParameters:
            cover_grid = []

            r_min = obstacle_shadow[0]
            r_max = r_min + 300

            theta_max = obstacle_shadow[1]
            theta_min = obstacle_shadow[2]

            for point in grid:
                polar_point = GamePoint_2_RelativePolarCoordinate(point, enemy_base.position)
                # if polar_point is in obstacle_shadow, and r is within 200, then add it
                # ...to cover_grid
                polar_point_r = polar_point[0]
                polar_point_theta = polar_point[1]

                if polar_point_r <= r_max and polar_point_r > r_min:
                    if polar_point_theta <= theta_max and polar_point_theta >= theta_min:
                        cover_grid.append(point)
            # calculate centroid of cover_grid
            if len(cover_grid) > 0:
                exes, whys = zip(*cover_grid)
                centroid = (np.mean(exes), np.mean(whys))
                shadow_centroids.append(centroid)
                shadows[centroid] = cover_grid
            else:
                centroid = GamePoint_From_RelativePolarCoordinate((r_min + 50, (theta_max + theta_min) / 2.0),
                                                                  enemy_base.position)
                shadow_centroids.append(centroid)
                shadows[centroid] = cover_grid
        self.shadowCentroids = shadow_centroids
        self.shadows = shadows
    '''
    #endregion
    def doKeyDown(self, key):
        MOBAWorld.doKeyDown(self, key)
        if key == K_e:  # 'e'
            if isinstance(self.agent, PlayerHero):
                self.agent.bark()
        return None

    def getStationaryShooterShadowParams(self):
        all_bases = self.getBases()
        enemy_base_index = numpy.argmax([base.position[0] for base in all_bases])
        enemy_base = all_bases[enemy_base_index]

        enemy_towers = self.getTowersForTeam(2)


        self.stationaryShooters = [enemy_base] + enemy_towers
        manual_obstacles = self.getObstacles()

        self.shadowParameters = {}
        for obstacle in manual_obstacles:
            shooter_shadow_params = {}
            for shooter in self.stationaryShooters:
                shooter_shadow_params[shooter] = ShadowParams(obstacle,origin=shooter.position)
            ###
            self.shadowParameters[obstacle] = shooter_shadow_params
    def getShadows_final(self):
        all_bases = self.getBases()
        enemy_base_index = numpy.argmax([base.position[0] for base in all_bases])
        enemy_base = all_bases[enemy_base_index]
        grid = self.computeFreeLocations_ByRadius(10.0)

        shadow_centroids = []
        # shadows are indexed by shadow centroids
        shadows = {}

        obstacles = self.getObstacles()
        #obstacles = [self.getObstacles()[0]]
        for obstacle in obstacles:
            cover_grid = []
            for point in grid:
                valid_cover_point = True

                # could be optimized with a break
                for shooter in self.stationaryShooters:
                    shadow_parameters = self.shadowParameters[obstacle][shooter]

                    r_min = shadow_parameters[0]
                    r_max = r_min + 300
                    theta_max = shadow_parameters[1]
                    theta_min = shadow_parameters[2]

                    polar_point = GamePoint_2_RelativePolarCoordinate(point,shooter.position)
                    polar_point_r = polar_point[0]
                    polar_point_theta = polar_point[1]
                    if not (polar_point_r <= r_max and polar_point_r > r_min and polar_point_theta <= theta_max and polar_point_theta >= theta_min):
                        valid_cover_point = False
                if valid_cover_point:
                    cover_grid.append(point)
            # build cover dictionary
            # calculate centroid of cover_grid
            if len(cover_grid) > 0:
                exes,whys = zip(*cover_grid)
                centroid = (np.mean(exes),np.mean(whys))
                shadow_centroids.append(centroid)
                shadows[centroid] = cover_grid
            else:
                base_shadow_params = self.shadowParameters[obstacle][enemy_base]
                r_min = base_shadow_params[0]
                theta_max = base_shadow_params[1]
                theta_min = base_shadow_params[2]
                centroid = GamePoint_From_RelativePolarCoordinate((r_min + 50,(theta_max + theta_min)/2.0),enemy_base.position)
                shadow_centroids.append(centroid)
                shadows[centroid] = cover_grid
        self.shadowCentroids = shadow_centroids
        self.shadows = shadows

    def update(self, delta):
        MOBAWorld.update(self, delta)
        # for point in self.obstacleCoverNodes:
        #     drawCross(self.background, point, color=(0,0,255),size=6,width=2)
        #for point in self.shadowCartesianParameters:
        #    drawCross(self.background, point, color=(0, 255, 0), size=15, width=4)
        #    drawCross(self.background, (100, 100), color=(0, 255, 0))

        ''' shadow nodes '''
        #if self.useShadows:
        #    for shadow_centroid in self.shadowCentroids:
        #        cover_nodes = self.shadows[shadow_centroid]
                #for node in cover_nodes:
                #    drawCross(self.background,node,color=(75,150,150),size=5,width = 4)


#############################################
def BarkContext_original(Mover,previous_state = None):
    barkState = {}
    healer_values = {}
    minion_1_values = {}
    minion_2_values = {}
    ###########################################################

    # desired values:
    #     - relative distance to [Healer,Minion1,Minion2,Hero]
    #     - distance to nearest cover point
    #     - health [Healer,Minion1,Minion2,Hero]

    team = Mover.getTeam()
    friends = Mover.world.getNPCsForTeam(team)
    hero = None
    for friend in friends:
        if isinstance(friend,PlayerHero):
            hero = friend
    if hero:
        if isinstance(Mover,MyHealer):
            healer_values["playerHealth"] = np.float(hero.getHitpoints())/np.float(hero.getMaxHitpoints())
            healer_values["playerDistance"] = distance(hero.position,Mover.position)
        else:
            healer_values["playerHealth"] = None
            healer_values["playerDistance"] = None
    else:
        healer_values["playerHealth"] = None
        healer_values["playerDistance"] = None

    barkState[0] = healer_values
    barkState[1] = minion_1_values
    barkState[2] = minion_2_values
    ###########################################################
    return barkState
def BarkContext(character, previous_state=None):
    #placeholder: should be deleted
    barkState = {}
    companion_state_toggle = ["formation","attack"]

    #region Populate with defaults if none
    if previous_state == None:
        barkState = {}
        healer_defaults = {}
        healer_defaults["playerHealth"] = None
        healer_defaults["playerDistance"] = None

        companion1_defaults = {}
        companion2_defaults = {}

        companion1_defaults["states"] = ["formation","attack"]
        companion2_defaults["states"] = ["formation","attack"]

        companion1_defaults["currentStateIndex"] = 0
        companion2_defaults["currentStateIndex"] = 0

        companion1_defaults["state"] = companion1_defaults["states"][companion1_defaults["currentStateIndex"]]
        companion2_defaults["state"] = companion2_defaults["states"][companion2_defaults["currentStateIndex"]]


        hero_defaults = {}

        barkState[0] = healer_defaults
        barkState[1] = companion1_defaults
        barkState[2] = companion2_defaults
        barkState[3] = hero_defaults
        return barkState
    #endregion

    # barkState = previous_state.copy()

    #region Update Hero-relevant stuff
    #endregion

    #region Update Healer-relevant stuff
    # below could be streamlined

    barkState = previous_state.copy()

    if isinstance(character, MyHealer):
        team = character.getTeam()
        friends = character.world.getNPCsForTeam(team)
        hero = None
        for friend in friends:
            if isinstance(friend,PlayerHero):
                hero = friend
        if hero:
            barkState[character.id]["playerHealth"] = np.float(hero.getHitpoints())/np.float(hero.getMaxHitpoints())
            barkState[character.id]["playerDistance"] = distance(hero.position,character.position)
    #endregion

    #region Update Companion-relevant stuff
    if isinstance(character,MyCompanionHero):
        current_state_index = barkState[character.id]["currentStateIndex"]
        if current_state_index == 0:
            barkState[character.id]["currentStateIndex"] = 1
        else:
            barkState[character.id]["currentStateIndex"] = 0
        barkState[character.id]["state"] = barkState[character.id]["states"][barkState[character.id]["currentStateIndex"]]
    #endregion
    return barkState

class Barker():
    def __init__(self):
        self.barkState = BarkContext(self)
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
        Hero.die(self)
        mybase = self.world.getBaseForTeam(self.getTeam())
        if mybase is not None:
            offset = (mybase.getLocation()[0] - self.getLocation()[0],
                  mybase.getLocation()[1] - self.getLocation()[1])
            self.move(offset)
            self.level = 0
            self.start()

    def bark(self):
        Barker.bark(self)
        thebark = None
        ### Set thebark to whatever is the contextually relevant thing (probably a string)
        ### YOUR CODE GOES BELOW HERE ###
        thebark = BarkContext(self)
        ### YOUR CODE GOES ABOVE HERE ###
        for n in self.world.getNPCsForTeam(self.getTeam()):
            if isinstance(n, Barker):
                n.hearBark(thebark)


##############################################
### Healer

class Healer(MOBAAgent, Barker):
    def __init__(self, position, orientation, world, image=GRUNT, speed=SPEED, viewangle=360, hitpoints=HITPOINTS,
                 firerate=FIRERATE, bulletclass=SmallBullet, healrate=HEALRATE,dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
        MOBAAgent.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate,
                           bulletclass)
        ### Added timers and such to enable AOE Healing
        self.healRate = healrate
        self.healTimer = 0
        self.canHeal = True
        self.minionTarget = None
        self.minionTargetLocation = None
        self.myHero = None
        self.dodgeRate = dodgerate
        self.dodgeTimer = 0
        self.candodge = True
        self.canareaeffectheal = True
        self.areaEffectRate = areaeffectrate
        self.areaEffectDamage = areaeffectdamage
        self.areaEffectTimer = 0
        self.getHero()


    def die(self):
        MOBAAgent.die(self)
        self.world.addNPC(self)
        mybase = self.world.getBaseForTeam(self.getTeam())
        if mybase is not None:
            offset = (mybase.getLocation()[0] - self.getLocation()[0],
                  mybase.getLocation()[1] - self.getLocation()[1])
            self.move(offset)
            self.start()

    def update(self, delta=0):
        MOBAAgent.update(self, delta)

        #region Healing
        if self.canHeal == False:
            self.healTimer = self.healTimer + 1
            if self.healTimer >= self.healRate:
                self.canHeal = True
                self.healTimer = 0
        # Added the ability to dodge
        if self.candodge == False:
            self.dodgeTimer = self.dodgeTimer + 1
            if self.dodgeTimer >= self.dodgeRate:
                self.candodge = True
                self.dodgeTimer = 0
        # Added the ability to AOE Heal
        if self.canareaeffectheal == False:
            self.areaEffectTimer = self.areaEffectTimer + 1
            if self.areaEffectTimer >= self.areaEffectRate:
                self.canareaeffectheal = True
                self.areaEffectTimer = 0

    def heal(self, agent):
        if self.canHeal:
            if isinstance(agent, MOBAAgent) and distance(self.getLocation(),
                                                         agent.getLocation()) < self.getRadius() + agent.getRadius():
                agent.hitpoints = agent.maxHitpoints
                self.canHeal = False

    def areaEffectHeal(self):
        if self.canareaeffectheal:
            self.canareaeffectheal = False
            pygame.draw.circle(self.world.background, (0, 0, 255),
                               (int(self.getLocation()[0]), int(self.getLocation()[1])), int(self.getRadius() * 2), 1)
            for x in self.world.getNPCsForTeam(self.team):
                if distance(self.getLocation(), x.getLocation()) < (self.getRadius() * AREAEFFECTRANGE) + (
                x.getRadius()):
                    x.hitpoints += (self.areaEffectDamage)
            self.hitpoints+=self.areaEffectDamage
            return True
        return False

    def getHero(self):
        npc_list = self.world.getNPCsForTeam(self.getTeam())
        hero = None
        for npc in npc_list:
            if isinstance(npc, PlayerHero):
                self.myHero = npc
                return None
        return None

    def canDodge(self):
        return self.candodge

    def canAreaEffectHeal(self):
        return self.canareaeffectheal

###################################################
### MyHealer

class MyHealer(Healer, BehaviorTree):
    def __init__(self, position, orientation, world, image=GRUNT, speed=SPEED, viewangle=360, hitpoints=HITPOINTS,
                 firerate=FIRERATE, bulletclass=SmallBullet, healrate=HEALRATE):
        Healer.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass,
                        healrate)
        BehaviorTree.__init__(self)
        self.states = []
        self.speed = (self.speed[0]*4.5,self.speed[1]*4.5)
        self.startState = None
        ### YOUR CODE GOES BELOW HERE ###
        self.team = self.getTeam()

        self.justHeardBark = False
        self.executingBark = False


        self.barkState = BarkContext(self)
        self.executingBark = False
        ### YOUR CODE GOES ABOVE HERE ###
        self.nearestShadow = None



    def update(self, delta):
        Healer.update(self, delta)
        BehaviorTree.update(self, delta)

        #region  Shadow Update--uncomment for shadows
        if self.world.useShadows:
            self.nearestShadow = sorted(self.world.shadowCentroids,key=lambda x: distance(x,self.position))[0]



        #endregion
        # region testing
        # nearest_shadow_grid = self.getNearestShadowGrid()
        # nearest_cover_node_at_destination = self.getNearestCoverNode_AtPosition((100,100))
        # nearest_cover_node = self.getNearestCoverNode()
        # endregion

    def getNearestShadowGrid(self):
        return self.world.shadows[self.nearestShadow]
    def getNearestCoverNode_AtPosition(self,destination):
        relevant_shadow = sorted(self.world.shadowCentroids,key=lambda x: distance(x,self.position))[0]
        shadow_grid = self.world.shadows[relevant_shadow]
        nearest_node = sorted(shadow_grid,key=lambda x:distance(x,destination))[0]
        return nearest_node
    def getNearestCoverNode(self):
        return self.getNearestCoverNode_AtPosition(self.position)
    def start(self):
        # Build the tree
        spec = healerTreeSpec(self)
        if spec is not None and (isinstance(spec, list) or isinstance(spec, tuple)):
            self.buildTree(spec)
            # Start the agent
        Healer.start(self)
        BehaviorTree.start(self)

    def stop(self):
        Healer.stop(self)
        BehaviorTree.stop(self)

    def communicationBark(self,string):
        print string
    def calculateBarkString(self):
        #print "Companion Minion Barking!!!"
        return None

    def bark(self):
        Barker.bark(self)
        self.barkState = BarkContext(self,previous_state=self.barkState)
        ### YOUR CODE GOES BELOW HERE
        self.calculateBarkString()
        ### YOUR CODE GOES ABOVE HERE
    def calculateHeardBarkString(self):
        #print "Companion Minion Heard Bark!!!"
        self.barkState = BarkContext(self,previous_state = self.barkState)
        self.calculateBarkString()
        return None
    def hearBark(self, thebark):
        Barker.hearBark(self, thebark)
        self.barkState = BarkContext(self,previous_state=self.barkState)
        ### YOUR CODE GOES BELOW HERE ###
        self.justHeardBark = True
        self.calculateHeardBarkString()

        #region Below to be handled in behavior tree
        # pause beavhior tree?
        #self.stop()
        # only goes to heal the healer if he barks at us
        #hero = self.world.agent
        #self.navigateTo(hero.getLocation())
        #self.heal(hero)
        #endregion
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
        self.speed = (self.speed[0]*3,self.speed[1]*3)
        self.startState = None
        self.id = None
        self.justHeardBark = False
        self.barkState = BarkContext(self)
        ### YOUR CODE GOES BELOW HERE ###
        self.nearestShadow =None

    def die(self):
        Hero.die(self)
        self.world.addNPC(self)
        mybase = self.world.getBaseForTeam(self.getTeam())
        if mybase is not None:
            offset = (mybase.getLocation()[0] - self.getLocation()[0],
                  mybase.getLocation()[1] - self.getLocation()[1])
            self.move(offset)
            self.level = 0
            self.start()


        ### YOUR CODE GOES ABOVE HERE ###


    def calculateBarkString(self):
        if self.barkState[self.id]["state"] == "formation":
            print "Taking Position!!!"
        if self.barkState[self.id]["state"] == "attack":
            print "Engaging the Enemy!!!"
        return None
    def communicationBark(self,string):
        print string
    def bark(self):
        Barker.bark(self)
        ### YOUR CODE GOES BELOW HERE
        self.barkState = BarkContext(self,previous_state = self.barkState)
        self.calculateBarkString()
        ### YOUR CODE GOES ABOVE HERE

    def calculateHeardBarkString(self):
        print "Companion Minion Heard Bark!!!"
        self.calculateBarkString()
        return None

    def hearBark(self, thebark):
        Barker.hearBark(self, thebark)
        ### YOUR CODE GOES BELOW HERE ###
        self.justHeardBark = True
        self.barkState = BarkContext(self,previous_state = self.barkState)
        self.calculateHeardBarkString()
        ### YOUR CODE GOES ABOVE HERE ###

    def update(self, delta):
        Hero.update(self, delta)
        BehaviorTree.update(self, delta)

        # region  Shadow Update
        if self.world.useShadows:
            self.nearestShadow = sorted(self.world.shadowCentroids, key=lambda x: distance(x, self.position))[0]



        # endregion
        # region testing
        # nearest_shadow_grid = self.getNearestShadowGrid()
        # nearest_cover_node_at_destination = self.getNearestCoverNode_AtPosition((100,100))
        # nearest_cover_node = self.getNearestCoverNode()
        # endregion

    def getNearestShadowGrid(self):
        return self.world.shadows[self.nearestShadow]
    def getNearestCoverNode_AtPosition(self,destination):
        relevant_shadow = sorted(self.world.shadowCentroids,key=lambda x: distance(x,self.position))[0]
        shadow_grid = self.world.shadows[relevant_shadow]
        nearest_node = sorted(shadow_grid,key=lambda x:distance(x,destination))[0]
        return nearest_node
    def getNearestCoverNode(self):
        return self.getNearestCoverNode_AtPosition(self.position)

    def start(self):
        # Build the tree; ONLY USE SPECS, TREES SUCK
        spec = companionTreeSpec(self)
        if spec is not None and (isinstance(spec, list) or isinstance(spec, tuple)):
            self.buildTree(spec)
            # Start the agent
        Hero.start(self)
        BehaviorTree.start(self)

    def stop(self):
        Hero.stop(self)
        BehaviorTree.stop(self)


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
    #TODO This is a place holder spec, we need one that actually heals!
    # spec=[(AEDaemon,'AED'),(Formation)]

    # spec = [Selector, [HealthDaemon, HealCompanion],[LeftSideDaemon, Formation], TacticalCover]
    # spec = [Selector, [LeftSideDaemon, Formation]]  # , TacticalCover]
    
	
	#### Chris: variables ####

	# Lanssie, the variables: (these won't populate during the build tree process, since (I think) the build happens before the game starts.)
    # heard_bark = agent.justHeardBark
    # if heard_bark:
    #     healer_barkContext = agent.barkState[agent.id]
    #     playerHealth = healer_barkContext["playerHealth"]
    #     playerDistance = healer_barkContext["playerDistance"]
    # # and to reset the bark state
    # agent.justHeardBark = False

    ##########################


	# LANSSIE STUFF
    spec = [(Selector, 'starting the healer'),
                [(HealerBarkDaemon,'heard bark order'), #dogde
                    [(Sequence, 'finding and healing hero sequence'), (FindTeammate, agent.myHero, 'finding hero'), (HealTeammate, agent.myHero, 'Healing Hero')]
                ],
                [(HealTeammateDaemon, 'regular healing'), #dodge
                    [(Sequence, 'finding and healing teammate sequence'),(FindTeammate, agent.minionTarget, 'finding hero'), (HealTeammate, agent.minionTarget, 'Healing Hero')],
                ],
                (Formation, 'doing regular formation')
            ]
    ### YOUR CODE GOES ABOVE HERE ###
    return spec

def companionTreeSpec(agent):
    myid = str(agent.getTeam())
    spec = None
    ### YOUR CODE GOES BELOW HERE ###
    spec=[(Selector),\
            [(CompanionFormationDaemon),\
                    [(AEDaemon,'AED'),(Formation)\
                    ]\
            ],\
            [(CompanionAttackDaemon),\
                [(DodgeDaemon,'DD'),[(AEDaemon,'AED'),\
                            [(Selector,'Sel1'),\
                                [(Selector,'Sel4'),(RetreatToHealer,0.3,'Retreat'),(Retreat,0.3,'Retreat')\
                                ],\
                                [(HitpointDaemon,0.3,'HPD'),\
                                    [(Sequence,'Seq1'),(ChaseEnemy,'ChaseEnemy'),(KillEnemy,'KillEnemy')\
                                    ],\
                                ]\
                            ]\
                ]\
            ]\
        ]]\
    ### YOUR CODE GOES ABOVE HERE ###
    return spec


### Helper function for making BTNodes (and sub-classes of BTNodes).
### type: class type (BTNode or a sub-class)
### agent: reference to the agent to be controlled
### This function takes any number of additional arguments that will be passed to the BTNode and parsed using BTNode.parseArgs()
def makeNode(type, agent, *args):
    node = type(agent, args)
    return node


##########################################################
### YOUR STATES AND BEHAVIORS GO HERE
class CompanionFormationDaemon(BTNode):
    def parseArgs(self,args):
        BTNode.parseArgs(self,args)
    def execute(self,delta=0):
        ret = BTNode.execute(self,delta)

        condition = self.agent.barkState[self.agent.id]["state"] == "formation"
        if condition:
            return self.getChild(0).execute(delta)
        else:
            return False


        # Any idea why the original daemons were structured this way?
        # Are we breaking anything by not reaching this line?
        return ret


class CompanionAttackDaemon(BTNode):
    def parseArgs(self, args):
        BTNode.parseArgs(self, args)

    def execute(self, delta=0):
        ret = BTNode.execute(self,delta)

        condition = self.agent.barkState[self.agent.id]["state"] == "attack"
        if condition:
            return self.getChild(0).execute(delta)
        else:
            return False

        # Any idea why the original daemons were structured this way?
        # Are we breaking anything by not reaching this line?
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
        world = self.agent.world

        # currently, no logic implemented
        return self.getChild(0).execute(delta)


        # Any idea why the original daemons were structured this way?
        # Are we breaking anything by not reaching this line?
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
            shootEnRoute(self.agent)
            AOEEnRoute(self.agent)
            return None
        return ret


# LANSSIE HEALER THINGS
# FINDING COVER AS THE DEFAULT STATE OF BEING FOR HEALERS AND POSSIBLY OTHER MINIONS?

# DAEMONS GALORE

class HealerBarkDaemon(BTNode):

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.target = None
        self.timer = 50
        # First argument is the factor
        if len(args) > 0:
        #     self.playerHealth = args[0]
        # # Second argument is the node ID
        # if len(args) > 1:
        #     self.healerDistanceToPlayer = args[1]
        # if len(args) > 2:
        #     self.bark = args[2]
        # if len(args) > 3:
            self.id = args[0]        

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)

        # if self.playerHealth < .5 * HEROHITPOINTS and self.healerDistanceToPlayer < 150 and self.bark == True:
        #     return self.getChild(0).execute(delta)
        # else:
        #     return False
        # return ret


        #### Chris Add on For Bark "Logic"
        if self.agent.justHeardBark == True or self.agent.executingBark == True:
            self.agent.justHeardBark = False
            
            player_health = self.agent.barkState[self.id]["playerHealth"]
            player_distance = self.agent.barkState[self.id]["playerDistance"]
            if player_health < .5 * HEROHITPOINTS and player_distance < 150: 
                self.agent.executingBark = True
                return self.getChild(0).execute(delta)
            else: 
                self.agent.executingBark = False
                return False
        else:
            # Double check this logic.  Not sure it will work as expected
            self.agent.executingBark = False
            self.agent.justHeardBark = False
            return False
        return ret
        ####


class HealTeammateDaemon(BTNode):
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
        team = self.agent.world.getNPCsForTeam(self.agent.getTeam())
        #print team 

        to_heal = None
        distance_away = {} #key = teammate, value = distance

        for teammate in team:
            if teammate != self.agent and teammate != self.agent.myHero:
                distance_away[teammate] = distance(teammate.getLocation(), self.agent.getLocation())
        #print distance_away
        min_to_heal = min(distance_away, key=distance_away.get)
        #print to_heal
        min_dist = min(distance_away)

        if min_to_heal != None and min_to_heal.isAlive() and min_dist < 150 and min_to_heal.getHitpoints() < .5*min_to_heal.getMaxHitpoints():
            self.agent.minionTarget = min_to_heal
            self.agent.minionTargetLocation = min_to_heal.getLocation()
            return self.getChild(0).execute(delta)
        else:
            return False
        return ret

class HealTeammate(BTNode):
    ### target: the minion to chase
    ### timer: how often to replan

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.timer = 50
        # First argument is the node ID
        if len(args) > 0:
            self.target = args[0]
        if len(args) > 1:
            self.id = args[1]

    def enter(self):
        return None

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None or self.target.isAlive() == False:
            # failed execution conditions
            #print "exec", self.id, "false"
            return False
        else:
            self.agent.heal(self.target)
            # return True
        return ret



##################
### FINDTEAMMATE
###
### Find the closest minion and move to intercept it.
### Parameters:
###   0: node ID string (optional)


class FindTeammate(BTNode):
    ### target: the minion to chase
    ### timer: how often to replan

    def parseArgs(self, args):
        BTNode.parseArgs(self, args)
        self.target = None
        self.timer = 50
        # First argument is the node ID
        if len(args) > 0:
            self.hero = args[0]
        if len(args) > 1:
            self.id = args[1]

    def enter(self):
        BTNode.enter(self)
        self.timer = 50
        
        if self.hero != self.agent.minionTarget: #should expect a hero if from other branch. should expect minion if passed through the daemon successfully.
            self.target = self.hero
        else:
            self.target = self.agent.minionTarget
        if self.target is not None:
            navTarget = self.chooseNavigationTarget()
            if navTarget is not None:
                self.agent.navigateTo(navTarget)

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None or self.target.isAlive() == False:
            # failed execution conditions
            #print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target.getLocation()) < 1:
            # succeeded
            #print "exec", self.id, "true"
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

###############################
### BEHAVIOR CLASSES FROM IAN:
'''
def treeSpec(agent):
    myid = str(agent.getTeam())
    spec = None
    ### YOUR CODE GOES BELOW HERE ###
    spec=[(DodgeDaemon,'DD'),[(AEDaemon,'AED'),\
                    [(Selector,'Sel1'),\
                        [(Selector,'Sel4'),(RetreatToHealer,0.3,'Retreat'),(RetreatToHealer,0.3,'Retreat')],\
                        [(HitpointDaemon,0.3,'HPD'),\
                            [(Selector,'Sel2'),\
                                [(Sequence,'Seq1'),(ChaseHero,'ChaseHero'),(KillHero,'KillHero')],\
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
            print "Hey", self.target, "Fuck Off!"
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
            #print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target) < self.agent.getRadius():
            # Execution succeeds
            #print "exec", self.id, "true"
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
            #print "exec", self.id, "false"
            return False
        elif self.agent.getHitpoints() == self.agent.getMaxHitpoints():
            # Exection succeeds
            #print "exec", self.id, "true"
            return True
        else:
            # executing
            self.timer -= 1
            if self.timer <= 0:
                self.timer = 50
                self.agent.navigateTo(self.agent.world.getBaseForTeam(self.agent.getTeam()).getLocation())
            shootEnRoute(self.agent)
            AOEEnRoute(self.agent)
            return None
        return ret


##################
### ChaseEnemy

class ChaseEnemy(BTNode):

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
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())+self.agent.world.getEnemyTowers(self.agent.getTeam())+self.agent.world.getEnemyBases(self.agent.getTeam())
        if len(enemies) > 0:
            best = None
            dist = float('Inf')
            for e in enemies:
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
            #print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE - 3:
            # succeeded
            #print "exec", self.id, "true"
            return True
        else:
            # executing
            self.timer = self.timer - 1
            if self.timer <= 0:
                self.timer = 50
                navTarget = self.chooseNavigationTarget()
                if navTarget is not None:
                    self.agent.navigateTo(navTarget)
            shootEnRoute(self.agent)
            AOEEnRoute(self.agent)
            return None
        return ret

    def chooseNavigationTarget(self):
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())+self.agent.world.getEnemyTowers(self.agent.getTeam())+self.agent.world.getEnemyBases(self.agent.getTeam())
        if len(enemies) > 0:
            best = None
            dist = float('Inf')
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
### KillEnemy
###
### Kill the closest enemy


class KillEnemy(BTNode):
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
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())+self.agent.world.getEnemyTowers(self.agent.getTeam())+self.agent.world.getEnemyBases(self.agent.getTeam())
        if len(enemies) > 0:
            best = None
            dist = float('Inf')
            for e in enemies:
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
            #print "exec", self.id, "false"
            return False
        elif self.target.isAlive() == False:
            # succeeded
            #print "exec", self.id, "true"
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
            #print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE - 3:
            # succeeded
            #print "exec", self.id, "true"
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
            #print "exec", self.id, "false"
            return False
        elif self.target.isAlive() == False:
            # succeeded
            #print "exec", self.id, "true"
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
            #print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE - 3:
            # succeeded
            #print "exec", self.id, "true"
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
            #print "exec", self.id, "false"
            return False
        elif self.target.isAlive() == False:
            # succeeded
            #print "exec", self.id, "true"
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


#####################
### Towers

class ChaseTower(BTNode):
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
        enemies = self.agent.world.getEnemyTowers(self.agent.getTeam())
        dist=float('Inf')
        for e in enemies:
            if dist < distance(self.agent.getLocation(),e.getLocation()):
                closest=e
                dist=distance(self.agent.getLocation(),e.getLocation())    
        self.target = closest
        navTarget = self.chooseNavigationTarget()
        if navTarget is not None:
            self.agent.navigateTo(navTarget)
        return None

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None or self.target.isAlive() == False:
            # fails executability conditions
            #print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE - 3:
            # succeeded
            #print "exec", self.id, "true"
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
### KillTower


class KillTower(BTNode):
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
        enemies = self.agent.world.getEnemyTowers(self.agent.getTeam())
        dist=float('Inf')
        for e in enemies:
            if dist < distance(self.agent.getLocation(),e.getLocation()):
                closest=e
                dist=distance(self.agent.getLocation(),e.getLocation())    
        self.target = closest
        self.destinations = getDestinationsInRadius(self.agent, BIGBULLETRANGE, self.target.getLocation())
        self.dest = getRandomDestination(self.destinations)
        self.old = self.target.getLocation()
        return None

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None or distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE:
            # failed executability conditions
            #print "exec", self.id, "false"
            return False
        elif self.target.isAlive() == False:
            # succeeded
            #print "exec", self.id, "true"
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
            #print "exec", self.id, "fail"
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
            #print "exec", self.id, "fail"
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
        if isinstance(self,Hero):
            if self.agent.canAreaEffect():
                enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())+self.agent.world.getEnemyTowers(self.agent.getTeam())+self.agent.world.getEnemyBases(self.agent.getTeam())
                enemy = getNearestEnemy(self.agent, enemies)
                if distance(self.agent.getLocation(), enemy.getLocation()) <= AREAEFFECTRANGE + enemy.getRadius():
                    self.agent.areaEffect()
        elif isinstance(self,Healer):
            if self.agent.canAreaEffectHeal():
                allies = self.agent.world.getNPCsForTeam(self.agent.getTeam())
                ally = getNearestEnemy(self.agent, allies)
                if distance(self.agent.getLocation(), ally.getLocation()) <= AREAEFFECTRANGE + ally.getRadius():
                    self.agent.areaEffectHeal()
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
            #print "exec", self.id, "fail"
            return False
        else:
            # Check didn't fail, return child's status
            return self.getChild(0).execute(delta)
        return ret


## Retreat to Healer
class RetreatToHealer(BTNode):

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
        self.timer = 50
        allies = self.agent.world.getNPCsForTeam(self.agent.getTeam())
        if len(allies) > 0:
            for a in allies:
                if isinstance(a, Healer):
                    self.target = a
        if self.target is not None:
            navTarget = self.chooseNavigationTarget()
            if navTarget is not None:
                self.agent.navigateTo(navTarget)

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.agent.getHitpoints() > self.agent.getMaxHitpoints() * self.percentage:
            # fail executability conditions
            #print "exec", self.id, "false"
            return False
        elif self.target == None or self.target.isAlive() == False:
            # failed execution conditions
            #print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target.getLocation()) < self.agent.getMaxRadius() and self.agent.hitpoints==self.agent.getMaxHitpoints:
            # succeeded
            #print "exec", self.id, "true"
            return True
        else:
            # executing
            self.timer = self.timer - 1
            if self.timer <= 0:
                self.timer = 50
                self.reset()
            shootEnRoute(self.agent)
            AOEEnRoute(self.agent)
            return None
        return ret

    def chooseNavigationTarget(self):
        if self.target is not None:
            return self.target.getLocation()
        else:
            return None

## Retreat to Player
class RetreatToPlayer(BTNode):
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
                if isinstance(a, PlayerHero):
                    self.target = a.getLocation()
        if self.target is not None:
            navTarget = self.chooseNavigationTarget()
            if navTarget is not None:
                self.agent.navigateTo(navTarget)

    def execute(self, delta=0):
        ret = BTNode.execute(self, delta)
        if self.target == None or self.target.isAlive() == False:
            # failed execution conditions
            #print "exec", self.id, "false"
            return False
        elif distance(self.agent.getLocation(), self.target.getLocation()) < self.agent.getMaxRadius():
            # succeeded
            #print "exec", self.id, "true"
            return True
        else:
            # executing
            self.timer = self.timer - 1
            if self.timer <= 0:
                self.timer = 50
                self.reset()
            shootEnRoute(self.agent)
            AOEEnRoute(self.agent)

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
    if enemy_minions:
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

def shootEnRoute(agent):
    enemies = agent.world.getEnemyNPCs(agent.getTeam())+agent.world.getEnemyTowers(agent.getTeam())+agent.world.getEnemyBases(agent.getTeam())
    closest=[]
    if len(enemies) > 0:
        for e in enemies:
            if distance(agent.getLocation(), e.getLocation()) < BIGBULLETRANGE:
                closest.append(e)
        dist=float('Inf')
        target=None
        for e in closest:
            d = distance(agent.getLocation(), e.getLocation())
            if d<dist:
                dist=d
                target=e
        if target:
            shootAtTarget_function(agent, target)
            #agent.turnToFace(target.getLocation())
            #agent.shoot()

def AOEEnRoute(agent):
    if isinstance(agent,Hero):
        if agent.canAreaEffect():
            enemies = agent.world.getEnemyNPCs(agent.getTeam())+agent.world.getEnemyTowers(agent.getTeam())+agent.world.getEnemyBases(agent.getTeam())
            if enemies:
                enemy = getNearestEnemy(agent, enemies)
                if distance(agent.getLocation(), enemy.getLocation()) <= AREAEFFECTRANGE + enemy.getRadius():
                    agent.areaEffect()
    elif isinstance(agent,Healer):
        if agent.canAreaEffectHeal():
            allies = agent.world.getNPCsForTeam(agent.getTeam())
            if allies:
                ally = getNearestEnemy(agent, allies)
                if distance(agent.getLocation(), ally.getLocation()) <= AREAEFFECTRANGE + ally.getRadius():
                    agent.areaEffectHeal()



# Leading Shot Functions
def normalize(line):
    dx = line[1][0] - line[0][0]
    dy = line[1][1] - line[0][1]
    mag = (dx**2.0 + dy**2.0)**0.5
    if mag == 0.0:
        return (0.,0.)
    return (dx/mag,dy/mag)
def turnToFace_TurnAngle(agent, pos):
    direction = (pos[0] - agent.getLocation()[0], pos[1] - agent.getLocation()[1])
    angle = math.degrees(numpy.arctan2(direction[0],direction[1]))-90
    return angle

def cross_product(a,b):
    i = a[1]*b[2]
    j = a[2]*b[0]
    k = a[0]*b[1]
    return (i,j,k)

def polarity(vector_to_agent,normalizedDirection):
    polarity_primitive = vector_to_agent[0] * normalizedDirection[1] - vector_to_agent[1] * normalizedDirection[0]
    if polarity_primitive >= 0:
        return 1.0
    else:
        return -1.0
def leading_shot_angle(agent,target):
    if not isinstance(target,Tower) and not isinstance(target,Base):
        if not target.isMoving():
            return False,0.
    else:
        return False,0.
    # this is going to happen anyway
    agent.turnToFace(target.position)

    target_position = target.position
    target_destination = target.moveTarget
    target_speed = target.speed
    normalizedDirection = normalize((target_position,target_destination))

    agent_position = agent.position
    vector_to_agent = normalize((target_position,agent_position))

    if normalizedDirection and vector_to_agent:
        if isinstance(normalizedDirection[0],numpy.float) and isinstance(normalizedDirection[1],numpy.float) and isinstance(vector_to_agent[0],numpy.float) and isinstance(vector_to_agent[1],numpy.float):
            dp = dotProduct(normalizedDirection,vector_to_agent)
        else:
            dp = 0.
    else:
        dp = 0.
    phi = math.acos(dp)


    bullet_speed = BIGBULLETSPEED
    theta_prime = math.degrees(math.asin((float(target_speed[0])/float(bullet_speed[0]))*math.sin(phi)))
    #print ("normalizedDirection:{0} vector_to_agent:{1}".format(normalizedDirection,vector_to_agent))
    theta = polarity(vector_to_agent,normalizedDirection)*theta_prime
    total_angle = agent.orientation + theta
    #o if total_angle > 360:
    # 	return True,total_angle - 360
    # elif total_angle < 0:
    # 	return True,total_angle + 360
    # else:
    # 	return True,total_angle
    return True,total_angle

def shootAtTarget_function(agent,target):
    if agent is not None and target is not None:
        takeLeadingShot, turn_angle = leading_shot_angle(agent, target)
        if takeLeadingShot:
            agent.turnToAngle(turn_angle)
        # self.agent.turnToAngle(turn_angle)
        else:
            agent.turnToFace(target.getLocation())
        agent.shoot()
