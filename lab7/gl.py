import numpy as np
from math import isclose, floor, ceil, pi, tan, atan2, acos
from camera import Camera

import pygame
import random

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = self.screen.get_rect()

        self.camera = Camera()
        self.glViewport(0, 0, self.width, self.height)
        self.glProjection()

        self.glColor(1, 1, 1)
        self.glClearColor(0, 0, 0)

        self.glClear()

        self.scene = []
        self.lights = []

        self.envMap = None

        self.maxRecursionDepth = 3

    
    def glViewport(self, x, y, width, height):
        self.vpX = round(x)
        self.vpY = round(y)
        self.vpWidth = width
        self.vpHeight = height

        self.viewportMatrix = np.matrix([[width/2, 0, 0,x + width/2],
                                         [0, height/2, 0, y + height/2],
                                         [0, 0, 0.5, 0.5],
                                         [0, 0, 0, 1]])
    
    def glProjection(self, n = 0.1, f = 1000, fov = 60):
        aspectRatio = self.vpWidth / self.vpHeight
        fov *= pi/180
        self.topEdge = tan(fov/2)*n
        self.rightEdge = self.topEdge * aspectRatio

        self.nearPlane = n

        self.projectionMatrix = np.matrix([[n/self.rightEdge, 0, 0, 0],
                                           [0, n/self.topEdge, 0, 0],
                                           [0, 0, -(f+n)/(f-n), -(2*f*n)/(f-n)],
                                           [0, 0, -1, 0]])
    
    def glClearColor(self, r, g, b):
        # 0 - 1
        r = min(1, max(0,r))
        g = min(1, max(0,g))
        b = min(1, max(0,b))

        self.clearColor = [r,g,b]
    
    def glColor(self, r, g, b):
        # 0 - 1
        r = min(1, max(0,r))
        g = min(1, max(0,g))
        b = min(1, max(0,b))
        
        self.currColor = [r,g,b]

    def glEnvMapColor(self, orig, dir):
        if self.envMap:
            x = atan2(dir[2], dir[0])/(2 * pi) + 0.5
            y = acos(-dir[1])/pi

            return self.envMap.getColor(x, y)

        return self.clearColor
    
    def glClear(self):
        color = [int(i * 255) for i in self.clearColor]
        self.screen.fill(color)
        
        self.frameBuffer = [[color for y in range(self.height)]
							for x in range(self.width)]
    
    def glPoint(self, x, y, color = None):
        # Pygame empieza a renderizar desde la esquina
		# superior izquierda, hay que voltear la Y

        x = round(x)
        y = round(y)
        
        if (0 <= x < self.width) and (0 <= y < self.height):
            color = [int(i * 255) for i in (color or self.currColor) ]

            self.screen.set_at((x,self.height - 1 - y ), color)

            self.frameBuffer[x][y] = color
    
    def glLine(self, p0, p1, color = None):
        		# Algoritmo de Lineas de Bresenham
		# y = mx + b

        x0 = p0[0]
        x1 = p1[0]
        y0 = p0[1]
        y1 = p1[1]

		# Si el punto 0 es igual que el punto 1, solamente dibujar un punto
        if x0 == x1 and y0 == y1:
            self.glPoint(x0, y0)
            return

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        
        steep = dy > dx
        
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        limit = 0.75
        m = dy / dx
        y = y0

        for x in range(round(x0), round(x1) + 1):
            if steep:
                self.glPoint(y, x, color or self.currColor)
            else:
                self.glPoint(x, y, color or self.currColor)

            offset += m
            
            if offset >= limit:
                if y0 < y1:
                    y += 1
                else:
                    y -= 1

                limit += 1
    
    def glRender(self):

        indeces = [(i, j) for i in range(self.vpWidth) for j in range(self.vpHeight)]
        random.shuffle(indeces)

        for i, j in indeces:
            x = i + self.vpX
            y = j + self.vpY

            if 0 <= x < self.width and 0 <= y < self.height:

                pX = ((x + 0.5 - self.vpX) / self.vpWidth) * 2 - 1
                pY = ((y + 0.5 - self.vpY) / self.vpHeight) * 2 - 1 

                pX *= self.rightEdge
                pY *= self.topEdge
                pZ = -self.nearPlane

                dir = [pX, pY, pZ]
                dir /= np.linalg.norm(dir)

                hit = self.glCastRay(self.camera.translation, dir)

                color = [0,0,0]

                if hit != None:
                    if hit.obj.material:
                        color = hit.obj.material.GetSurfaceColor(hit, self)
                else:
                    color = self.glEnvMapColor(self.camera.translation, dir)

                self.glPoint(x, y, color)
                pygame.display.flip()

    def glCastRay(self, origin, direction, sceneObj = None, recursion = 0):

        if recursion > self.maxRecursionDepth:
            return None

        depht = float('inf')
        intercept = None
        hit = None

        for obj in self.scene:
            if obj != sceneObj:
                intercept =  obj.ray_intersect(origin, direction)

                if intercept != None:
                    if intercept.distance < depht:
                        hit = intercept
                        depht = intercept.distance
        return hit