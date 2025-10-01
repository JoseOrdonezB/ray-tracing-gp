import pygame
from pygame.locals import *
from gl import *
from BMP_Writer import GenerateBMP
from figures import *
from lights import * 
from material import *
from BMPTexture import BMPTexture
import os
 
width = 1512
height = 982

screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()

rend = Renderer(screen)

base_path = os.path.dirname(__file__)
background_path = os.path.join(base_path, "textures/background_hdri.bmp")

rend.envMap = BMPTexture(background_path)


# materiales opacos
red = Material(diffuse = [1, 0, 0], spec = 50, ks = 0.5, matType = OPAQUE)
green = Material(diffuse = [0, 1, 0], spec = 50, ks = 0.5, matType = OPAQUE)
blue = Material(diffuse = [0, 0, 1], spec = 50, ks = 0.5, matType = OPAQUE)

# materiales reflectivos
oro = Material(diffuse=[1.0, 0.84, 0.0], spec=90, ks=0.8, matType=REFLECTIVE)
plata = Material(diffuse=[0.9, 0.9, 0.9], spec=100, ks=0.9, matType=REFLECTIVE)


# materiales transparentes
vidrio = Material(diffuse=[1, 1, 1], spec=80, ks=0.5, ior=1.5, matType=TRANSPARENT)
vidrio_azul = Material(diffuse=[0.6, 0.8, 1.0], spec=90, ks=0.6, ior=1.3, matType=TRANSPARENT)


rend.scene.append(Cylinder(position = [-2, -2.5, -6], radius = 1, height = 1, material = red))
rend.scene.append(Cylinder(position = [-1, -0.5, -7], radius = 0.5, height = 1, material = oro))
rend.scene.append(Cylinder(position = [-2, 1, -5], radius = 0.5, height = 1.5, material = vidrio))

rend.scene.append(Ellipsoid(position = [2, -2, -7], radius = [0.5, 0.5, 1], material = green))
rend.scene.append(Ellipsoid(position = [1, 0, -6], radius = [1, 0.5, 0.5], material = plata))
rend.scene.append(Ellipsoid(position = [2, 2, -7], radius = [0.5, 1, 0.5], material = vidrio_azul))


rend.lights.append(DirectionalLight(direction = [-1,-1,-1], intensity = 1.2))
rend.lights.append(AmbientLight())

rend.glRender() 

isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                isRunning = False


    pygame.display.flip()
    clock.tick(60)


GenerateBMP('output.bmp', width, height, 3, rend.frameBuffer)

pygame.quit