import tkinter as tk
from tkinter import filedialog as fk
import main

root = tk.Tk()
root.geometry("800x250")
root.title("Fitts's Law Setup")
root.resizable(width = False, height = False)
mainFrame = tk.Frame(root, width=800, height=250, bg = "light blue")

#Bases
userInfoFrame = tk.Frame(mainFrame, bg = "light blue")
checkBoxFrame = tk.Frame(mainFrame, bg = "light blue")
setFrame = tk.Frame(mainFrame, bg = "light blue")
screenFrame = tk.Frame(mainFrame, bg = "light blue")
variableFrame = tk.Frame(mainFrame, bg = "light blue")
startButton = tk.Button(mainFrame, text="Begin", bg = "cyan", command = lambda : begin())

#User info
userNameLabel = tk.Label(userInfoFrame, text="UserName", bg = "light blue")
userName = tk.StringVar()
userName.set("Default")
userNameBox = tk.Entry(userInfoFrame, textvariable = userName)
controller = tk.StringVar()
controller.set("Mouse")
controllerLabel = tk.Label(userInfoFrame, text="Controller", bg = "light blue")
sticks = main.game().get_joysticks()
controllerDrop = tk.OptionMenu(userInfoFrame, controller, "Mouse", *sticks)

#Variables
numTargetsLabel = tk.Label(variableFrame, text="Number of Targets", bg = "light blue")
numTargetsSpinner = tk.Spinbox(variableFrame, from_=2, to=20)
sensitivityLabel = tk.Label(variableFrame, text="Sensitivity", bg = "light blue")
sensitivitySpinner = tk.Spinbox(variableFrame, from_=1, to=20)
deadZoneLabel = tk.Label(variableFrame, text="Dead Zone", bg = "light blue")
deadZoneSpinner = tk.Spinbox(variableFrame, from_=0, to=99)

#Check boxes
randVar = tk.IntVar()
randVar.set(1)
randomCheck = tk.Checkbutton(checkBoxFrame,  text = "Random", command = lambda  : setDiag.config(state = "disable") if randVar.get() else setDiag.config(state="active"), variable = randVar, bg = "light blue")

screenVar = tk.IntVar()
screenCheck = tk.Checkbutton(checkBoxFrame, text = "FullScreen", command = lambda  : disableSize(True) if screenVar.get() else disableSize(False), variable = screenVar, bg = "light blue")


def disableSize(off):
    if(off):
        screenWEntry.config(state = "disabled")
        screenHEntry.config(state = "disabled")
    else:
        screenWEntry.config(state = "normal")
        screenHEntry.config(state = "normal")


setVar = tk.StringVar()
setText = tk.Entry(setFrame, textvariable = setVar, state="disable")
setDiag = tk.Button(setFrame, text = "Choose a csv file", command = lambda : setVar.set(fk.askopenfilename()), state = "disable")

screenLabelW = tk.Label(screenFrame, text = "Width:", bg = "light blue")
screenLabelH = tk.Label(screenFrame, text = "Height:", bg = "light blue")
screenW = tk.StringVar()
screenW.set("800")
screenH = tk.StringVar()
screenH.set("800")
screenWEntry = tk.Entry(screenFrame, textvariable = screenW)
screenHEntry = tk.Entry(screenFrame, textvariable = screenH)


def packWindow():
    #mainFrame.pack()
    mainFrame.place(relheight = 1, relwidth = 1)
    userInfoFrame.place(height = 50, width = 800)
    variableFrame.place(height = 50, width = 800, y = 60)
    checkBoxFrame.place(height = 25, width = 800, y = 125)

    setFrame.place(height = 100, width = 400 , y=150)
    screenFrame.place(height = 100, width = 400, x=400, y=150)
    startButton.place(height = 50, width = 800, y = 200)

    randomCheck.place(height = 25, width = 400)
    screenCheck.place(height = 25, width = 400, x = 400)

    userNameLabel.place(height = 25, width = 400)
    userNameBox.place(height = 25, width = 400, y = 25)
    controllerLabel.place(height = 25, width = 400, x = 400)
    controllerDrop.place(height = 25, width = 400, x = 400, y = 25)

    numTargetsLabel.place(height = 25, relwidth=0.34)
    numTargetsSpinner.place(height = 25, width = 50, relx = 0.15, y =25)
    sensitivityLabel.place(height = 25, relwidth = 0.34, relx = 0.34)
    sensitivitySpinner.place(height = 25, width = 50, relx = 0.5, y = 25)
    deadZoneLabel.place(height = 25, relwidth = 0.34, relx = 0.68)
    deadZoneSpinner.place(height = 25, width = 50, relx = 0.85, y = 25)

    setDiag.place(height = 25, width = 400, y = 25)
    setText.place(height = 25, width=400)
    screenLabelW.place(height = 25, width = 200)
    screenWEntry.place(height = 25, width = 200, x = 200)
    screenLabelH.place(height = 25, width = 200, y = 25)
    screenHEntry.place(height = 25, width = 400, y = 25, x = 200)


def begin():
    name = userName.get()
    joystick = controller.get()
    fullScreen = bool(screenVar.get())
    screenSize = (int(screenW.get()), int(screenH.get()))
    random = bool(randVar.get())
    if not random:
        setWidths, setRadii = readSet()
    else:
        setWidths, setRadii = [], []
    numTargets = int(numTargetsSpinner.get())
    sensitivity = int(sensitivitySpinner.get())
    deadZone = float(deadZoneSpinner.get()) / 10
    newGame = main.game(fullScreen, random, numTargets, sensitivity, deadZone, setWidths, setRadii, screenSize, joystick, name)
    if joystick == "Mouse":
        newGame.play_mouse()
    else:
        newGame.play_joystick()


def readSet():
    f = open(str(setVar.get()), "r")
    stringRadii = f.readline()
    stringWidths = f.readline()
    f.close()
    set_radii = [int(x) for x in stringRadii.split(",")]
    setWidths = [int(x) for x in stringWidths.split(",")]

    return setWidths, set_radii


packWindow()
#main.game().get_joysticks()
root.mainloop()



