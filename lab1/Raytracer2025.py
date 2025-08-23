import pygame
from pygame.locals import *
from gl import *
from BMP_Writer import GenerateBMP

width = 960
height = 540

screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock

rend = Renderer(screen)

isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                isRunning = False

    rend.glClear()

    rend.glRender()

    pygame.display.flip()
    clock.tick(60)


GenerateBMP('output.bmp', width, height, 3, rend.frameBuffer)

pygame.quit