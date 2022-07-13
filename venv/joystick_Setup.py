import pygame.joystick

pygame.init()

print(pygame.joystick.get_count())
stick = pygame.joystick.Joystick(0)
print(stick.get_name())
