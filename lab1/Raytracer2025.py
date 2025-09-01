import pygame
from pygame.locals import *
from gl import *
from BMP_Writer import GenerateBMP
from figures import *
from lights import * 
from material import *
 
width = 256
height = 256

screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()

rend = Renderer(screen)

# Jigglypuff materials
pink = Material(diffuse = [1, 0.702, 0.980], spec = 16, ks = 0.5)
white = Material(diffuse = [1, 1, 1])
aqua = Material(diffuse = [0.329, 0.655, 0.620], spec = 16, ks = 0.5)
black = Material(diffuse = [0,0,0])
red = Material(diffuse = [0.722, 0.282, 0.529])

# body
rend.scene.append(Sphere(position = [0,0,-7], radius = 2, material = pink))

# eyes
rend.scene.append(Sphere(position = [-0.5,0.3,-4], radius = 0.4, material = white))
rend.scene.append(Sphere(position = [0.5,0.3,-4], radius = 0.4, material = white))

# pupils
rend.scene.append(Sphere(position = [-0.5, 0.3, -3.6], radius = 0.2, material = aqua))
rend.scene.append(Sphere(position = [0.5, 0.3, -3.6], radius = 0.2, material = aqua))

# mouth
rend.scene.append(Sphere(position = [0, -0.3, -4], radius = 0.15, material = red))

# hair
rend.scene.append(Sphere(position = [0.2, 0.7, -4.5], radius = 0.5, material = pink))
rend.scene.append(Sphere(position = [-0.1, 1.2, -5], radius = 0.8, material = pink))

# arms
rend.scene.append(Sphere(position = [-0.5, -0.7, -4], radius = 0.2, material = pink))
rend.scene.append(Sphere(position = [0.5, -0.7, -4], radius = 0.2, material = pink))

# feet
rend.scene.append(Sphere(position = [-0.7, -2, -6], radius = 0.5, material = pink))
rend.scene.append(Sphere(position = [0.7, -2, -6], radius = 0.5, material = pink))

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