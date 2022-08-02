import csv
from random import randint
import pygame
from math import sin, cos, sqrt, pi

"""
This class is used for the fitts's law game
"""
class game():

    """Parameters;
    fullScreen: bool, defines whether the game is run in fullscreen (True) or windowed (False)
    randomFlag: bool, does the game use randomly generated target widths and circle radii or read from a user created set
    numberOfTarget: int, the number of targets rendered for the game. Default: 12, min: 2, Max: 20
    sensitivity: int, a scalar value which is applied to the joystick input (if a joystick is used). Default: 10, Min: 1, Max: 20
    deadZone: float, The mininmum value for joystick input that the game will register as valid input. Min: 0, Max: 1
    setWidths: list, a list of widths for the targets. Only used if randomFlag == False. Must have same length as setRadii
    setRadii: list, a set of radii for the circle. Only used if randomFlag == False. Must have same length as setWidths
    windowSize: tuple, (x, y), The width and height of the window. Only used if fullScreen  == false. Default: (800,800). Min: (600,600)
    joyStick: String, The name of the joystick selected to be used. Default: "Mouse"
    user: String, The name of the user playign the game. Default: "Default"
    """
    def __init__(self, fullScreen=False, randomFlag=True, numberOfTargets=12, sensitivity=10, deadZone=0.1, setWidths = [], setRadii = [], windowSize = (800, 800), joystick ="Mouse", user = "Default"):
        # Settings
        self.randomFlag = randomFlag
        self.setWidths = setWidths
        self.setRadii = setRadii
        self.numberOfTargets = numberOfTargets
        self.fullScreen = fullScreen
        self.windowSize = windowSize
        self.sensitivity = sensitivity # value greater than 1. Higher the number, the higher the sensitivity
        self.deadZone = deadZone + 0.001 # value from 0 to 1 (Very small value added to prevent freezing at 0 deadzone)
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

    """
    Begins and instance of pygame which utilizes the selected joystick.
    """
    def play_joystick(self):
        # Begin pygame, verify that a joystick with the given name exists. Define stick as an instance of that joystick object.
        # if the joystick does not exist, end the game.
        pygame.init()
        if pygame.joystick.get_count()>0 :
            stick = pygame.joystick.Joystick(0)
            for x in range(pygame.joystick.get_count()):
                if pygame.joystick.Joystick(x).get_name == self.joystick:
                    stick=pygame.joystick.Joystick(x)
                    break

            # Pump begins the event listener. set_grab forces the users focus onto the game.
            pygame.event.pump()
            pygame.display.init()
            pygame.event.set_grab(True)

            #Create window dependant on fullscreen
            if self.fullScreen:
                window = pygame.display.set_mode((0,0), pygame.FULLSCREEN) # 0, 0, fullscreen
            else:
                window = pygame.display.set_mode(self.windowSize)

            #Create the gamers cursor.
            cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
            pygame.mouse.set_cursor(cursor)

            #Draw an initial set of targets. This uses default settings. This means the first set of targets the user experiences are always the same
            target = self.draw_ring(window)

            #game loop
            going = True
            while going:
                # Read an event from the queue
                event = pygame.event.poll()
                # Process a button press from the gamepad
                if event.type == pygame.JOYBUTTONDOWN:
                    # get_button(0) returns the bool value of the A button on a xbox controller.
                    if stick.get_button(0):
                        target = self.button_press(target, window)
                # Process joystick movement
                elif event.type == pygame.JOYAXISMOTION:
                    # Check that atleast one axis value is outside the given deadZone
                    if stick.get_axis(0) > self.deadZone or stick.get_axis(0) < -self.deadZone or stick.get_axis(1) > self.deadZone or stick.get_axis(1) < -self.deadZone:
                        # get the mouse position
                        pos = pygame.mouse.get_pos()
                        x = float(pos[0])
                        y = float(pos[1])
                        # Change the mouse position on the screen based on the current (x,y), the joystick axis value, and the sensitivity scalar
                        pygame.mouse.set_pos([round(x + stick.get_axis(0)*self.sensitivity), round(y + stick.get_axis(1)*self.sensitivity)])# Set_pos uses int's. this is awful. axis values are 0-1 and get rounded down.
                        # Check if the mouse is at the edge of the window and prevent it from escaping the window.
                        self.stop_mouse(window)
                # Process quit button on the window being clicked and end the game loop
                elif event.type == pygame.QUIT:
                    going = False
                # Process the escape button being pushed and end the game loop
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        going = False

            # Create a .csv using the users name
            fileName = self.user + ".csv"
            f = open(fileName, 'a')
            writer = csv.writer(f)
            # Write the users settings at the top of the append
            writer.writerow(["sensitivity: "+str(self.sensitivity), "Num of Targets: "+str(self.numberOfTargets), "Deadzone: "+ str(self.deadZone), "Controller: "+self.joystick, "Random: "+str(self.randomFlag)])
            # Write a title for each column
            writer.writerow(["Time","Misses", "Width", "Distance"])
            # Write the collected user data
            writer.writerows(self.data)
            f.close()
            pygame.time.wait(10)
            pygame.display.quit()
        else:
            print("No Joysticks Found")
            pygame.display.quit()

    """
    Begins and instance of the game utilizing the players mouse rather than a joystick mimics play_joystick()
    """
    def play_mouse(self):
        # Start game, Start event listener, grab focus.
        pygame.init()
        pygame.event.pump()
        pygame.display.init()
        pygame.event.set_grab(True)
        # Create window at given size
        if self.fullScreen:
            window = pygame.display.set_mode((0,0), pygame.FULLSCREEN) # 0, 0, fullscreen
        else:
            window = pygame.display.set_mode(self.windowSize)
        # Set cursor
        cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        pygame.mouse.set_cursor(cursor)

        # Create the default starting ring
        target = self.draw_ring(window)

        # Game loop
        going = True
        while going:

            # poll the event queue
            event = pygame.event.poll()

            # Process mouse button being pushed
            if event.type == pygame.MOUSEBUTTONUP:
                target = self.button_press(target, window)

            # Process mouse movement
            elif event.type == pygame.MOUSEMOTION:
                # Check if the mouse is at the edge of the window and prevent exit
                self.stop_mouse(window)
            # process exit button being pushed and end game loop
            if event.type == pygame.QUIT:
                going = False
            # process escape being pushed and end game loop
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    going = False
        # Create .csv using the users name
        fileName = self.user + ".csv"
        f = open(fileName, 'a')
        writer = csv.writer(f)
        # Write the users settings
        writer.writerow(["sensitivity: "+str(self.sensitivity), "Num of Targets: "+str(self.numberOfTargets), "Deadzone: "+ str(self.deadZone), "Controller: "+self.joystick, "Random: "+str(self.randomFlag)])
        # Create titles for columns
        writer.writerow(["Time","Misses", "Width", "Distance"])
        # Write the collected user data
        writer.writerows(self.data)
        f.close()
        pygame.time.wait(10)
        pygame.display.quit()


    """
    This method draws the ring of targets onto a given surface (window)
    """
    def draw_ring(self, surface):

        x = []
        y = []
        # Get angles around ring that targets will be placed at based on the number of targets
        theta = [0]
        for i in range(0, self.numberOfTargets-1):
            theta.append(theta[i]+(360/self.numberOfTargets))
        # Get the center of the window
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

    """
    Checks if the mouse is within a 10px border of the edge of the screen and moves it inside the border if it is.
    """
    def stop_mouse(self, surface):
        if pygame.mouse.get_pos()[0] in range(0, 10): # left wall
            pygame.mouse.set_pos(11, pygame.mouse.get_pos()[1])

        if pygame.mouse.get_pos()[0] in range(surface.get_size()[0]-10, surface.get_size()[0]): # right wall
            pygame.mouse.set_pos(surface.get_size()[0]-11, pygame.mouse.get_pos()[1])

        if pygame.mouse.get_pos()[1] in range(0, 10): # ceiling
            pygame.mouse.set_pos(pygame.mouse.get_pos()[0], 11)

        if pygame.mouse.get_pos()[1] in range(surface.get_size()[1]-10, surface.get_size()[1]): # floor
            pygame.mouse.set_pos(pygame.mouse.get_pos()[0], surface.get_size()[1]-11)



    """
    Deals with buttons presses, updates the targets if the current target is clicked. draw targets
    """
    def button_press(self, currentTarget, window):
        # Determine distance from mouse pointer to the current target
        dx = currentTarget.centerx - pygame.mouse.get_pos()[0]
        dy = currentTarget.centery - pygame.mouse.get_pos()[1]
        dist_sq = dx*dx + dy*dy
        # get the radius of the current target
        rad = currentTarget.width/2
        # if the distance between the cursor and the center of the target is within the radius. Then the target has been clicked.
        if dist_sq < rad*rad:
            # Empty the window
            window.fill((0, 0 ,0))
            # get the current mouse position
            currentPos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            # Draw a new ring with updated current target
            currentTarget = self.draw_ring(window)
            # get the distance from the last target to the current target that was just clicked
            distance = sqrt((self.lastPosition[0]-currentPos[0])**2+(self.lastPosition[1]-currentPos[1])**2)
            self.lastPosition = currentPos
            # if the ring has just been updated
            if self.pastTarget > 0:
                # determine the time between the last target being clicked and this target being clicked.
                self.currentTicks = pygame.time.get_ticks()
                dt = self.currentTicks - self.lastTicks
                self.lastTicks = self.currentTicks
                # append to the data list, the time between target hits, number of misses, width of the target and the distance between targets
                self.data.append([dt, self.misses, self.targetWidth, distance])
            else:
                # If the ring has just updated: print seperator and update the time
                self.data.append("###############")
                self.lastTicks = pygame.time.get_ticks()
        else:
            # if the target is missed, increment the number of misses
            self.misses = self.misses + 1

        return currentTarget

    """
    Returns the available joysticks that are plugged into the computer
    """
    @staticmethod
    def get_joysticks():
        pygame.init()
        count = pygame.joystick.get_count()
        sticks = []
        for x in range(count):
            sticks.append(pygame.joystick.Joystick(x).get_name())
        return sticks


if __name__ == '__main__':
    game = game()
    game.play_mouse()
