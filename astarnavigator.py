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
from mycreatepathnetwork import *
from mynavigatorhelpers import *


###############################
### AStarNavigator
###
### Creates a path node network and implements the FloydWarshall all-pairs shortest-path algorithm to create a path to the given destination.
            
class AStarNavigator(NavMeshNavigator):

    def __init__(self):
        NavMeshNavigator.__init__(self)
        

    ### Create the pathnode network and pre-compute all shortest paths along the network.
    ### self: the navigator object
    ### world: the world object
    def createPathNetwork(self, world):
        self.pathnodes, self.pathnetwork, self.navmesh = myCreatePathNetwork(world, self.agent)
        return None
        
    ### Finds the shortest path from the source to the destination using A*.
    ### self: the navigator object
    ### source: the place the agent is starting from (i.e., it's current location)
    ### dest: the place the agent is told to go to
    def computePath(self, source, dest):
        ### Make sure the next and dist matricies exist
        if self.agent != None and self.world != None: 
            self.source = source
            self.destination = dest
            ### Step 1: If the agent has a clear path from the source to dest, then go straight there.
            ###   Determine if there are no obstacles between source and destination (hint: cast rays against world.getLines(), check for clearance).
            ###   Tell the agent to move to dest
            ### Step 2: If there is an obstacle, create the path that will move around the obstacles.
            ###   Find the pathnodes closest to source and destination.
            ###   Create the path by traversing the self.next matrix until the pathnode closes to the destination is reached
            ###   Store the path by calling self.setPath()
            ###   Tell the agent to move to the first node in the path (and pop the first node off the path)
            if clearShot(source, dest, self.world.getLines(), self.world.getPoints(), self.agent):
                self.agent.moveToTarget(dest)
            else:
                start = findClosestUnobstructed(source, self.pathnodes, self.world.getLinesWithoutBorders())
                end = findClosestUnobstructed(dest, self.pathnodes, self.world.getLinesWithoutBorders())
                if start != None and end != None:
                    #print len(self.pathnetwork)
                    newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates())
                    #print len(newnetwork)
                    closedlist = []
                    path, closedlist = astar(start, end, newnetwork)
                    if path is not None and len(path) > 0:
                        path = shortcutPath(source, dest, path, self.world, self.agent)
                        self.setPath(path)
                        if self.path is not None and len(self.path) > 0:
                            first = self.path.pop(0)
                            self.agent.moveToTarget(first)
        return None
        
    ### Called when the agent gets to a node in the path.
    ### self: the navigator object
    def checkpoint(self):
        myCheckpoint(self)
        return None

    ### This function gets called by the agent to figure out if some shortcuts can be taken when traversing the path.
    ### This function should update the path and return True if the path was updated.
    def smooth(self):
        return mySmooth(self)

    def update(self, delta):
        myUpdate(self, delta)


def unobstructedNetwork(network, worldLines):
    newnetwork = []
    for l in network:
        hit = rayTraceWorld(l[0], l[1], worldLines)
        if hit == None:
            newnetwork.append(l)
    return newnetwork

def astar(init, goal, network):
    path = []
    openSet = []
    closedSet = []
    cameFrom = {}

    # Get Nodes
    nodes=list(set([node for edge in network for node in edge])) 

    # Initialize Cost Map    
    gScore={}
    fScore={}
    for node in nodes:
        gScore[node]=float('Inf')
        fScore[node]=float('Inf')
    gScore[init]=0
    fScore[init]=0

    # Search
    openSet.append(init)
    while openSet:
        
        minF=float('Inf')
        for node in openSet:
            if fScore[node]<minF:
                current=node
                minF=fScore[node]

        if current==goal:
            path=reconstruct_path(cameFrom,current)
            break

        openSet.remove(current)
        closedSet.append(current)
        neighbours=get_neighbours(current,nodes,network)
        
        for neighbour in neighbours:
            if neighbour in closedSet:
                continue
            tentative_gScore=gScore[current]+mydistance(current, neighbour)
            if neighbour not in openSet:
                openSet.append(neighbour)
            elif tentative_gScore >= gScore[neighbour]:
                continue
            cameFrom[neighbour]=current
            gScore[neighbour]=tentative_gScore
            fScore[neighbour]=gScore[neighbour]+mydistance(neighbour,goal)
    #drawAstarPath(path,)   
    return path[::-1], closedSet

def mydistance(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

#TODO world surface?
def drawAstarPath(path, surface):
	if path is not None:
		for i in range(0,len(path)-1):
			pygame.draw.line(surface, (0, 0, 255), i, i+1, 2)

def reconstruct_path(cameFrom,current):
    fullPath=[current]
    while current in cameFrom.keys():
        current=cameFrom[current]
        fullPath.append(current)
    return fullPath    

def get_neighbours(node,Nodes,network):
    neighbours=[]
    for node2 in Nodes:
        if ((node,node2) in network or (node2,node) in network) and node2 not in neighbours:
            neighbours.append(node2)
    return neighbours

def myUpdate(nav, delta):
    ### YOUR CODE GOES BELOW HERE ###
    if not clearShot(nav.agent.position, nav.agent.getMoveTarget(), nav.world.getLines(), nav.world.getPoints(), nav.agent):
        nav.agent.stopMoving()
        nav.agent.moveToTarget(findClosestUnobstructed(nav.agent.position, nav.pathnodes, nav.world.getLines()))
    ### YOUR CODE GOES ABOVE HERE ###
    return None

def myCheckpoint(nav):
    ### YOUR CODE GOES BELOW HERE ###
    for i in range(0,len(nav.path[:])-1):
        if not clearShot(nav.path[i], nav.path[i+1], nav.world.getLines(), nav.world.getPoints(), nav.agent):
            nav.computePath(nav.agent.position, nav.destination)
            return None
    ### YOUR CODE GOES ABOVE HERE ###
    return None


### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
    ### YOUR CODE GOES BELOW HERE ###
    if p1 and p2:    
        z=[] 
        radius=(2**1/2)*agent.getMaxRadius()
        for point in worldPoints:
            z.append(minimumDistance((p1,p2),point))
        if rayTraceWorld(p1,p2,worldLines)==None and min(z)>radius:
            return True
    ### YOUR CODE GOES ABOVE HERE ###
    return False

