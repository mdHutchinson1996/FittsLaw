from random import randint
import pygame
from math import sin, cos, sqrt, pi
from csv import writer

# Settings
randomFlag = True
setWidths = [20, 60, 30, 50, 40, 30, 20, 50]
setRadi = [100, 300, 200, 150, 250, 300, 150, 100]
numberOfTargets = 12
fullScreen = True
windowSize = (800,800)
sensitivity = 10# value greater than 1. Higher the number, the higher the sensitivity
deadZone = 0.1 #value from 0 to 1

# Globals
targets = []
pastTarget = 0
targetWidth = 50
chosenTarget = 0
flag = True
radius = 150
lastTicks = 0
currentTicks = 0
misses = 0
lastPosition = (0,0)
data = []
setCount = 0


def draw_ring(surface):

    global targets
    global chosenTarget
    global pastTarget
    global numberOfTargets
    global flag
    global radius
    global targetWidth
    global randomFlag
    global setCount
    global setWidths
    global setRadi
    x = []
    y = []
    # Get angles around ring that targets will be placed at
    theta = [0]
    for i in range(0, numberOfTargets-1):
        theta.append(theta[i]+(360/numberOfTargets))

    centerx = pygame.display.get_window_size()[0]/2
    centery = pygame.display.get_window_size()[1]/2

    # Algo for moving target around ring. Follows the movement shown in paper by I. MacKenzie
    if pastTarget <= numberOfTargets/2:
        if flag:
            if pastTarget <= (numberOfTargets-1)/2 :
                chosenTarget = pastTarget + int(numberOfTargets/2)
            else:
                chosenTarget = pastTarget - int(numberOfTargets/2)
            flag = False
        else:

            chosenTarget = pastTarget
            pastTarget = pastTarget + 1
            flag = True
    else:
        #reset targets and create new ring
        flag = True
        targets = []

        pastTarget = 0
        chosenTarget = 0

        # If not set to random, use set widths and radi
        if randomFlag:
            targetWidth = randint(20, 60)
            radius = randint(100, 300)
        else:
            if setCount >= len(setWidths):
                setCount = 0
            targetWidth = setWidths[setCount]
            radius = setRadi[setCount]
            setCount = setCount +1
    # calc x and y position based on angles generated
    for i in range(len(theta)):
        x.append(centerx + radius * cos(theta[i] * pi / 180))
        y.append(centery + radius * sin(theta[i] * pi / 180))
    # create targets
    for i in range(len(x)):
        targets.append(pygame.draw.circle(surface, (50, 50, 50), (x[i], y[i]), targetWidth))
    # append chosen target at at end so that it is drawn last and on top of all other targets
    targets.append(pygame.draw.circle(surface, (200, 10, 10), (x[chosenTarget], y[chosenTarget]), targetWidth))
    pygame.display.flip()

    return targets[chosenTarget]

# adds 10px border to window to prevent mouse exiting screen
def stop_mouse(surface):
    if pygame.mouse.get_pos()[0] in range(0, 10): #left wall
        pygame.mouse.set_pos(11, pygame.mouse.get_pos()[1])

    if pygame.mouse.get_pos()[0] in range(surface.get_size()[0]-10, surface.get_size()[0]): # right wall
        pygame.mouse.set_pos(surface.get_size()[0]-11, pygame.mouse.get_pos()[1])

    if pygame.mouse.get_pos()[1] in range(0, 10): # ceiling
        pygame.mouse.set_pos(pygame.mouse.get_pos()[0], 11)

    if pygame.mouse.get_pos()[1] in range(surface.get_size()[1]-10, surface.get_size()[1]): # floor
        pygame.mouse.set_pos(pygame.mouse.get_pos()[0], surface.get_size()[1]-11)


# def create_target_random(surface):
#     radius = random.randint(25, 100)
#     sizeX = surface.get_size()[0]-radius-10 # -10 added to account for border created by stop_mouse
#     sizeY = surface.get_size()[1]-radius-10
#     x = random.randint(radius, sizeX)
#     y = random.randint(radius, sizeY)
#
#     target = pygame.draw.circle(surface, (200, 10, 10), (x, y), radius)
#     return target


# deals with button press's and checks if mouse is within chosen target
def button_press(currentTarget):
    global targetWidth
    global pastTarget
    global lastTicks
    global currentTicks
    global misses
    global lastPosition
    dx = currentTarget.centerx - pygame.mouse.get_pos()[0]
    dy = currentTarget.centery - pygame.mouse.get_pos()[1]
    dist_sq = dx*dx + dy*dy

    rad = currentTarget.width/2

    if dist_sq < rad*rad:

        window.fill((0, 0 ,0))
        currentPos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        currentTarget = draw_ring(window)

        distance = sqrt((lastPosition[0]-currentPos[0])**2+(lastPosition[1]-currentPos[1])**2)
        lastPosition = currentPos

        if pastTarget > 0:
            currentTicks = pygame.time.get_ticks()
            dt = currentTicks - lastTicks
            lastTicks = currentTicks
            data.append([dt, misses, targetWidth, distance])
        else:
            data.append("###############")
            lastTicks = pygame.time.get_ticks()
    else:
        misses = misses +1

    return currentTarget

# game code
pygame.init()

if(pygame.joystick.get_count()>0):
    stick = pygame.joystick.Joystick(0)

    pygame.event.pump()
    pygame.display.init()
    pygame.event.set_grab(True)
    if fullScreen:
        window = pygame.display.set_mode((0,0), pygame.FULLSCREEN) # 0, 0, fullscreen
    else:
        window = pygame.display.set_mode(windowSize)
    cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
    pygame.mouse.set_cursor(cursor)

    target = draw_ring(window)

    going = True

    while going:

        event = pygame.event.poll()

        if event.type == pygame.JOYBUTTONDOWN:
            if stick.get_button(0):
                target = button_press(target)

        elif event.type == pygame.JOYAXISMOTION:
            while stick.get_axis(0) > deadZone or stick.get_axis(0) < -deadZone or stick.get_axis(1) > deadZone or stick.get_axis(1) < -deadZone: #0.1 is the deadzone im applying to deal with jitter

                pygame.time.Clock().tick(90) #Forces code to run at 90fps. Keeps mouse from getting wildly sensative

                pos = pygame.mouse.get_pos()
                x = float(pos[0])
                y = float(pos[1])
                pygame.mouse.set_pos([round(x + stick.get_axis(0)*sensitivity), round(y + stick.get_axis(1)*sensitivity)])#Set_pos uses int's. this is awful. axis values are 0-1 and get rounded down.
                stop_mouse(window)
                if pygame.event.peek(pygame.JOYBUTTONDOWN):
                    if stick.get_button(0):
                        target = button_press(target)
                        pygame.event.get()
                        break

        if event.type == pygame.QUIT:
            going = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                going = False

    f = open('data.csv', 'w')
    writer = writer(f)
    writer.writerow(["Time","Misses", "Width", "Distance"])
    writer.writerows(data)
    f.close()
    pygame.time.wait(10)
else:
    print("No Joysticks Found")
