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
import astarnavigator

### This function optimizes the given path and returns a new path
### source: the current position of the agent
### dest: the desired destination of the agent
### path: the path previously computed by the Floyd-Warshall algorithm
### world: pointer to the world
def shortcutPath(source, dest, path, world, agent):
    ### YOUR CODE GOES BELOW HERE ###
    edges=[]
    newpath=[source]+path+[dest]
    for node1 in newpath:
        for node2 in newpath:
            if node1!=node2 and ClearShot(node1, node2, world.getLines(), world.getPoints(), agent) and (node1,node2) not in edges and (node2,node1) not in edges:
                edges.append((node1,node2))
    Apath,closedset=astarnavigator.astar(newpath[0], newpath[-1], edges)
    ### YOUR CODE GOES BELOW HERE ###
    return Apath
    #next,dist=APSP(newpath,edges)
    #return findPath(newpath[0],newpath[-1],next)

def findPath(start, end, next):
    path = []
    if next[start][end]==None:
        return path
    path=[start]
    while start!=end:
        start=next[start][end]
        path.append(start)
    return path

def APSP(nodes, edges):
    dist = {}
    next = {}
    for n in nodes:
        next[n] = {}
        dist[n] = {}
    for node1 in nodes:
        for node2 in nodes:
            next[node1][node2]=None
            dist[node1][node2]=float('Inf')    
    for node in nodes:
        next[node][node]=node
        dist[node][node]=0
    for edge in edges:
        dist[edge[0]][edge[1]]=distance(edge[0],edge[1])
        next[edge[0]][edge[1]]=edge[1]
        dist[edge[1]][edge[0]]=distance(edge[1],edge[0])
        next[edge[1]][edge[0]]=edge[0]
    for node1 in nodes:
        for node2 in nodes:
            for node3 in nodes:
                if dist[node2][node3]>(dist[node2][node1]+dist[node1][node3]):
                    dist[node2][node3]=(dist[node2][node1]+dist[node1][node3])
                    next[node2][node3]=next[node2][node1]
    return next, dist

           
### This function changes the move target of the agent if there is an opportunity to walk a shorter path.
### This function should call nav.agent.moveToTarget() if an opportunity exists and may also need to modify nav.path.
### nav: the navigator object
### This function returns True if the moveTarget and/or path is modified and False otherwise
def mySmooth(nav):
    
    ### YOUR CODE GOES BELOW HERE ###
    if nav.agent.position and nav.destination and ClearShot(nav.agent.position, nav.destination, nav.world.getLines(), nav.world.getPoints(), nav.agent)==True:
        if not nav.agent.moveToTarget(nav.destination):
            #nav.agent.stopMoving()
            pass
        else:
            nav.agent.moveToTarget(nav.destination)
        return True
    ### YOUR CODE GOES ABOVE HERE ###
    
    return False

def ClearShot(p1, p2, worldLines, worldPoints, agent):

    ### YOUR CODE GOES BELOW HERE ###
    z=[] 
    radius=1.1*agent.getMaxRadius()
    for point in worldPoints:
        z.append(minimumDistance((p1,p2),point))
    if rayTraceWorld(p1,p2,worldLines)==None and min(z)>radius:
        return True
    ### YOUR CODE GOES ABOVE HERE ###
    return False
