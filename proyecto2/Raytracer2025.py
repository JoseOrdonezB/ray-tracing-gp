import pygame
from pygame.locals import *
from gl import *
from BMP_Writer import GenerateBMP
from figures import *
from lights import * 
from material import *
from BMPTexture import BMPTexture
import os
 
width = 512
height = 512

screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()

rend = Renderer(screen)

base_path = os.path.dirname(__file__)
background_path = os.path.join(base_path, "textures/background_hdri.bmp")

rend.envMap = BMPTexture(background_path)


mountain_texture = os.path.join(base_path, 'textures/vecteezy_grunge-texture-effect-distressed-overlay-rough-textured_11449725.bmp')
mountain = Material(diffuse = [0.7764705882, 0.0, 1.0], spec=50, ks = 0.3, texture = BMPTexture(mountain_texture))

# materiales opacos
black = Material(diffuse = [0, 0, 0], spec = 10, ks = 0.1, matType = OPAQUE)
purple = Material(diffuse = [0.7764705882, 0.0, 1.0], spec = 50, ks = 0.3, matType = OPAQUE)
cyan = Material(diffuse = [0.168627451, 1.0, 0.976470588], spec = 50, ks = 0.3, matType = OPAQUE)

# materiales reflectivos
oro = Material(diffuse=[1.0, 0.84, 0.0], spec=90, ks=0.8, matType=REFLECTIVE)
plata = Material(diffuse=[0.9, 0.9, 0.9], spec=100, ks=0.9, matType=REFLECTIVE)


# materiales transparentes
vidrio = Material(diffuse=[1, 1, 1], spec=80, ks=0.5, ior=1.5, matType=TRANSPARENT)
obsidiana = Material(diffuse=[0.02, 0.025, 0.03], spec=110, ks=0.85, ior=1.52, matType=TRANSPARENT)

# Escena final (vaporwave)
# Suelo (plano)
rend.scene.append(Plane(position = [0, -2, 0], normal = [0, 1, 0], material = obsidiana))

# Montañas (cono)
rend.scene.append(Cone(position = [-2, -2, -8], radius = 1, height = 2.75, material = cyan))
rend.scene.append(Cone(position = [-3, -2, -7], radius = 1, height = 2.75, material = cyan))
rend.scene.append(Cone(position = [-4, -2, -6], radius = 1, height = 2.75, material = cyan))
rend.scene.append(Cone(position = [-5, -2, -5], radius = 1, height = 2.75, material = cyan))

rend.scene.append(Cone(position = [2, -2, -8], radius = 1, height = 2.75, material = cyan))
rend.scene.append(Cone(position = [3, -2, -7], radius = 1, height = 2.75, material = cyan))
rend.scene.append(Cone(position = [4, -2, -6], radius = 1, height = 2.75, material = cyan))
rend.scene.append(Cone(position = [5, -2, -5], radius = 1, height = 2.75, material = cyan))

# Sol (esfera)
rend.scene.append(Sphere(position = [0, 3, -15], radius = 5, material = oro))

# Torres 1 (cilindro)
rend.scene.append(Cylinder(position = [-3, -2, -10], radius = 0.75, height = 4, material = mountain))
rend.scene.append(Cylinder(position = [3, -2, -10], radius = 0.75, height = 4, material = mountain))

# Torres 2 (Elipsoide)
rend.scene.append(Ellipsoid(position = [-5.5, 0, -10], radius = [1.5, 5, 0.75], material = purple))
rend.scene.append(Ellipsoid(position = [5.5, 0, -10], radius = [1.5, 5, 0.75], material = purple))

# Detalle del centro (toroide)
rend.scene.append(Torus(position = [0, -1.9, -6], major_radius = 0.4, minor_radius = 0.05, material = purple))
rend.scene.append(Torus(position = [0, -1.5, -3], major_radius = 0.4, minor_radius = 0.05, material = purple))


# # Esfera
# rend.scene.append(Sphere(position=[0, -2.0, -8], radius=0.75, material=blue))

# # Plano (suelo) en y = -3
# rend.scene.append(Plane(position=[0, -3.0, -5], normal=[0, 1, 0], material=green))

# # Disco
# rend.scene.append(Disk(position=[3.0, -2.9, -6.0], normal=[0, 1, 0], radius=0.75, material=oro))

# # AABB (caja alineada a ejes)
# rend.scene.append(AABB(center=[-3.0, 0.0, -6.5], size=[1.0, 1.0, 1.0], material=red))

# # Triángulo
# rend.scene.append(Triangle(v0=[-0.5, 2.5, -6.0], v1=[0.5, 2.5, -6.0], v2=[0.0, 1.5, -6.0], material=plata))

# # Cono (base en position, eje +Y)
# rend.scene.append(Cone(position=[-3.0, -2.5, -8.0], radius=0.7, height=1.5, material=vidrio_azul))

# # Toroide
# rend.scene.append(Torus(position=[3.0, 0.5, -8.0], major_radius=1.0, minor_radius=0.3, material=oro))

rend.lights.append(DirectionalLight(direction=[-1, -1, -1], intensity=1.2, color=[1.0, 0.0, 1.0]))
# rend.lights.append(DirectionalLight(direction = [-1,-1,-1], intensity = 1.2))
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