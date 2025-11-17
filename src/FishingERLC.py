import pyautogui
import keyboard
from mss import mss
import asyncio

pyautogui.FAILSAFE = True
sct = mss()
activationThreshold = 15
reelingTolerance = 0.04

'''
instructions:
face character in 3rd person with your back facing the water, and a railing to stop you from being dragged
cast once manually, and when a fish arrives, hover your mouse over the upper left limit of the minigame and press p
repeat for the lower right bound of the minigame
repeat for the fishing icon to the right of the vertical bar
place your mouse over where you want to cast and leave it there
press p to start the program
pres x to stop it
'''
async def recast():
    await asyncio.sleep(2)
    # Press and hold Ctrl
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('shift')
    pyautogui.keyDown('alt')
    pyautogui.keyDown('p')

    await asyncio.sleep(2)

    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('shift')
    pyautogui.keyUp('alt')
    pyautogui.keyUp('p')

def pixelDif(pixelA, pixelB):
    distance = 0
    distance += (pixelA[0] - pixelB[0]) ** 2
    distance += (pixelA[1] - pixelB[1]) ** 2
    distance += (pixelA[2] - pixelB[2]) ** 2
    distance = distance ** 0.5
    return distance

def findClosestColor(img, targetColor):
    diff = 255 * 3
    x = int(img.width / 2)
    closestY = 0
    #loop through the minigame's pixels vertically
    for y in range(0, img.height):
        currentColor = img.pixel(x, y)
        currentDiff = pixelDif(targetColor, currentColor)
        # if the current pixel is whiter, it's now the whitest known pixel
        if currentDiff < diff:
            diff = currentDiff
            color = currentColor
            closestY = y
    
    return {"colorFound": color, "diff": diff, "y": closestY}

# Mark upper bound of fishing indicator
print("Upper Left bound: ", end="")
keyboard.wait("p")
upperBound = pyautogui.position()
print(upperBound)

# Mark lower bound of fishing indicator
print("Lower Right bound: ", end="")
keyboard.wait("p")
lowerBound = pyautogui.position()
print(lowerBound)

#mark color of fishing icon
print("Blue RGB: ", end="")
keyboard.wait("p")
blueColor = pyautogui.pixel(pyautogui.position().x, pyautogui.position().y)
bluePosition = pyautogui.position()
print(blueColor)
print("Blue position:", bluePosition)

# Create bounding box
bounds = {"top": upperBound.y, "left": upperBound.x, "width": lowerBound.x - upperBound.x, "height": lowerBound.y - upperBound.y}
fishStartBounds = {"top": upperBound.y, "left": bluePosition.x, "width": 2, "height": lowerBound.y - upperBound.y}

#Capture screen
img = sct.grab(bounds)
'''dispImg = cvtColor(np.array(img), COLOR_RGBA2RGB)
imshow("sdfsadf", dispImg)
waitKey(0)'''


#find whitest pixel on the screen
whiteColor = findClosestColor(img, (255,255,255))["colorFound"]
print("White RGB: ", whiteColor)

#find greenest pixel on the screen
greenColor = findClosestColor(img, (104,221,2))["colorFound"]
print("Green RGB: ", greenColor)

# Wait for them to be ready
print("awaiting startup")
keyboard.wait("p")
print("started up")

# Fishing loop
fishCaught = 0
while True:
    # Cast rod
    asyncio.run(recast())

    # wait for a fish
    while True:
        #Capture screen
        img = sct.grab(fishStartBounds)
        #print(findClosestColor(img, blueColor)["colorFound"])

        if findClosestColor(img, blueColor)["diff"] <= activationThreshold:
            #print("found ti")
            break
        # Check for quit
        if keyboard.is_pressed('x'):
            exit()

    # reeling loop
    while True:
        # Check for quit
        if keyboard.is_pressed('x'):
            exit()
        
        #Check if fish is gone
        fishImg = sct.grab(fishStartBounds)
        if findClosestColor(fishImg, blueColor)["diff"] > activationThreshold:
            break

        # Check for quit
        if keyboard.is_pressed('x'):
            exit()

        
        img = sct.grab(bounds)
        #get position of white bar
        hookPosY = findClosestColor(img, whiteColor)["y"]

        #get position of green bar
        fishPosY = findClosestColor(img, greenColor)["y"]

        #if white bar too far from green bar, tap
        if (hookPosY - fishPosY) > reelingTolerance * img.height:
            pyautogui.press('[')
            print("reeling")
    fishCaught += 1
    print("fish caught: ", fishCaught)