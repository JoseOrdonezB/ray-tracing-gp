import pygame
from pygame.locals import *
from gl import *
from BMP_Writer import GenerateBMP
from figures import *
from lights import * 
from material import *
from BMPTexture import BMPTexture
import os
 
width = 1080
height = 720

screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()

rend = Renderer(screen)

# base_path = os.path.dirname(__file__)
# background_path = os.path.join(base_path, "textures/background_hdri.bmp")

# rend.envMap = BMPTexture(background_path)


# materiales opacos
red = Material(diffuse = [1, 0, 0], spec = 50, ks = 0.5, matType = OPAQUE)

# materiales reflectivos
oro = Material(diffuse=[1.0, 0.84, 0.0], spec=90, ks=0.8, matType=REFLECTIVE)

# materiales transparentes
vidrio = Material(diffuse=[0.3, 0.6, 1.0], spec=80, ks=0.5, ior=1.5, matType=TRANSPARENT)

# # Escena final
# rend.scene.append(Plane(position=[0, 0, -6], normal=[0, 0, 1], material=pared))
# rend.scene.append(Plane(position=[-3.5, 0, -6], normal=[1, 0, 0], material=pared))
# rend.scene.append(Plane(position=[3.5, 0, -6], normal=[-1, 0, 0], material=pared))
# rend.scene.append(Plane(position=[0, -2, -6], normal=[0, 1, 0], material=suelo))
# rend.scene.append(Plane(position=[0, 2, -6], normal=[0, -1, 0], material=techo))


# rend.scene.append(Triangle(v0=[0, 1.9, -6], v1=[-0.4, 1.9, -6 + 0.7], v2=[0.4, 1.9, -6 + 0.7], material=oro))
# rend.scene.append(Triangle(v0=[-0.4, 1.9, -6 + 0.7], v1=[-0.8, 1.9, -6 + 1.4], v2=[0, 1.9, -6 + 1.4], material=oro))
# rend.scene.append(Triangle(v0=[0.4, 1.9, -6 + 0.7], v1=[0, 1.9, -6 + 1.4], v2=[0.8, 1.9, -6 + 1.4], material=oro))

# rend.scene.append(AABB(center=[-1.5, -1.7, -4.3], size=[0.8, 0.8, 0.8], material = pedestal))
# rend.scene.append(Sphere(position=[-1.5, -0.8, -4.3], radius=0.4, material = esfera_oro))

# rend.scene.append(AABB(center=[1.5, -1.7, -4.8], size=[0.8, 0.8, 0.8], material = pedestal))
# rend.scene.append(Disk(position=[1.5, -1, -4.8], normal=[0.2, 1, 0.3], radius=0.5, material=disco_vidrio))

# rend.scene.append(AABB(center=[0, -1.7, -4.5], size=[0.8, 0.8, 0.8], material = pedestal))
# rend.scene.append(Triangle(v0=[-0.3, -1, -4.7], v1=[0.3, -1, -4.7], v2=[0, -0.4, -4.5], material=triangulo_cobre))

rend.lights.append(DirectionalLight(direction = [1e-6, 1e-6, -1], intensity = 1.2))
rend.lights.append(AmbientLight(intensity = 1.5))

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