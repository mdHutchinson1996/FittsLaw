import csv
from random import randint
import pygame
from math import sin, cos, sqrt, pi


class game():

    def __init__(self, fullScreen=False, randomFlag=True, numberOfTargets=12, sensitivity=10, deadZone=0.1, setWidths = [], setRadii = [], windowSize = (800, 800), joystick ="Mouse", user = "Default"):
        # Settings
        self.randomFlag = randomFlag
        self.setWidths = setWidths
        self.setRadii = setRadii
        self.numberOfTargets = numberOfTargets
        self.fullScreen = fullScreen
        self.windowSize = windowSize
        self.sensitivity = sensitivity# value greater than 1. Higher the number, the higher the sensitivity
        self.deadZone = deadZone + 0.001 #value from 0 to 1
        self.joystick = joystick
        self.user = user

        self.pastTarget = 0
        self.targets = []
        self.chosenTarget = 0
        self.targetWidth = 50
        self.flag = True
        self.radius = 150
        self.lastTicks = 0
        self.currentTicks = 0
        self.misses = 0
        self.lastPosition = (0,0)
        self.data = []
        self.setCount = 0

        #self.play()

    def play_joystick(self):
        pygame.init()
        if pygame.joystick.get_count()>0 :
            stick = pygame.joystick.Joystick(0)
            for x in range(pygame.joystick.get_count()):
                if pygame.joystick.Joystick(x).get_name == self.joystick:
                    stick=pygame.joystick.Joystick(x)
                    break

            pygame.event.pump()
            pygame.display.init()
            pygame.event.set_grab(True)
            if self.fullScreen:
                window = pygame.display.set_mode((0,0), pygame.FULLSCREEN) # 0, 0, fullscreen
            else:
                window = pygame.display.set_mode(self.windowSize)
            cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
            pygame.mouse.set_cursor(cursor)

            target = self.draw_ring(window)

            going = True

            while going:
                #pygame.time.Clock().tick(90) #Forces code to run at 90fps. Keeps mouse from getting wildly sensative
                event = pygame.event.poll()

                if event.type == pygame.JOYBUTTONDOWN:
                    if stick.get_button(0):
                        target = self.button_press(target, window)

                elif event.type == pygame.JOYAXISMOTION:
                    if stick.get_axis(0) > self.deadZone or stick.get_axis(0) < -self.deadZone or stick.get_axis(1) > self.deadZone or stick.get_axis(1) < -self.deadZone: #0.1 is the deadzone im applying to deal with jitter
                        #print(stick.get_axis(0))
                        # print(stick.get_axis(1))
                        # print("deadzone: ",self.deadZone)

                        #pygame.time.Clock().tick(90) #Forces code to run at 90fps. Keeps mouse from getting wildly sensative
                        pos = pygame.mouse.get_pos()
                        x = float(pos[0])
                        y = float(pos[1])
                        #print(stick.get_axis(1))
                        pygame.mouse.set_pos([round(x + stick.get_axis(0)*self.sensitivity), round(y + stick.get_axis(1)*self.sensitivity)])#Set_pos uses int's. this is awful. axis values are 0-1 and get rounded down.
                        self.stop_mouse(window)
                        # if pygame.event.peek(pygame.JOYBUTTONDOWN):
                        #     if stick.get_button(0):
                        #         target = self.button_press(target, window)
                        #         pygame.event.get()
                        #         break

                elif event.type == pygame.QUIT:
                    going = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        going = False

            fileName = self.user + ".csv"
            f = open(fileName, 'a')
            writer = csv.writer(f)
            writer.writerow(["sensitivity: "+str(self.sensitivity), "Num of Targets: "+str(self.numberOfTargets), "Deadzone: "+ str(self.deadZone), "Controller: "+self.joystick, "Random: "+str(self.randomFlag)])
            writer.writerow(["Time","Misses", "Width", "Distance"])
            writer.writerows(self.data)
            f.close()
            pygame.time.wait(10)
            pygame.display.quit()
        else:
            print("No Joysticks Found")
            pygame.display.quit()


    def play_mouse(self):
        pygame.init()
        pygame.event.pump()
        pygame.display.init()
        pygame.event.set_grab(True)
        if self.fullScreen:
            window = pygame.display.set_mode((0,0), pygame.FULLSCREEN) # 0, 0, fullscreen
        else:
            window = pygame.display.set_mode(self.windowSize)
        cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        pygame.mouse.set_cursor(cursor)

        target = self.draw_ring(window)

        going = True

        while going:

            event = pygame.event.poll()
            if event.type == pygame.MOUSEBUTTONUP:
                target = self.button_press(target, window)

            elif event.type == pygame.MOUSEMOTION:
                pygame.time.Clock().tick(90) #Forces code to run at 90fps. Keeps mouse from getting wildly sensative
                self.stop_mouse(window)

            if event.type == pygame.QUIT:
                going = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    going = False
        fileName = self.user + ".csv"
        f = open(fileName, 'a')
        writer = csv.writer(f)
        writer.writerow(["sensitivity: "+str(self.sensitivity), "Num of Targets: "+str(self.numberOfTargets), "Deadzone: "+ str(self.deadZone), "Controller: "+self.joystick, "Random: "+str(self.randomFlag)])
        writer.writerow(["Time","Misses", "Width", "Distance"])
        writer.writerows(self.data)
        f.close()
        pygame.time.wait(10)
        pygame.display.quit()


    def draw_ring(self, surface):

        x = []
        y = []
        # Get angles around ring that targets will be placed at
        theta = [0]
        for i in range(0, self.numberOfTargets-1):
            theta.append(theta[i]+(360/self.numberOfTargets))

        centerx = pygame.display.get_window_size()[0]/2
        centery = pygame.display.get_window_size()[1]/2

        # Algo for moving target around ring. Follows the movement shown in paper by I. MacKenzie
        if self.pastTarget <= self.numberOfTargets/2:
            if self.flag:
                if self.pastTarget <= (self.numberOfTargets-1)/2 :
                    self.chosenTarget = self.pastTarget + int(self.numberOfTargets/2)
                else:
                    self.chosenTarget = self.pastTarget - int(self.numberOfTargets/2)
                self.flag = False
            else:

                self.chosenTarget = self.pastTarget
                self.pastTarget = self.pastTarget + 1
                self.flag = True
        else:
            #reset targets and create new ring
            self.flag = True
            self.targets = []

            self.pastTarget = 0
            self.chosenTarget = 0

            # If not set to random, use set widths and radi
            if self.randomFlag:
                self.targetWidth = randint(20, 60)
                self.radius = randint(100, 300)
            else:
                if self.setCount >= len(self.setWidths):
                    self.setCount = 0
                self.targetWidth = self.setWidths[self.setCount]
                self.radius = self.setRadii[self.setCount]
                self.setCount = self.setCount +1
        # calc x and y position based on angles generated
        for i in range(len(theta)):
            x.append(centerx + self.radius * cos(theta[i] * pi / 180))
            y.append(centery + self.radius * sin(theta[i] * pi / 180))
        # create targets
        for i in range(len(x)):
            self.targets.append(pygame.draw.circle(surface, (50, 50, 50), (x[i], y[i]), self.targetWidth))
        # append chosen target at at end so that it is drawn last and on top of all other targets
        self.targets.append(pygame.draw.circle(surface, (200, 10, 10), (x[self.chosenTarget], y[self.chosenTarget]), self.targetWidth))
        pygame.display.flip()

        return self.targets[self.chosenTarget]

    # adds 10px border to window to prevent mouse exiting screen
    def stop_mouse(self, surface):
        if pygame.mouse.get_pos()[0] in range(0, 10): #left wall
            pygame.mouse.set_pos(11, pygame.mouse.get_pos()[1])

        if pygame.mouse.get_pos()[0] in range(surface.get_size()[0]-10, surface.get_size()[0]): # right wall
            pygame.mouse.set_pos(surface.get_size()[0]-11, pygame.mouse.get_pos()[1])

        if pygame.mouse.get_pos()[1] in range(0, 10): # ceiling
            pygame.mouse.set_pos(pygame.mouse.get_pos()[0], 11)

        if pygame.mouse.get_pos()[1] in range(surface.get_size()[1]-10, surface.get_size()[1]): # floor
            pygame.mouse.set_pos(pygame.mouse.get_pos()[0], surface.get_size()[1]-11)



    # deals with button press's and checks if mouse is within chosen target
    def button_press(self, currentTarget, window):

        dx = currentTarget.centerx - pygame.mouse.get_pos()[0]
        dy = currentTarget.centery - pygame.mouse.get_pos()[1]
        dist_sq = dx*dx + dy*dy

        rad = currentTarget.width/2

        if dist_sq < rad*rad:

            window.fill((0, 0 ,0))
            currentPos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            currentTarget = self.draw_ring(window)

            distance = sqrt((self.lastPosition[0]-currentPos[0])**2+(self.lastPosition[1]-currentPos[1])**2)
            self.lastPosition = currentPos

            if self.pastTarget > 0:
                self.currentTicks = pygame.time.get_ticks()
                dt = self.currentTicks - self.lastTicks
                self.lastTicks = self.currentTicks
                self.data.append([dt, self.misses, self.targetWidth, distance])
            else:
                self.data.append("###############")
                self.lastTicks = pygame.time.get_ticks()
        else:
            self.misses = self.misses +1

        return currentTarget

    def get_joysticks(self):
        pygame.init()
        count = pygame.joystick.get_count()
        sticks = []
        for x in range(count):
            sticks.append(pygame.joystick.Joystick(x).get_name())
        return sticks


if __name__ == '__main__':
    game = game()
    game.play_mouse()
    #print("after game")
