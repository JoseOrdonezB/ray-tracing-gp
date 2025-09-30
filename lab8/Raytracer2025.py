import pygame
from pygame.locals import *
from gl import *
from BMP_Writer import GenerateBMP
from figures import *
from lights import * 
from material import *
from BMPTexture import BMPTexture
import os
 
width = 256
height = 256

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

# materiales transparentes
vidrio = Material(diffuse=[1, 1, 1], spec=80, ks=0.5, ior=1.5, matType=TRANSPARENT)

rend.scene.append(Cylinder(position = [-2, -1.5, -4], radius = 0.5, height = 1, material = red))
rend.scene.append(Cylinder(position = [0, -1.5, -4], radius = 0.5, height = 1, material = oro))
rend.scene.append(Cylinder(position = [2, -1.5, -4], radius = 0.5, height = 1, material = vidrio))


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