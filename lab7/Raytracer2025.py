import pygame
from pygame.locals import *
from gl import *
from BMP_Writer import GenerateBMP
from figures import *
from lights import * 
from material import *
from BMPTexture import BMPTexture
import os
 
width = 128
height = 128

screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()

rend = Renderer(screen)

base_path = os.path.dirname(__file__)
background_path = os.path.join(base_path, "textures/background_hdri.bmp")

rend.envMap = BMPTexture(background_path)


# materiales opacos
purple = Material(diffuse = [1,0,1], spec=50, ks = 0.3)
red = Material(diffuse = [1,0,0], spec=50, ks = 0.4)

# mateiales reflectivos
pearl = Material(diffuse = [0.95, 0.90, 0.85], spec = 100, ks = 0.8, matType = REFLECTIVE)
hematite = Material(diffuse = [0.2, 0.2, 0.25], spec = 80, ks = 0.75, matType = REFLECTIVE)

# materiales transparentes
amber = Material(diffuse = [1.0, 0.6, 0.2], spec = 64, ks = 0.15, ior = 1.55, matType = TRANSPARENT)

# prueba esfera
rend.scene.append(Sphere(position = [0, 0, -4], radius = 0.5, material = purple))

# prueba plano
rend.scene.append(Plane(position = [0, -2, 0], normal = [0, 1, 0], material = red))

# prueba disco
rend.scene.append(Disk(position = [0, -1, -4], radius = 1, normal = [0, 1, 0], material = pearl))

# Luces
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