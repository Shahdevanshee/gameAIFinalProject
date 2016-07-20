import numpy as np
#from operator import itemgetter
import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *

from constants import *
from utils import *
from core import *
from agents import *
from moba4 import *
from behaviortree import *
from cover_and_shadow_functions import *


import sys, pygame, math, random, time, copy
from pygame.locals import *

from constants import *
from utils import *
from core import *
from agents import *
from moba4 import *
from behaviortree import *
from cover_and_shadow_functions import *


def vectorDifference(v1, v2):
    return (v1[0]-v2[0],v1[1]-v2[1])
def vectorAddition(v1, v2):
    return (v1[0]+v2[0],v1[1]+v2[1])
def Polar2Cartesian_transformPoint(point,origin=(0,0),gui_modifier=(1,1)):
    origin = list(origin)

    x = point[0]*np.cos(point[1])*gui_modifier[0]
    y = point[0]*np.sin(point[1])*gui_modifier[1]

    return vectorAddition((x,y),origin)


def Cartesian2Polar_transformPoint(point):
    r = np.sqrt(point[0] ** 2.0 + point[1] ** 2.0)

    if point[1] == 0 and point[0] == 0:
        return (r,0)
    elif point[1] == 0 and point[0] > 0:
        return (r,0)
    elif point[1] == 0 and point[0] < 0:
        return (r,np.deg2rad(180))
    else:
        theta = np.arctan((point[0] / point[1]))
    return (r, theta)

def Cartesian2Polar_transformPointList(point_list):
    polar_point_list = []
    for point in point_list:
        polar_point_list.append(Cartesian2Polar_transformPoint(point))
    return polar_point_list

def ManualObstacle2PolarPoints(manualObstacle,origin = (0,0),gui_modifier=(1,1)):
    origin = list(origin)
    origin[0] *= gui_modifier[0]
    origin[1] *= gui_modifier[1]

    mo_cartesian_points = [vectorDifference(point, origin) for point in manualObstacle.points]
    return Cartesian2Polar_transformPointList(mo_cartesian_points)

def ShadowParam_pointList(point_list):
    # commented line is faster, but requires extra import
    # max(point_list,key=itemgetter(0))

    pt1_max_theta = max(point_list,key=lambda x: x[1])
    pt2_min_theta = min(point_list,key=lambda x: x[1])

    arrrs = [pt1_max_theta[0],pt2_min_theta[0]]
    rMax = max(arrrs)

    return (rMax,pt1_max_theta[1],pt2_min_theta[1])
def ManualObstacle2ShadowParams(manualObstacle,origin = (0,0),gui_modifier=(1,1)):
    manualObstacle_polarPoints = ManualObstacle2PolarPoints(manualObstacle,origin=(0,0),gui_modifier=(1,-1))
    return ShadowParam_pointList(manualObstacle_polarPoints)

def ShadowParams(item,origin=(0,0),gui_modifier=(1,-1)):
    if isinstance(item,ManualObstacle):
        return ManualObstacle2ShadowParams(item,origin,gui_modifier)