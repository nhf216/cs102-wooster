from media import *
import time

def getLakeMichigan():
    return makePicture('/Users/nfox/Documents/CS102/Lake Michigan2 cropped.jpg')

def getBigPic():
    return makePicture('/Users/nfox/Dropbox/Nathan Fox Wooster Stuff/CS 102/Homework/right.JPG')

def getTracey():
    return makePicture('/Users/nfox/Documents/CS102/Pictures/TRACEY.jpg')

def getMoon():
    return makePicture('/Users/nfox/Documents/CS102/Pictures/moon-surface.jpg')

def halveRed1(pic):
    pic2 = duplicatePicture(pic)
    for pixel in getPixels(pic2):
        redval = getRed(pixel)
        setRed(pixel, redval // 2)
    return pic2

def halveRed3(pic):
    pic2 = duplicatePicture(pic)
    for y in range(getHeight(pic2)):
        for x in range(getWidth(pic2)):
            pix = getPixel(pic2, x, y)
            redval = getRed(pix)
            setRed(pix, redval // 2)
    return pic2

def halveRed2(pic):
    pic2 = duplicatePicture(pic)
    img = pic2.image
    w = getWidth(pic2)
    h = getHeight(pic2)
    #print("hello")
    #idx = 0
    for y in range(h):
        pixline = img.scanLine(y)
        pixarray = pixline.asarray(4*w)
        for x in range(w):
            redval = pixarray[4*x + 2]
            pixarray[4*x + 2] = redval // 2
    return pic2

def halveRed4(pic):
    pic2 = duplicatePicture(pic)
    img = pic2.image
    w = getWidth(pic2)
    h = getHeight(pic2)
    #print("hello")
    #idx = 0
    for x in range(w):
        for y in range(h):
            pixline = img.scanLine(y)
            pixarray = pixline.asarray(4*w)
            for x in range(w):
                redval = pixarray[4*x + 2]
                pixarray[4*x + 2] = redval // 2
    return pic2

def chromakeyAnimation(obj, scene):
    canvas = duplicatePicture(scene)
    show(canvas)
    row = 10
    
    for count in range(0, getWidth(scene)-getWidth(obj), 10):
        bg = cropPicture(scene, count, row, getWidth(obj), getHeight(obj))
        copyInto(chromakeyBlue(obj, bg), canvas, count, row)
        repaint(canvas)
        time.sleep(.1)
        # "erase" the object
        copyInto(scene, canvas, 0, 0)

#The second argument is the background
def chromakeyBlue(blueScreenImage, background):
    newPic = duplicatePicture(blueScreenImage)
    for y in range(getHeight(newPic)):
        for x in range(getWidth(newPic)):
            pixFG = getPixel(newPic, x, y)
            if getBlue(pixFG) > getRed(pixFG) + 15:
                #pass
                #We're in the background
                pixBG = getPixel(background, x, y)
                setColor(pixFG, getColor(pixBG))
    return newPic

def tracey_test():
    tracey = getTracey()
    moon = getMoon()
    return chromakeyBlue(tracey, moon)

def time_code(fun, inp):
    t0 = time.time()
    ret = fun(*inp)
    t1 = time.time()
    return [t1-t0, ret]