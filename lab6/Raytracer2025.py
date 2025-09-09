import pygame
from pygame.locals import *
from gl import *
from BMP_Writer import GenerateBMP
from figures import *
from lights import * 
from material import *
from BMPTexture import BMPTexture
import os
 
width = 1024
height = 1024

screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()

rend = Renderer(screen)

base_path = os.path.dirname(__file__)
background_path = os.path.join(base_path, "textures/background_hdri.bmp")

rend.envMap = BMPTexture(background_path)

# materiales opacos
dirt_texture = os.path.join(base_path, 'textures/dirt.bmp')
green = Material(diffuse = [0.804,0.521,0.247], spec=50, ks = 0.3, texture = BMPTexture(dirt_texture))
purple = Material(diffuse = [1,0,1], spec=50, ks = 0.3)

# mateiales reflectivos
pearl = Material(diffuse = [0.95, 0.90, 0.85], spec = 100, ks = 0.8, matType = REFLECTIVE)
hematite = Material(diffuse = [0.2, 0.2, 0.25], spec = 80, ks = 0.75, matType = REFLECTIVE)

# materiales transparentes
ice_texture = os.path.join(base_path, 'textures/ice.bmp')
iceTexture = BMPTexture(ice_texture)
ice = Material(diffuse = [0.85, 0.95, 1.0], spec = 32, ks = 0.05, ior = 1.31, matType = TRANSPARENT, texture = iceTexture)
amber = Material(diffuse = [1.0, 0.6, 0.2], spec = 64, ks = 0.15, ior = 1.55, matType = TRANSPARENT)


rend.scene.append(Sphere(position = [-1.5, 1,-4], radius = 0.5, material = green))
rend.scene.append(Sphere(position = [-1.5, -1,-4], radius = 0.5, material = purple))
rend.scene.append(Sphere(position = [0, 1,-4], radius = 0.5, material = pearl))
rend.scene.append(Sphere(position = [0, -1,-4], radius = 0.5, material = hematite))
rend.scene.append(Sphere(position = [1.5, 1,-4], radius = 0.5, material = ice))
rend.scene.append(Sphere(position = [1.5, -1,-4], radius = 0.5, material = amber))

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