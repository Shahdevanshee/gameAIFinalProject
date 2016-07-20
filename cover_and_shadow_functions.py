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

def CoordinateSystemTransform_Point(point, gui_modifier):
    return (point[0]*gui_modifier[0],point[1]*gui_modifier[1])

def vectorDifference(v1, v2):
    return (v1[0]-v2[0],v1[1]-v2[1])
def vectorAddition(v1, v2):
    return (v1[0]+v2[0],v1[1]+v2[1])

def Polar2Cartesian_transformPoint(point):
    x = point[0]*np.cos(point[1])
    y = point[0]*np.sin(point[1])
    return (x,y)


def Cartesian2Polar_transformPoint(point):
    r = np.sqrt(point[0] ** 2.0 + point[1] ** 2.0)


    if point[0] == 0 and point[1] >= 0:
        return (r,np.deg2rad(90))
    elif point[0] == 0 and point[1] < 0:
        return (r,-np.deg2rad(90))
    else:
        ratio = np.float(point[1])/np.float(point[0])
        theta_prime = np.arctan(ratio)

    x_sign = np.sign(point[0])
    y_sign = np.sign(point[1])

    if (x_sign == -1 and y_sign == -1):
        return (r,np.deg2rad(180) + theta_prime)
    elif (x_sign == -1 and y_sign == 1):
        return (r,np.deg2rad(90) - theta_prime)
    elif (x_sign == 1 and y_sign == -1):
        return (r,-theta_prime)
    return (r, theta_prime)

def Cartesian2Polar_transformPointList(point_list):
    polar_point_list = []
    for point in point_list:
        polar_point_list.append(Cartesian2Polar_transformPoint(point))
    return polar_point_list



def TranslateTo_Point(point,origin):
    return vectorDifference(point,origin)
def TranslateFrom_Point(point,origin):
    return vectorAddition(point,origin)

def TranslateTo_PointList(point_list,origin):
    return [vectorDifference(point,origin) for point in point_list]
def TranslateFrom_PointList(point_list,origin):
    return [vectorAddition(point,origin) for point in point_list]

def CoordinateSystemTransform_PointList(point_list,gui_modifier=(1,1)):
    return [CoordinateSystemTransform_Point(point,gui_modifier) for point in point_list]


def GamePoint_2_RelativePolarCoordinate(point,origin,gui_modifier=(1,-1)):
    # Convert Origin
    o_hat = CoordinateSystemTransform_Point(origin, gui_modifier=(1, -1))
    # Convert Incoming Point
    p_hat = CoordinateSystemTransform_Point(point, gui_modifier=(1, -1))
    # Translate Incoming Point to new Origin
    p_prime = TranslateTo_Point(p_hat, o_hat)
    # Cartesian To Polar
    p_polar = Cartesian2Polar_transformPoint(p_prime)

    return p_polar

def GamePoint_From_RelativePolarCoordinate(p_polar,origin,gui_modifier=(1,-1)):
    # Polar to Cartesian
    p_cartesian = Polar2Cartesian_transformPoint(p_polar)
    # Convert Origin
    o_hat2 = CoordinateSystemTransform_Point(origin, gui_modifier=(1, -1))
    # Translate Point FROM origin
    p_c2 = TranslateFrom_Point(p_cartesian, o_hat2)
    # Convert Point
    p_final = CoordinateSystemTransform_Point(p_c2, gui_modifier=(1, -1))

    return p_final


def GamePointList_To_RelativePolarCoordinates(point_list,origin,gui_modifier=(1,-1)):
    return [GamePoint_2_RelativePolarCoordinate(point,origin,gui_modifier=gui_modifier) for point in point_list]

def GamePointList_From_RelativePolarCoordinates(point_list,origin,gui_modifier=(1,-1)):
    return [GamePoint_From_RelativePolarCoordinate(point,origin,gui_modifier=gui_modifier) for point in point_list]


def ManualObstacle2PolarPoints(manualObstacle,origin = (0,0),gui_modifier=(1,-1)):
    return GamePointList_To_RelativePolarCoordinates(manualObstacle.points,origin,gui_modifier=gui_modifier)
def ShadowParam_pointList(point_list):
    # commented line is faster, but requires extra import
    # max(point_list,key=itemgetter(0))
    all_thetas = [x[1] for x in point_list]
    theta_avg = np.mean(all_thetas)

    pt1_max_theta = max(point_list,key=lambda x: np.abs(x[1]-theta_avg))
    pt2_min_theta = min(point_list,key=lambda x: np.abs(pt1_max_theta[1] - x[1]))
    arrrs = [pt1_max_theta[0],pt2_min_theta[0]]
    rMax = max(arrrs)
    return (rMax,pt1_max_theta[1],pt2_min_theta[1])
def ManualObstacle2ShadowParams(manualObstacle,origin = (0,0),gui_modifier=(1,-1)):
    manualObstacle_polarPoints = ManualObstacle2PolarPoints(manualObstacle,origin=origin,gui_modifier=gui_modifier)
    return ShadowParam_pointList(manualObstacle_polarPoints)
def ShadowParams(item,origin=(0,0),gui_modifier=(1,-1)):
    if isinstance(item,ManualObstacle):
        return ManualObstacle2ShadowParams(item,origin,gui_modifier)




game_origin = (2500.0,700.0)
obstacle_1 = [(1230,1400),(1330,1400),(1330,775),(1230,775)]


# Test 1: Point To polar, from 0,0
# t1 = Cartesian2Polar_transformPoint((1230,1400)) # should be: (1863,0.85) (units,radians)
# print ("Should Be:{0}; Is:{1}".format((1863,0.85),t1))
#
# Test 2: Point List to Polar, from 0,0:
# t1 = Cartesian2Polar_transformPointList(obstacle_1)
# print(t1)


# Test 3: Polar to Cartesian, from 0,0:
# t1 = Cartesian2Polar_transformPoint(obstacle_1[0])
# t2 = Polar2Cartesian_transformPoint(t1)
# print(t2)


### Generate Polar Coordinate

# Convert Origin
o_hat = CoordinateSystemTransform_Point(game_origin,gui_modifier=(1,-1))
# Convert Incoming Point
p_hat = CoordinateSystemTransform_Point(obstacle_1[0],gui_modifier=(1,-1))
# Translate Incoming Point to new Origin
p_prime = TranslateTo_Point(p_hat,o_hat)
# Cartesian To Polar
p_polar = Cartesian2Polar_transformPoint(p_prime)


p_polar2 = GamePoint_2_RelativePolarCoordinate(obstacle_1[0],game_origin)


### Convert Back to Cartesian

# Polar to Cartesian
p_cartesian = Polar2Cartesian_transformPoint(p_polar)
# Convert Origin
o_hat2 = CoordinateSystemTransform_Point(game_origin,gui_modifier=(1,-1))
# Translate Point FROM origin
p_c2 = TranslateFrom_Point(p_cartesian,o_hat2)
# Convert Point
p_final = CoordinateSystemTransform_Point(p_c2,gui_modifier=(1,-1))

p_final2 = GamePoint_From_RelativePolarCoordinate(p_polar2,game_origin,gui_modifier=(1,-1))

x = 1


