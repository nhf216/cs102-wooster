#ORIGINAL COMMENT from JES media.py BELOW
#
# Media Wrappers for "Introduction to Media Computation"
# Started: Mark Guzdial, 2 July 2002
# Revisions:
# 18 June 2003: (ellie)
#    Added (blocking)play(AtRate)InRange methods to Sound class
#      and global sound functions
#    Changed getSampleValue, setSampleValue to give the appearance
#      of 1-based indexing
#    Added getLeftSampleValue and getRightSampleValue to Sound class
# 14 May 2003: Fixed discrepancy between getMediaPath and setMediaFolder (AdamW)
# 8 Nov: Fixed getSamplingRate (MarkG)
# 1 Nov: Fixed printing pixel
# 31 Oct: Fixed pickAColor (MarkG)
# 30 Oct: Added raises, fixed error messages. Added repaint (MarkG)
# 10 Oct: Coerced value to integer in Sound.setSampleValue   (MarkR)
# 2 Oct:  Corrected calls in setSampleValueAt  (MarkG):
# 30 Aug: Made commands more consistent and add type-checking (MarkG)
# 2 Aug: Changed to getSampleValueAt and setSampleValueAt (MarkG)
# 1 Dec 2005: made max makeEmptySound size 600
#             made max makeEmptyPicture dimensions 10000x10000
#             fixed the off-by-one error in makeEmptyPicture
# 14 June 2007: (Pam Cutter, Kalamazoo College)
#              Fixed off-by-one error in copyInto.  Now allows copying
#		of same-sized picture, starting at top-left corner
#
# 6 July 2007: (Pam Cutter/Alyce Brady, Kalamazoo College)
#              Added flexibility to make an empty picture of a specified color.  Added
#                  additional, 3-parameter constructor to Picture and SimplePicture classes to support this.
#              Modified copyInto so that it will copy as much of the source picture as will fit
#              Added crop and copyInto methods to Picture class to support these.
#
# 8 July 2007: (Pam Cutter/ Alyce Brady, Kalamazoo College)
#              Changed all  _class_ comparisons to use isinstance instead so that
#                   they will work with subclasses as well (e.g., subclasses of Picture
#                   are still pictures)
#              Added getSampleValue, setSampleValue functions with same functionality, but
#                   more intuitive names, as the getSample, setSample function, respectively.
#              Added global getDuration function to return the number of seconds in a sound
#
# 10 July 2007: (Pam Cutter, Kalamazoo College)
#              Added a global duplicateSound function
# 11 July 2007: (Pam Cutter, Kalamazoo College)
#              Added global addTextWithStyle function to allow users to add text to images
#                  with different font styles.
#
# 17 July 2007: (Pam Cutter, Kalamazoo College)
#              Added 7global addOval, addOvalFilled, addArc and addArcFilled functions.
#              Added global getNumSamples function as more meaningful name for getLength of a sound.
#
# 19 July 2007: (Pam Cutter, Kalamazoo College)
#              Modified the SoundExplorer class to be consistent with sounds in JES
#                  starting at sample index 1.
#              Modified the PictueExplorer class to initially show color values from
#			 pixel 1,1, instead of 0,0.
#
# 1 Nov 2007: Added __add__ and __sub__ to Color class (BrianO)
# 29 Apr 2008: Changed makeEmptySound to take an integer number of samples
#	       Added optional second argument to makeEmptySound for sampleRate
# 6 June 2008: Added a check for forward slash in a directory path in makeMovieFromInitialFile
#		This check should work with os.altsep, but it does not work with Jython 2.2.
#		This should be fixed again at a later date.
# 27 June 2008: Added optional input to setMediaFolder and setMediaPath.
#		Added showMediaFolder and showMediaPath methods.
# 11 July 2007: Removed showMediaFolder and showMediaPath for no-arg version of getMediaPath/getMediaFolder.
#		Added generic explore method. 
# 15 July 2007: Added no-arg option for setLibPath

# TODO:
## Fix HSV/RGB conversions -- getting a divide by zero error when max=min

import sys
import os
import math
import tempfile
import numbers
import threading
import collections
import numbers
import time
#import traceback
#import user

#Don't Use PIL for images
#except one case
import PIL
#import PIL.ImageTk as ImageTk

#from os import system
#from platform import system as platform

#Use Qt for everything
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtMultimedia import * #This is for sound/video (video later)
import wave #This is for reading sound file metadata
# Create an PyQT4 application object.
#If we're running in Canopy, there already is one
root = QApplication.instance()
if root is None:
    #We're not running in Canopy
    #Need to launch a new application
    root = QApplication(sys.argv)
#import tkinter
#from tkinter import filedialog
#from tkinter.colorchooser import askcolor
#import threading
#import org.python.core.PyString as String
#root = tkinter.Tk()
#root.withdraw()

#roots = []

# Support a media shortcut

#mediaFolder = JESConfig.getMediaPath()
#if ( mediaFolder == "" ):
mediaFolder = os.getcwd() + os.sep
    
# Store last pickAFile() opening

_lastFilePath = ""

true = 1
false = 0

#List of things to keep around
keepAround = []

#Check supported image types
suppTypes = QImageReader.supportedImageFormats()
supportedImageTypes = set([])
for typ in suppTypes:
    supportedImageTypes.add(str(typ)[2:-1])

#Is the type of this file supported?
def isSupportedImageFormat(fname):
    inddot = fname.rfind(".")
    if inddot == -1:
        tstr = fname
    else:
        tstr = fname[inddot+1:]
    return tstr.lower() in supportedImageTypes

#Error reporting structure
#Lets us refactor error reporting by changing only one line of code!
def reportErrorToUser(errType, msg):
    #print(msg)
    raise errType(msg)

#Shortcut for ValueError reporting
def repValError(msg):
    reportErrorToUser(ValueError, msg)

#Done
def setMediaPath(file=None):
    global mediaFolder
    if(file == None):
        mediaFolder = pickAFolder()
    else:	
        mediaFolder = file
    #mediaFolder = getMediaPath()
    return mediaFolder

def getMediaPath( filename = "" ):
    return mediaFolder + os.sep + filename
    #return FileChooser.getMediaPath( filename )

#Done
def setMediaFolder(file=None):
    return setMediaPath(file)

#Done
def setTestMediaFolder():
    global mediaFolder
    mediaFolder = os.getcwd() + os.sep

#Done
def getMediaFolder( filename = "" ):
    return getMediaPath(filename)

#Done
def showMediaFolder():
    global mediaFolder
    print("The media path is currently: ",mediaFolder)

#Done
def getShortPath(filename):
    dirs = filename.split(os.sep)
    if len(dirs) < 1:
        return "."
    elif len(dirs) == 1:
        return dirs[0]
    else:
        return (dirs[len(dirs) - 2] + os.sep + dirs[len(dirs) - 1])

#Done
def setLibPath(directory=None):
    if(directory == None):
        directory = pickAFolder()
    if(os.path.isdir(directory)):
    	sys.path.append(directory)
    else:
        #print("Note: There is no directory at ",directory)
        #raise ValueError
        repValError("Note: There is no directory at "+str(directory))
    return directory

#This is not actually a media function
#Instead, it prints lists better
def betterPrint(val):
    print(recursive_str(val))

#Recursively call str on all components of val
#If val is not a sequence type, it's just str
#No need to call directly
#This is called by betterPrint
def recursive_str(val):
    if isinstance(val, collections.abc.Sequence) and not isinstance(val, str):
        #It's a sequence; recurse!
        return str(type(val)(map(str, val)))
    else:
        return str(val)

#Like time.sleep, but continues to play sounds
def sleep(secs):
    cur_time = time.time()
    while time.time() - cur_time < secs:
        QApplication.processEvents()

#Sample class
#A Sample knows its value, its position, and the Sound it's from
class Sample:
    #Constructor
    #Takes a Sound and a position
    #Finds the value
    def __init__(self, sound, pos):
        self.sound = sound
        self.pos = pos
        self.value = sound.getSampleValue(pos)
    
    #Convert to a printable string
    def __str__(self):
        return 'Sample at ' + str(self.pos) + ' with value ' + str(self.value)
    
    #Get the Sample's value
    def getValue(self):
        return self.value
    
    #Set the Sample's value
    def setValue(self, newVal):
        #Update the Sound
        self.sound.setSampleValueRaw(self.pos, newVal)
        #Update the Sample's internal value
        self.value = newVal
    
    #Get the Sound object
    def getSound(self):
        return self.sound
    
    #Get the position
    def getIndex(self):
        return self.pos

#Sound class
#Only supports WAV for now
class Sound:
    #Constants
    SAMPLE_RATE = 22050
    NUM_CHANNELS = 1
    SAMPLE_SIZE = 16
    
    #Default audio output device
    AUDIO_DEVICE = QAudioDeviceInfo.defaultOutputDevice()
    
    #Constructor
    def __init__(self, arg1, arg2 = None):
        #arg1 can be a filename, a number of samples, or a Sound
        #arg2, if provided, is a sample rate
        #super().__init__()
        if isinstance(arg1, Sound):
            #arg1 is a Sound. Copy it.
            self.fileName = None #It doesn't duplicate this part
            # #Instead, use a temporary file, which gets changed
            # #if they save the sound
            # self.tempfile = tempfile.mkstemp(suffix = '.wav')
            #self.file = QFile(arg1.fileName)
            self.numSamples = arg1.numSamples
            self.sampleRate = arg1.sampleRate
            self.sampleSize = arg1.sampleSize
            self.numChannels = arg1.numChannels
            #Copy the raw data
            self.data = bytearray(arg1.data)
            #self.writeFile(self.tempfile[1])
            #self.file = QFile(self.tempfile[1])
        elif isinstance(arg1, str):
            #arg1 is a file name
            self.fileName = arg1
            #self.file = QFile(self.fileName)
            #Get the metadata
            wav = wave.open(self.fileName)
            self.numSamples = wav.getnframes()
            self.sampleRate = wav.getframerate()
            self.sampleSize = wav.getsampwidth() * 8
            self.numChannels = wav.getnchannels()
            #Get the raw data
            self.data = bytearray(wav.readframes(self.numSamples))
            wav.close()
        elif isinstance(arg1, int):
            #arg1 is a number of samples
            self.numSamples = arg1
            # #Apparently the number of samples needs to be even or everything breaks?
            # if self.numSamples % 2 == 1:
            #     self.numSamples += 1
            if arg2 is None:
                self.sampleRate = Sound.SAMPLE_RATE
            else:
                self.sampleRate = arg2
            self.fileName = None
            self.numChannels = Sound.NUM_CHANNELS
            self.sampleSize = Sound.SAMPLE_SIZE
            #Blank data
            self.data = bytearray([0 for i in range(self.numSamples * self.sampleSize)])
            #self.file = None
            # #Use a temporary file, which gets changed
            # #if they save the sound
            # #TODO instead just send the sound data directly
            # self.tempfile = tempfile.mkstemp(suffix = '.wav')
            
        self.setUpFormat()
        #Tuples (QBuffer, QByteArray, QAudioOutput) used for playing multiple instances
        self.buffs = []
        #Cleanup lock
        self.cleanupLock = threading.Lock()
        #self.isPlaying = False
        #Set up "Samples" representation of data
        #This is clunky but "necessary" for efficiency of JES operations
        self.setUpSampleObjects()
        # #For blocking play
        # self.blockEvent = None
    
    def setUpFormat(self):
        #Create the audio format
        self.format = QAudioFormat()
        self.format.setCodec('audio/pcm')
        self.format.setSampleRate(self.sampleRate)
        self.format.setSampleSize(self.sampleSize)
        self.format.setChannelCount(self.numChannels)
        #This is a WAV thing
        if self.sampleSize == 8:
            self.format.setSampleType(QAudioFormat.UnSignedInt)
        elif self.sampleSize == 16:
            self.format.setSampleType(QAudioFormat.SignedInt)
        self.format.setByteOrder(QAudioFormat.LittleEndian)
        #print(self.sampleRate, self.sampleSize, self.numChannels)
    
    #Convert to string
    def __str__(self):
        ret = "Sound"
        fileName = self.fileName

        #if there is a file name then add that to the output
        if fileName is not None:
            ret = ret + " file: " + fileName

        #add the length in frames
        ret = ret + " number of samples: " + str(self.getLengthInFrames())

        return ret
    
    #Number of sample
    def getLengthInFrames(self):
        return self.numSamples
    
    #Get a "slice" of the raw data
    def getDataSlice(self, start, stop):
        return self.data[start * (self.sampleSize//8):stop * (self.sampleSize//8)]
    
    #Play the sound
    #Do nothing if it's already playing
    #Play from start to stop (default is the whole sound)
    def play(self, start=0, stop=0):
        #if not self.isPlaying:
        
        ##Clean up zombie processes, if somehow there are some
        #self.cleanUpResources()
        
        #Make start and stop both positive
        if start < 0:
            newStart = self.numSamples + start
        else:
            newStart = start
        if stop <= 0:
            newStop = self.numSamples + stop
        else:
            newStop = stop
                
        qba = QByteArray(self.getDataSlice(newStart, newStop))
        buff = QBuffer(qba)
        audioOutput = QAudioOutput(Sound.AUDIO_DEVICE, self.format)
        self.buffs.append((buff, qba, audioOutput))
        #print("Still alive")
        #worked = self.file.open(QIODevice.ReadOnly)
        #worked = self.buff.open(QIODevice.ReadOnly)
        worked = self.buffs[-1][0].open(QIODevice.ReadOnly)
        if not worked:
            #Clean up the corrupted buffer
            del self.buffs[-1]
            raise IOError("Failed to open sound data stream")
        #print(worked)
        
        #Is it supported?
        if not Sound.AUDIO_DEVICE.isFormatSupported(self.format):
            #Clean up the corrupted buffer
            del self.buffs[-1]
            raise RuntimeError("Sound format not supported")
    
        #self.audioOutput = QAudioOutput(Sound.AUDIO_DEVICE, self.format)
        
        #worked = QObject.connect(self.audioOutput, SIGNAL('stateChanged(QAudio.State)'), self, SLOT('finishedPlaying()'))
        #worked = QObject.connect(self.audioOutput, SIGNAL('stateChanged'), self, SLOT('finishedPlaying(int)'))
        #worked = self.audioOutput.stateChanged.connect(self.finishedPlaying)
        #self.audioOutput.stateChanged.connect(self.finishedPlaying)
        self.buffs[-1][-1].stateChanged.connect(self.finishedPlaying)
        #if not worked:
        #    raise RuntimeError("Signal binding failed")
        #connect(audioOutput,SIGNAL(stateChanged(QAudio.State)),SLOT(finishedPlaying(QAudio.State)))
        #self.audioOutput.start(self.file)
        #self.audioOutput.start(self.buffs[-1][0])
        self.buffs[-1][-1].start(self.buffs[-1][0])
        QApplication.processEvents()
            #self.isPlaying = True
        #return audioOutput
    
    #Plays a sound, and blocks until done
    def blockingPlay(self, start=0, stop=0):
        #thrd = threading.Thread(target = self.play())
        #thrd.start()
        #self.blockingEvent = threading.Event()
        self.play(start, stop)
        # cv = threading.Condition()
        # cv.acquire()
        # while len(self.buffs) > 0:
        #     cv.wait(0.01)
        # #cv.wait_for(lambda: len(self.buffs) == 0)
        # cv.release()
        while len(self.buffs) > 0:
            #Hang around here
            QApplication.processEvents() #YES!!!!!
        #self.blockingEvent.wait()
        #self.blockingEvent = None
        #thrd.join()
        #time.sleep(2)
    
    #Is the sound currently playing?
    def isPlaying(self):
        return len(self.buffs) > 0
    
    #Stop the sound from playing (however many times it's currently playing)
    def stopPlaying(self):
        #Acquire the cleanup lock
        self.cleanupLock.acquire()
        try:
            #Clean up ALL instances of playing the sound
            buffs = list(self.buffs)
            for i in range(len(buffs)-1, -1, -1):
                self.buffs[i][-1].stop()
                self.buffs[i][0].close()
                del self.buffs[i]
        finally:
            #Release the lock
            self.cleanupLock.release()
    
    #Go through the list of playing sound resources and destroy
    #the ones that have finished playing
    def cleanUpResources(self):
        #Acquire lock; don't want multiple threads in here at once
        self.cleanupLock.acquire()
        try:
            #Clean up finished instances of playing the sound
            buffs = list(self.buffs)
            for i in range(len(buffs)-1, -1, -1):
                if buffs[i][0].atEnd():
                    #This one's done
                    self.buffs[i][0].close()
                    self.buffs[i][-1].stop()
                    del self.buffs[i]
            # if len(self.buffs) == 0 and self.blockingEvent is not None:
            #     #Wake up the block!
            #     self.blockingEvent.set()
        finally:
            QApplication.processEvents()
            #Release the lock
            self.cleanupLock.release()
    
    #It was working with files, but failed with buffers (triggered too soon)
    #Workaround is to manually call the clean up method
    def finishedPlaying(self, state):
        #print("yo", state)
        #state = self.audioOutput.state()
        #Is it finished?
        if state == QAudio.IdleState:
            # self.audioOutput.stop()
            # #self.file.close()
            # self.buff.close()
            # self.isPlaying = False
            # print("It's done!")
            self.cleanUpResources()
    
    #Write this sound to the given
    def writeToFile(self, fil):
        fd = wave.open(fil, 'wb')
        fd.setnchannels(self.numChannels)
        fd.setnframes(self.numSamples)
        fd.setframerate(self.sampleRate)
        fd.setsampwidth(self.sampleSize // 8)
        fd.writeframes(self.data)
        fd.close()
    
    #Represent the sound as an image of the given dimensions
    #Used by Sound Explorer
    def getImageRep(self, width, height):
        #Find the height in the image of a given sample value
        def findY(sval):
            if self.sampleSize == 8:
                return int((-height/256)*sval + height-1)
            elif self.sampleSize == 16:
                return int((-height/65536)*sval + height/2)
        
        #Create an empty black picture
        ret = makeEmptyPicture(width, height, black)
        
        #Add the waveform, adjusted for proper step size
        lastY = findY(getSampleValueAt(self, 0))
        stepSize = max(self.numSamples // width, 1)
        for i in range(stepSize, self.numSamples, stepSize):
            curY = findY(getSampleValueAt(self, i))
            addLine(ret, i//stepSize-1, lastY, i//stepSize, curY, white)
            lastY = curY
        
        #Add the zero line
        if self.sampleSize == 8:
            addLine(ret, 0, height-1, width-1, height-1, cyan)
        elif self.sampleSize == 16:
            addLine(ret, 0, height//2, width-1, height//2, cyan)
        
        return ret
    
    def setUpSampleObjects(self):
        ss = self.sampleSize // 8
        if len(self.data) % ss != 0:
            #The samples are corrupted
            raise ValueError("You have half a sample at the end. Not sure why.")
        self.samples = []
        #Convert the binary stream to integers by sample size
        #Make sure to use two's complement
        for i in range(self.numSamples):
            self.samples.append(Sample(self, i))
    
    #Get the ith sample value
    def getSampleValue(self, i):
        if self.sampleSize == 8:
            #This is easy
            val = int(self.data[i])
        elif self.sampleSize == 16:
            #This is harder
            val = int.from_bytes(self.data[2*i:2*i+2], 'little', signed=True)
            # val = self.data[2*i] * 256 + self.data[2*i+1]
            # if val >= 32768:
            #     #Need to make it be negative
            #     val -= 65536
        return val
    
    def getSample(self, i):
        return self.samples[i]
    
    #Get all the samples, as a list
    #DO NOT PRINT THIS!!!
    def getSamples(self):
        # ss = self.sampleSize // 8
        # if len(self.data) % ss != 0:
        #     #The samples are corrupted
        #     raise ValueError("You have half a sample at the end. Not sure why.")
        # ret = []
        # #Convert the binary stream to integers by sample size
        # #Make sure to use two's complement
        # for i in range(self.numSamples):
        #     ret.append(self.getSample(i))
        # return ret
        return self.samples
    
    #Set a sample value
    #DOES change the Sample objects
    def setSampleValue(self, pos, value):
        #Clipping
        val = value
        if val < -32768:
            val = -32768
        elif val > 32767:
            val = 32767
        self.samples[pos].setValue(val)
    
    #Set the value of the sample at position pos to value
    #DO NOT CALL THIS IF YOU ARE USING Sample OBJECTS!
    #This is called by Sample to update the Sound
    #It will desync the Sample objects if you call it directly
    def setSampleValueRaw(self, pos, value):
        if self.sampleSize == 8:
            #This is easy
            self.data[pos] = value
        elif self.sampleSize == 16:
            #This is harder
            # #First, un-two's-complement it
            # val = value
            # if val < 0:
            #     val = val + 65536
            # #Then, extract the bytes
            # hiByte = val // 256
            # loByte = val % 256
            # #Finally, set the data
            # self.data[2*pos] = hiByte
            # self.data[2*pos+1] = loByte
            val = value.to_bytes(2, 'little', signed=True)
            self.data[2*pos:2*pos+2]  = val
    
    #What is the sample size, in bits?
    def getSampleSize(self):
        return self.sampleSize
    
    #What is the sampling rate?
    def getSamplingRate(self):
        return self.sampleRate
    
##
## Global sound functions
##
#Done
def makeSound(filename):
    global mediaFolder
    if not os.path.isabs(filename):
        filename = mediaFolder + filename
    if not os.path.isfile(filename):
        #print("There is no file at "+filename)
        #raise ValueError
        repValError("There is no file at "+filename)
    return Sound(filename)

# MMO (1 Dec 2005): capped size of sound to 600
# Brian O (29 Apr 2008): changed first argument to be number of samples, added optional 2nd argument of sampling rate
#Done
def makeEmptySound(numSamples, samplingRate = Sound.SAMPLE_RATE):
    if numSamples <= 0 or samplingRate <= 0:
        #print("makeEmptySound(numSamples[, samplingRate]): numSamples and samplingRate must each be greater than 0")
        #raise ValueError
        repValError("makeEmptySound(numSamples[, samplingRate]): numSamples and samplingRate must each be greater than 0")
    if (numSamples/samplingRate) > 600:
        #print("makeEmptySound(numSamples[, samplingRate]): Created sound must be less than 600 seconds")
        #raise ValueError
        repValError("makeEmptySound(numSamples[, samplingRate]): Created sound must be less than 600 seconds") 
    if not isinstance(numSamples, int):
        repValError("makeEmptySound(numSamples[, samplingRate]): numSamples must be an integer")  
    if not isinstance(samplingRate, int):
        repValError("makeEmptySound(numSamples[, samplingRate]): samplingRate must be an integer")  
    return Sound(numSamples, samplingRate)

#    if size > 600:
#        #print "makeEmptySound(size): size must be 600 seconds or less"
#        #raise ValueError
#        repValError("makeEmptySound(size): size must be 600 seconds or less")
#    return Sound(size * Sound.SAMPLE_RATE)

# Brian O (5 May 2008): Added method for creating sound by duration
#Done
def makeEmptySoundBySeconds(seconds, samplingRate = Sound.SAMPLE_RATE):
    if seconds <= 0 or samplingRate <= 0:
        #print("makeEmptySoundBySeconds(numSamples[, samplingRate]): numSamples and samplingRate must each be greater than 0")
        #raise ValueError
        repValError("makeEmptySoundBySeconds(numSamples[, samplingRate]): numSamples and samplingRate must each be greater than 0")
    if seconds > 600:
        #print("makeEmptySoundBySeconds(numSamples[, samplingRate]): Created sound must be less than 600 seconds")
        #raise ValueError
        repValError("makeEmptySoundBySeconds(numSamples[, samplingRate]): Created sound must be less than 600 seconds")
    return Sound(int(seconds * samplingRate), samplingRate)

# PamC: Added this function to duplicate a sound
#Done
def duplicateSound(sound):
    if not isinstance(sound, Sound):
        #print("duplicateSound(sound): Input is not a sound")
        #raise ValueError
        repValError("duplicateSound(sound): Input is not a sound")
    return Sound(sound)

#Done
def getSamples(sound):
    if not isinstance(sound, Sound):
        #print("getSamples(sound): Input is not a sound")
        #raise ValueError
        repValError("getSamples(sound): Input is not a sound")
    return sound.getSamples()

#Done
def play(sound):
    if not isinstance(sound,Sound):
        #print "play(sound): Input is not a sound"
        #raise ValueError
        repValError("play(sound): Input is not a sound")
    sound.play()

#DONE!!!!!!!!!
#(Note: "blocking main thread" includes infinite loop)
def blockingPlay(sound):
    if not isinstance(sound,Sound):
        #print "blockingPlay(sound): Input is not a sound"
        #raise ValueError
        repValError("blockingPlay(sound): Input is not a sound")
    sound.blockingPlay()

# Buck Scharfnorth (27 May 2008): Added method for stopping play of a sound
#Done
def stopPlaying(sound):
    if not isinstance(sound,Sound):
        #print "stopPlaying(sound): Input is not a sound"
        #raise ValueError
        repValError("stopPlaying(sound): Input is not a sound")
    sound.stopPlaying()

# def playAtRate(sound,rate):
#     #if not isinstance(sound, Sound):
#     #    #print "playAtRate(sound,rate): First input is not a sound"
#     #    #raise ValueError
#     #    repValError("playAtRate(sound,rate): First input is not a sound")
#     ## sound.playAtRate(rate)
#     #sound.playAtRateDur(rate,sound.getLength())
#     pass #TODO
# 
# def playAtRateDur(sound,rate,dur):
#     #if not isinstance(sound,Sound):
#     #    #print "playAtRateDur(sound,rate,dur): First input is not a sound"
#     #    #raise ValueError
#     #    repValError("playAtRateDur(sound,rate,dur): First input is not a sound")
#     #sound.playAtRateDur(rate,dur)
#     pass #TODO

#20June03 new functionality in JavaSound (ellie)
def playInRange(sound,start,stop):
    if not isinstance(sound, Sound):
        repValError("playInRange(sound,start,stop): First input is not a sound")
    elif not isinstance(start, int):
        repValError("playInRange(sound,start,stop): Second input is not an integer")
    elif start < 0:
        repValError("playInRange(sound,start,stop): Second input cannot be negative")
    elif start >= getNumSamples(sound):
        repValError("playInRange(sound,start,stop): Second input cannot be greater than the length of the sound, which is " + getNumSamples(sound))
    elif not isinstance(stop, int):
        repValError("playInRange(sound,start,stop): Third input is not an integer")
    elif stop < 0:
        repValError("playInRange(sound,start,stop): Third input cannot be negative")
    elif stop >= getNumSamples(sound):
        repValError("playInRange(sound,start,stop): Third input cannot be greater than the length of the sound, which is " + getNumSamples(sound))
    elif start > stop:
        repValError("playInRange(sound,start,stop): Second input cannot exceed third input")
    # sound.playInRange(start,stop)
    #sound.playAtRateInRange(1,start-Sound._SoundIndexOffset,stop-Sound._SoundIndexOffset)
    sound.play(start, stop)

# #20June03 new functionality in JavaSound (ellie)
#Done
def blockingPlayInRange(sound,start,stop):
    if not isinstance(sound, Sound):
        repValError("playInRange(sound,start,stop): First input is not a sound")
    elif not isinstance(start, int):
        repValError("playInRange(sound,start,stop): Second input is not an integer")
    elif start < 0:
        repValError("playInRange(sound,start,stop): Second input cannot be negative")
    elif start >= getNumSamples(sound):
        repValError("playInRange(sound,start,stop): Second input cannot be greater than the length of the sound, which is " + getNumSamples(sound))
    elif not isinstance(stop, int):
        repValError("playInRange(sound,start,stop): Third input is not an integer")
    elif stop < 0:
        repValError("playInRange(sound,start,stop): Third input cannot be negative")
    elif stop >= getNumSamples(sound):
        repValError("playInRange(sound,start,stop): Third input cannot be greater than the length of the sound, which is " + getNumSamples(sound))
    elif start > stop:
        repValError("playInRange(sound,start,stop): Second input cannot exceed third input")
    sound.blockingPlay(start, stop)
# 
# #20June03 new functionality in JavaSound (ellie)
# def playAtRateInRange(sound,rate,start,stop):
#         #if not isinstance(sound,Sound):
#         #        #print "playAtRateInRAnge(sound,rate,start,stop): First input is not a sound"
#         #        #raise ValueError
#         #        repValError("playAtRateInRAnge(sound,rate,start,stop): First input is not a sound")
#         #sound.playAtRateInRange(rate,start - Sound._SoundIndexOffset,stop - Sound._SoundIndexOffset)
#         pass #TODO
# 
# #20June03 new functionality in JavaSound (ellie)
# def blockingPlayAtRateInRange(sound,rate,start,stop):
#         #if not isinstance(sound, Sound):
#         #        #print "blockingPlayAtRateInRange(sound,rate,start,stop): First input is not a sound"
#         #        #raise ValueError
#         #        repValError("blockingPlayAtRateInRange(sound,rate,start,stop): First input is not a sound")
#         #sound.blockingPlayAtRateInRange(rate, start - Sound._SoundIndexOffset,stop - Sound._SoundIndexOffset)
#         pass #TODO

#New
#Is the sound currently playing?
def isPlaying(sound):
    if not isinstance(sound, Sound):
        #print "getSamplingRate(sound): Input is not a sound"
        #raise ValueError
        repValError("isPlaying(sound): Input is not a sound")
    return sound.isPlaying()

#Done
def getSamplingRate(sound):
    if not isinstance(sound, Sound):
        #print "getSamplingRate(sound): Input is not a sound"
        #raise ValueError
        repValError("getSamplingRate(sound): Input is not a sound")
    return sound.getSamplingRate()

#Done
def setSampleValueAt(sound,index,value):
    if not isinstance(sound, Sound):
        repValError("setSampleValueAt(sound,index,value): First input is not a sound")
    if index < 0:
        repValError("You asked for the sample at index: " + str( index ) + ".  This number is less than " + str(0) + ".  Please try" + " again using an index in the range [" + str(0) + "," + str ( getLength( sound ) - 1 ) + "].")
    if index > getLength(sound) - 1:
        repValError("You are trying to access the sample at index: " + str( index ) + ", but the last valid index is at " + str( getLength( sound ) - 1 ))
    sound.setSampleValue(index, int(value))

#Done
def getSampleValueAt(sound,index):
    if not isinstance(sound,Sound):
        repValError("getSampleValueAt(sound,index): First input is not a sound")
    if index < 0:
        repValError("You asked for the sample at index: " + str( index ) + ".  This number is less than 0.  Please try" + " again using an index in the range [" + str(0) + "," + str ( getLength( sound ) - 1) + "].")
    if index > getLength(sound) - 1:
        repValError("You are trying to access the sample at index: " + str( index ) + ", but the last valid index is at " + str( getLength( sound ) - 1 ))
    return sound.getSampleValue(index)

#Done
def getSampleObjectAt(sound,index):
    if not isinstance(sound, Sound):
        repValError("getSampleObjectAt(sound,index): First input is not a sound")
    if index < 0:
        repValError("You asked for the sample at index: " + str( index ) + ".  This number is less than " + str(0) + ".  Please try" + " again using an index in the range [" + str(0) + "," + str ( getLength( sound ) - 1 ) + "].")
    if index > getLength(sound) - 1:
        repValError("You are trying to access the sample at index: " + str( index ) + ", but the last valid index is at " + str( getLength( sound ) - 1 ))
    return sound.getSample(index)

#New
#Get sample size, in bits
#Usually would be 16, but this code supports 8 as well
def getSampleSize(sound):
    if not isinstance(sound, Sound):
        repValError("getSampleSize(sound): Input is not a sound")
    return sound.getSampleSize()

#Done
def setSample(sample, value):
    if not isinstance(sample,Sample):
        repValError("setSample(sample,value): First input is not a Sample")
    ss = getSampleSize(getSound(sample))
    if ss == 8:
        vmax = 255
        vmin = 0
    elif ss == 16:
        vmax = 32767
        vmin = -32768
    #Clip
    if value > vmax:
        value = vmax
    elif value < vmin:
        value = vmin
    # Need to coerce value to integer
    sample.setValue( int(value) )

# PamC: Added this function to be a better name than setSample
#Done
def setSampleValue(sample, value):
  setSample(sample, value)

#Done
def getSample(sample):
    if not isinstance(sample, Sample):
        repValError("getSample(sample): Input is not a Sample")
    return sample.getValue()

# PamC: Added this to be a better name for getSample
#Done
def getSampleValue(sample):
    return getSample(sample)

#New
def getSampleIndex(sample):
    if not isinstance(sample, Sample):
        repValError("getSampleIndex(sample): Input is not a Sample")
    return sample.getIndex()

#Done
def getSound(sample):
    if not isinstance(sample,Sample):
        repValError("getSound(sample): Input is not a Sample")
    return sample.getSound()

#Done
def getLength(sound):
    if not isinstance(sound, Sound):
        repValError("getLength(sound): Input is not a Sound")
    return sound.getLengthInFrames()

# PamC: Added this function as a more meaningful name for getLength
#Done
def getNumSamples(sound):
    return getLength(sound)

# PamC: Added this function to return the number of seconds
# in a sound
#Done
def getDuration(sound):
    if not isinstance(sound, Sound):
        repValError("getDuration(sound): Input is not a Sound")
    return getLength(sound) / getSamplingRate(sound)

#New
#Frequency: Hertz
#Amplitude: Max/min of the sine wave (should be between 0 and 32767)
#Dur: Length, in seconds
def pureTone(freq, amp, dur):
    if not isinstance(freq, numbers.Number):
        repValError("pureTone(freq, amp, dur): freq must be a number")
    elif freq < 0:
        repValError("pureTone(freq, amp, dur): freq must be nonnegative")
    if not isinstance(amp, numbers.Number):
        repValError("pureTone(freq, amp, dur): amp must be a number")
    elif amp < 0 or amp > 32767:
        repValError("pureTone(freq, amp, dur): amp must be between 0 and 32767 (inclusive)")
    if not isinstance(dur, numbers.Number):
        repValError("pureTone(freq, amp, dur): dur must be a number")
    elif dur < 0:
        repValError("pureTone(freq, amp, dur): dur must be nonnegative")
    def getVal(i):
        return int(amp*math.sin((freq*2*math.pi)*i/Sound.SAMPLE_RATE))
        
    sound = makeEmptySoundBySeconds(dur)
    for i in range(int(dur * Sound.SAMPLE_RATE)):
        setSample(getSampleObjectAt(sound, i), getVal(i))
    return sound

#Done
def writeSoundTo(sound,filename):
    global mediaFolder
    if not os.path.isabs(filename):
        filename = mediaFolder + filename
    if not isinstance(sound, Sound):
        repValError("writeSoundTo(sound,filename): First input is not a Sound")
    sound.writeToFile(filename)

#New
def saveSound(sound):
    fil = pickASaveFile()
    #Try to get a format
    #If no format given, yell at the user
    # dotloc = fil.rfind(".")
    # if dotloc == -1:
    #     repValError("Error: No file extension provided")
    #     #raise ValueError("Error: No file extension provided")
    if len(fil) < 4 or (fil[-4:] != '.wav' and fil[-4:] != '.WAV'):
        repValError("Error: Must specify .wav extension")
    writeSoundTo(sound, fil)

##
# Globals for styled text
##
#Done
def makeStyle(fontName,emph,size):
    ret = QFont()
    #ret.setStyleName(fontName)
    ret.setPointSize(size)
    #if emph == sansSerif or emph == serif or emph == mono:
    #    ret.setStyleHint(emph)
    ret.setStyleHint(fontName)
    if emph == italic:
        ret.setStyle(emph)
    elif emph == bold or emph == plain:
        ret.setWeight(emph)
    return ret

sansSerif = QFont.SansSerif
serif = QFont.Serif
mono = QFont.Monospace
italic = QFont.StyleItalic
bold = QFont.Bold
plain = QFont.Normal

##
## Global color functions
##

# Buck Scharfnorth (28 May 2008): if bool == 1 colors will be (value % 256)
# 				  if bool == 0 colors will be truncated to 0 or 255
# updated (13 May 2009): 
# THIS GLOBAL FUNCTION CHANGES JES SETTINGS - this value overwrites
# the value in the JES options menu.
def setColorWrapAround(bool):
    #JESConfig.getInstance().setSessionWrapAround( bool )
    pass #TODO

# Buck Scharfnorth (28 May 2008): Gets the current ColorWrapAround Value
def getColorWrapAround():
    #return JESConfig.getInstance().getSessionWrapAround()
    pass #TODO

# Buck Scharfnorth (28 May 2008): Modified to no longer assume the value is 0-255
#Done
def _checkPixel(raw):
    value = int(raw)
    if getColorWrapAround():
        value = (value % 256)
    else:
        if value < 0:
            value = 0
        if value > 255:
            value = 255
    return value

# this class is solely for the purpose of
# making makeLighter makeDarker work.
# both of these functions destructively modify a color
# and a color in java is a constant value so we have to put
# this python interface here
#
# Buck Scharfnorth (28 May 2008): Modified to no longer assume the value is 0-255
# and the gray Color constructor to allow only 1 color parameter (will take 2, but ignores the second)
class Color:
    def __init__(self,r,g=None,b=None):
        if b == None:
            #In this case, r should be a tuple or Color or QColor
            if isinstance(r, Color):
                self.r = r.getRed()
                self.g = r.getGreen()
                self.b = r.getBlue()
            elif isinstance(r, QColor):
                self.r = r.red()
                self.g = r.green()
                self.b = r.blue()
            elif isinstance(r, int):
                #This case is necessary because of how QImage.pixel() works
                cl = QColor(r)
                self.r = cl.red()
                self.g = cl.green()
                self.b = cl.blue()
            else:
                self.r = r[0]
                self.g = r[1]
                self.b = r[2]
            #if isinstance( r, awt.Color ) or isinstance( r, Color ):
            #    self.color = r
            #else:
            #    val = _checkPixel(r)
            #    self.color = awt.Color( val, val, val )
        else:
            # self.color = awt.Color(r,g,b)
            #self.color = awt.Color( _checkPixel(r), _checkPixel(g), _checkPixel(b) )
            if not isinstance(r, numbers.Number):
                repValError("First color component (red) not a number")
                #raise ValueError
            if not isinstance(g, numbers.Number):
                repValError("Second color component (green) not a number")
                #raise ValueError
            if not isinstance(b, numbers.Number):
                repValError("Third color component (blue) not a number")
                #raise ValueError
            self.r = r
            self.g = g
            self.b = b
        #Fix out-of-bounds
        self.validateColor()
    
    #If any component is not in range 0 to 255, fix that
    #If any component is not an integer, fix that
    def validateColor(self):
        if self.r < 0:
            self.r = 0
        elif self.r > 255:
            self.r = 255
        if self.g < 0:
            self.g = 0
        elif self.g > 255:
            self.g = 255
        if self.b < 0:
            self.b = 0
        elif self.b > 255:
            self.b = 255
        if not isinstance(self.r, int):
            self.r = int(self.r)
        if not isinstance(self.g, int):
            self.g = int(self.g)
        if not isinstance(self.b, int):
            self.b = int(self.b)

    def __str__(self):
        return "color r="+str(self.getRed())+" g="+str(self.getGreen())+" b="+str(self.getBlue())

    def __repr__(self):
        return "Color("+str(self.getRed())+", "+str(self.getGreen())+", "+str(self.getBlue())+")"

    def __eq__(self,newcolor):
        return ((self.getRed() == newcolor.getRed()) and (self.getGreen() == newcolor.getGreen()) and (self.getBlue() == newcolor.getBlue()))

    def __ne__(self,newcolor):
        return (not self.__eq__(newcolor))

    #def __tojava__(self, javaclass):
    #    if javaclass == awt.Color:
    #        return self.color
    #    else:
    #        return self

    #Added by BrianO
    def __add__(self, other):
        r = self.getRed() + other.getRed()
        g = self.getGreen() + other.getGreen()
        b = self.getBlue() + other.getBlue()

	# if(wrapAroundPixelValues):
	#    r = r % 256
	#    g = g % 256
	#    b = b % 256

	# return Color(r,g,b)
        #return Color( _checkPixel(r), _checkPixel(g), _checkPixel(b) )
        return Color(r, g, b)

    #Added by BrianO
    def __sub__(self, other):
        r = self.getRed() - other.getRed()
        g = self.getGreen() - other.getGreen()
        b = self.getBlue() - other.getBlue()

	# if(wrapAroundPixelValues):
	#    r = r % 256
	#    g = g % 256
	#    b = b % 256

	# return Color(r,g,b)
        #return Color( _checkPixel(r), _checkPixel(g), _checkPixel(b) )
        return Color(r, g, b)

    def setRGB(self, r, g, b):
    #    # self.color = awt.Color(r,g,b)
    #    self.color = awt.Color(_checkPixel(r), _checkPixel(g), _checkPixel(b))
        if not isinstance(r, numbers.Number):
            repValError("First color component (red) not a number")
            #raise ValueError
        if not isinstance(g, numbers.Number):
            repValError("Second color component (green) not a number")
            #raise ValueError
        if not isinstance(b, numbers.Number):
            repValError("Third color component (blue) not a number")
            #raise ValueError
        self.r = r
        self.g = g
        self.b = b
        self.validateColor()
    

    def getRed(self):
        #return self.color.getRed()
        return self.r

    def getGreen(self):
        #return self.color.getGreen()
        return self.g

    def getBlue(self):
        #return self.color.getBlue()
        return self.b

    def distance(self, othercolor):
        r = pow((self.getRed() - othercolor.getRed()),2)
        g = pow((self.getGreen() - othercolor.getGreen()),2)
        b = pow((self.getBlue() - othercolor.getBlue()) ,2)
        return math.sqrt(r+g+b)

    def makeDarker(self):
      #return self.color.darker()
        return Color(max(int(self.getRed() * 0.7), 0), max(int(self.getGreen() * 0.7), 0), max(int(self.getBlue() * 0.7), 0))

    def makeLighter(self):
      #return self.color.brighter()
        return Color(min(int(self.getRed() / 0.7), 255), min(int(self.getGreen() / 0.7), 255), min(int(self.getBlue() / 0.7), 255))
    
    def getRGB(self):
        return (self.getRed(), self.getGreen(), self.getBlue())
    
    #Convert to QColor
    def toQColor(self):
        return QColor(*self.getRGB())
    
    #Convert to color integer
    def toQColorInt(self):
        return self.toQColor().rgb()
        

#Done
def pickAColor():
    ## Dorn 5/8/2009:  Edited to be thread safe since this code is executed from an
    ## interpreter JESThread and will result in an update to the main JES GUI due to 
    ## it being a modal dialog.
    #from java.lang import Runnable

    #class pickAColorRunner(Runnable):
	#color = Color(0,0,0)
	#def run(self):
	#    retValue = swing.JColorChooser().showDialog(swing.JFrame(),"Choose a color", awt.Color(0,0,0))
	#    if retValue != None:
	#        self.color = Color(retValue.getRed(),retValue.getGreen(),retValue.getBlue())

    #runner = pickAColorRunner()
    #swing.SwingUtilities.invokeAndWait(runner)
    
    #return runner.color
    #root.lift()
    #root.update()
    # root = tkinter.Tk()
    # root.withdraw()
    # #root.lift()
    # 
    # if platform() == 'Darwin':  # How Mac OS X is identified by Python
    #     system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    # 
    # root.focus_force()
    # col = askcolor()
    # root.update()
    # root.destroy()
    col = QColorDialog.getColor()
    #return Color(int(col[0][0]), int(col[0][1]), int(col[0][2]))
    return Color(col)

def colorPalette():
    '''The built-in colors that you can use are:
    black
    white
    blue
    red
    green
    gray
    darkGray
    lightGray
    yellow
    orange
    pink
    magenta
    cyan
    '''
    print ('''The built-in colors that you can use are:
    black
    white
    blue
    red
    green
    gray
    darkGray
    lightGray
    yellow
    orange
    pink
    magenta
    cyan
    ''')


#Constants
black = Color(0,0,0)
white = Color(255,255,255)
blue = Color(0,0,255)
red = Color(255,0,0)
green = Color(0,255,0)
gray = Color(128,128,128)
darkGray = Color(64,64,64)
lightGray = Color(192,192,192)
yellow = Color(255,255,0)
orange = Color(255,200,0)
pink = Color(255,175,175)
magenta = Color(255,0,255)
cyan = Color(0,255,255)

#Pixel class, because JES has one
class Pixel:
    #Constructor
    def __init__(self, picture, x, y):
        self.picture = picture
        self.x = x
        self.y = y
        #self.color = Color(picture.getpixel((x,y)))
        self.color = picture.getPixelColor(x, y)
    
    #Render as string
    def __str__(self):
        return "Pixel red=%d green=%d blue=%d" % self.color.getRGB()
    
    #Get red
    def getRed(self):
        return self.color.getRed()
    
    #Get green
    def getGreen(self):
        return self.color.getGreen()
    
    #Get blue
    def getBlue(self):
        return self.color.getBlue()
    
    #Get color
    def getColor(self):
        return self.color
    
    #Set color
    def setColor(self, r, g=None, b=None):
        if g == None:
            if isinstance(r, Color):
                self.color = r
            elif isinstance(r, tuple) and len(r) == 3:
                self.color = Color(r)
            else:
                repValError("Invalid color arguments")
                #raise ValueError
        else:
            self.color = Color(r, g, b)
        self.updatePicture()
    
    #Set red
    def setRed(self, r):
        self.color = Color(r, self.color.getGreen(), self.color.getBlue())
        self.updatePicture()
    
    #Set green
    def setGreen(self, g):
        self.color = Color(self.color.getRed(), g, self.color.getBlue())
        self.updatePicture()
    
    #Set blue
    def setBlue(self, b):
        self.color = Color(self.color.getRed(), self.color.getGreen(), b)
        self.updatePicture()
    
    #Get color
    def getColor(self):
        return self.color
    
    #Get x
    def getX(self):
        return self.x
    
    #Get y
    def getY(self):
        return self.y
    
    #Update picture
    def updatePicture(self):
        self.picture.setPixel(self.x, self.y, self.color)

#Picture class
#Mostly just a wrapper for QImages
class Picture:
    #Constructor
    def __init__(self, width = None, height = None, aColor = None):
        global keepAround
        if isinstance(width, Picture):
            #We're duplicating a picture
            self.height = width.image.height()
            self.width = width.image.width()
            self.filename = width.filename
            self.image = QImage(width.image)
        else:
            #We're making a blank picture
            self.filename = None
            self.height = height
            self.width = width
            if height != None:
                if isinstance(aColor, Color):
                    col = aColor.getRGB()
                elif isinstance(aColor, QColor):
                    col = (aColor.red(), aColor.green(), aColor.blue())
                else:
                    col = aColor
                #Qt image
                self.image = QImage(width, height, QImage.Format_RGB32)
                if col is not None:
                    self.image.fill(QColor(*col))
        #Set up a window for displaying it
        self.window = QWidget()
        if self.filename == None:
            self.title = "Image"
            #self.window.setWindowTitle("Image")
        else:
            self.title = self.filename
            #self.window.setWindowTitle(self.filename)
        self.window.setWindowTitle(self.title)
        self.picLabel = QLabel(self.window)
        #self.frame = None
        if self.height != None:
            self.window.resize(self.width, self.height)
        
        #Optimization
        self.line = None
        self.lineindex = -1
        
        #Keep a copy around forever (bad to do generally, but important for this)
        keepAround.append(self)
    
    #Match JES's printing of a picture
    def __str__(self):
        ret = "Picture, "
        if self.filename == None and self.height == None:
            return ret + "empty"
        retend = "height %d width %d" % (self.height, self.width)
        if self.filename == None:
            return ret + retend
        else:
            return ret + "filename %s %s" % (self.filename, retend)
    
    #Load a file into the Picture object
    def loadOrFail(self, filename):
        try:
            #Check if it's supported
            suppt = isSupportedImageFormat(filename)
            if not suppt:
                #print("Warning! Attempting to open unsupported file type!")
                ##Make a PNG and mess with that instead
                #First, open a PIL image
                self.pil_im = PIL.Image.open(filename)
                #Next, create a temporary PNG file
                tmpfl = tempfile.mkstemp(suffix = '.png')
                #Now, keep track of the file name to work with
                self.workfile = tmpfl[1]
                #Finally, export the PIL image as a PNG to the temp file
                self.pil_im.save(tmpfl[1])
            else:
                #Nothing went wrong, so pil_im should be None
                self.pil_im = None
                #The "actual" file is the same as the specified file
                self.workfile = filename
            #self.image = PIL.Image.open(filename)
            #Load the QImage
            self.image = QImage(self.workfile)
            if self.image.isNull():
                #Load failed
                #raise IOError
                reportErrorToUser(IOError, "Loading image failed")
            self.filename = filename
            self.height = self.image.height()
            self.width = self.image.width()
            self.window.resize(self.width, self.height)
            self.title = self.filename
            self.window.setWindowTitle(self.title)
        except IOError:
            raise IOError(filename + " could not be opened or was not a picture. Check that you specified the path")
    
    #Set all pixels to a color
    def setAllPixelsToAColor(self, col):
        self.image.fill(QColor(*col.getRGB()))
    
    #Get Pixels
    def getPixels(self):
        ##Get the raw data
        #dat = self.image.getdata()
        ##Convert them all to Pixel objects
        #return [Pixel(self, 
        #On second thought, let's just mirror the Pixel class in JES
        #return [Pixel(self, x, y) for y in range(self.height) for x in range(self.width)]
        return [Pixel(self, x, y) for x in range(self.width) for y in range(self.height)]
    
    #Get Pixel
    def getPixel(self, x, y):
        return Pixel(self, x, y)
    
    #Get pixel color
    def getPixelColor(self, x, y):
        #return Color(self.image.pixel(x, y))
        #Making it faster
        #Get the line
        if self.lineindex == y:
            pixarray = self.line
        else:
            pixline = self.image.scanLine(y)
            pixarray = pixline.asarray(4*self.width)
            self.line = pixarray
            self.lineindex = y
        #pixline = self.image.scanLine(y)
        #pixarray = pixline.asarray(4*self.width)
        #Create a color
        return Color(pixarray[4*x+2], pixarray[4*x+1], pixarray[4*x])
    
    #Get width
    def getWidth(self):
        return self.width
    
    #Get height
    def getHeight(self):
        return self.height
    
    #Set the (x,y) pixel to Color col
    def setPixel(self, x, y, col):
        if not isinstance(col, Color):
            repValError("non-color passed to setPixel")
            #raise ValueError
        #self.image.putpixel((x,y), col.getRGB())
        #NOTE: There's a warning about this being a slow operation
        #self.image.setPixel(x, y, col.toQColorInt())
        #Get the line
        if self.lineindex == y:
            pixarray = self.line
        else:
            pixline = self.image.scanLine(y)
            pixarray = pixline.asarray(4*self.width)
            self.line = pixarray
            self.lineindex = y
        #pixline = self.image.scanLine(y)
        #pixarray = pixline.asarray(4*self.width)
        #Set the corresponding bytes
        pixarray[4*x] = col.getBlue() #Blue
        pixarray[4*x+1] = col.getGreen() #Green
        pixarray[4*x+2] = col.getRed() #Red
    
    #Print the picture in Canopy
    #TODO make Windows-friendly
    def printPicture(self):
        #return self.image
        #Canopy prints out PIL images nicely
        #So, we'll convert to and return a PIL image
        #This is very hack-ish
        #img = QImage("/tmp/example.png")
        img = QImage(self.image)
        #Create a temporary file
        tmpfl = tempfile.mkstemp(suffix = '.png')
        #print(tmpfl)
        #tmpfl.close()
        #img.save("/tmp/example.png", "PNG")
        #pil_im = PIL.Image.open("/tmp/example.png")
        img.save(tmpfl[1], "PNG")
        pil_im = PIL.Image.open(tmpfl[1])
        # buffer = QBuffer()
        # buffer.open(QIODevice.ReadWrite)
        # img.save(buffer, "PNG")
        # 
        # strio = io.BytesIO()
        # strio.write(buffer.data())
        # buffer.close()
        # strio.seek(0)
        #pil_im = PIL.Image.open(strio)
        return pil_im
    
    #Show the picture
    def show(self, title = None):
        #self.image.show(title)
        #root = tkinter.Tk()
        #root.withdraw()
        #second = tkinter.Toplevel()
        if title != None:
            self.window.setWindowTitle(title)
        
        pixmap = QPixmap.fromImage(self.image)
        self.picLabel.setPixmap(pixmap)
        
        # Show window
        self.window.show()
        self.window.activateWindow()
        self.window.raise_()
        self.window.activateWindow()
        QApplication.processEvents()
        
        #second.geometry("%dx%d" % (self.width, self.height))
        #root.lift()
        #canvas = tkinter.Canvas(second,width=self.width,height=self.height)
        #canvas.pack()
        #try:
        #image = PIL.ImageTk.PhotoImage(self.image)
        #except TclError:
        #    #This is for debugging
        #    second.destroy()
        #    raise
            
        #canvas.create_image(0,0,image=image, anchor = 'nw')
        
        #second.update()
        #self.frame = second #Keep reference around?
        #th.start()
        #second.update()
        #second.mainloop()
        #roots.append(root) #Keep a reference around
        #return self.frame
    
    #Repaint the picture
    def repaint(self):
        pixmap = QPixmap.fromImage(self.image)
        self.picLabel.setPixmap(pixmap)
        self.window.update()
        QApplication.processEvents()
    
    #Copy the picture other into this one at position (x,y) for upper left
    def copyInto(self, other, x, y):
        painter = QPainter()
        painter.begin(self.image)
        painter.drawImage(x, y, other.image)
        painter.end()
    
    #Draw a line on the picture
    def addLine(self, col, x1, y1, x2, y2):
        painter = QPainter()
        painter.begin(self.image)
        painter.setPen(QColor(*col.getRGB()))
        painter.drawLine(x1, y1, x2, y2)
        painter.end()
    
    #Draw text on the picture
    def addText(self, col, x, y, string, font = None):
        painter = QPainter()
        painter.begin(self.image)
        if font is not None:
            painter.setFont(font)
        painter.setPen(QColor(*col.getRGB()))
        painter.drawText(x, y, string)
        painter.end()
    
    #Draw a rectangle on the picture
    def addRect(self, col, x, y, w, h, isFilled):
        painter = QPainter()
        qcol = QColor(*col.getRGB())
        painter.begin(self.image)
        painter.setPen(qcol)
        if isFilled:
            painter.fillRect(x, y, w, h, qcol)
        else:
            painter.drawRect(x, y, w, h)
        painter.end()
    
    #Draw an oval on the picture
    def addOval(self, col, x, y, w, h, isFilled):
        painter = QPainter()
        qcol = QColor(*col.getRGB())
        painter.begin(self.image)
        painter.setPen(qcol)
        if isFilled:
            painter.setBrush(QBrush(qcol))
            #painter.fillRect(x, y, w, h, qcol)
        #else:
        painter.drawEllipse(x, y, w, h)
        painter.end()
    
    def addArc(self, col, x, y, w, h, start, angle, isFilled):
        painter = QPainter()
        qcol = QColor(*col.getRGB())
        painter.begin(self.image)
        painter.setPen(qcol)
        if isFilled:
            painter.setBrush(QBrush(qcol))
            #*16 because these functions use 16ths of degrees
            painter.drawPie(x, y, w, h, start*16, angle*16)
        else:
            #*16 because these functions use 16ths of degrees
            painter.drawArc(x, y, w, h, start*16, angle*16)
        painter.end()
    
    #Save the picture
    #If fname is None, overwrite the file
    def writeOrFail(self, fname = None, fmt = None):
        if fname == None:
            fil = self.filename
        else:
            fil = fname
        #Check if it's supported
        suppt = (fmt == None and isSupportedImageFormat(fil)) or\
            (fmt != None and isSupportedImageFormat(fmt))
        if not suppt:
            #print("Warning! Attempting to save unsupported file type!")
            #Save as a temporary PNG first
            itWorked = self.image.save(self.workfile, 'PNG')
            if itWorked:
                #Then, open the PNG as a PIL image
                pil_im = PIL.Image.open(self.workfile)
                #Then, save the PIL image where we want
                pil_im.save(fil, fmt)
        else:
            #Everything's good.  Just save the iamge
            itWorked = self.image.save(fil, fmt)
        if not itWorked:
            #print("Saving image failed")
            #raise IOError
            reportErrorToUser(IOError, "Saving image failed")

##
## Global picture functions
##
#Done
def makePicture(filename):
    '''
    Student documentation:

    The makePicture function takes a file name(with its extention) as an argument and returns a picture object containing that file.
    
    Example:
    from media.py import *

    myPicture =  makePicture("cat.jpg")

    myPicture now contains the cat.jpg picture. Please keep in mind that your file name must be inside single quotes ('') or double quotes ("").
    ------------------------------------------
    Developer documentation:
    '''
    global mediaFolder
    if not os.path.isabs(filename):
        filename = mediaFolder + filename
    if not os.path.isfile(filename):
        repValError("makePicture(filename): There is no file at "+filename)
        #raise ValueError
    picture = Picture()
    picture.loadOrFail(filename)
    return picture
    #return PIL.Image.open(filename)

# MMO (1 Dec 2005): Capped width/height to max 10000 and min 1
# alexr (6 Sep 2006): fixed to work without the Python classes.
# PamC (6 July 2007): added new optional param to allow for empty pictures
# with different background colors.
#Done
def makeEmptyPicture(width, height, acolor = white):
    '''
    Student documentation:

    The makeEmptyPicture function takes a width a height and a color(the default color value is white) as arguments and returns a picture object with those specifications.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(300, 200, blue)

    myPicture now contains a 300 by 200 pixel blue picture. To display a list of the built-in colors call the colorPalette function.
    ------------------------------------------
    Developer documentation:
    '''
    if width > 10000 or height > 10000:
        repValError("makeEmptyPicture(width, height[, acolor]): height and width must be less than 10000 each")
        #raise ValueError
    if width <= 0 or height <= 0:
        repValError("makeEmptyPicture(width, height[, acolor]): height and width must be greater than 0 each")
        #raise ValueError
    if not isinstance(acolor, Color):
        repValError("makeEmptyPicture(width, height[, acolor]): acolor must be a color")
        #raise ValueError
    #if isinstance(acolor, Color):
    #    col = acolor.getRGB()
    #else:
    #    col = acolor
    picture = Picture(width, height, acolor)
    # picture.createImage(width, height)
    # picture.filename = ''
    # careful here; do we want empty strings or "None"?
    return picture
    #return PIL.Image.new('RGB', (width, height), col)

def getPixels(picture):
    '''
    Student documentation:

    The getPixels function takes a picture as argument and returns all of the pixels in that picture as a list.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(300, 200, red)

    for pix in getPixels(myPicture):
        myPicture = pix.setBlue(255)

    I now have a pink picture.
    ------------------------------------------
    Developer documentation:
    '''
    if not isinstance(picture, Picture):
        repValError("getPixels(picture): Input is not a picture")
        #raise ValueError
    return picture.getPixels()

#Done
def getAllPixels(picture):
    return getPixels(picture)

#Done
def getWidth(picture):
    '''
    Student documentation:

    The getWidth function takes a picture as argument and returns it's width.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(300, 200)

    print(getWidth(myPicture))

    This prints 300.
    ------------------------------------------
    Developer documentation:
    '''
    if not isinstance(picture, Picture):
        repValError("getWidth(picture): Input is not a picture")
        #raise ValueError
    return picture.getWidth()

#Done
def getHeight(picture):
    '''
    Student documentation:

    The getHeight function takes a picture as argument and returns it's height.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(300, 200)

    print(getHeight(myPicture))

    This prints 200.
    ------------------------------------------
    Developer documentation:
    '''
    if not isinstance(picture,Picture):
        repValError("getHeight(picture): Input is not a picture")
    return picture.getHeight()

#Done
def show(picture, title=None):
    '''
    Student documentation:

    The show function takes a picture and a window title(the window title is optional) as arguments and makes a window with those objects.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(300, 200, red)
    show(myPicture, "a black picture")

    I now have a black window with the title a black picture.
    ------------------------------------------
    Developer documentation:
    '''
    #Old Plan:
        #1. Create broken window with Tkinter
        #2. Add unshow procedure
        #3. Make it passed with stuff
        #Downside: can't close window
    #picture.setTitle(getShortPath(picture.filename))
    #if title <> None:
        #picture.setTitle(title)
    if not isinstance(picture, Picture):
        repValError("show(picture): Input is not a picture")
        #raise ValueError
    picture.show(title)
    #frm = picture.show(title)
    #def on_closing():
    #    print("Got here") #Debug?
    #    frm.destroy()
        
    #frm.protocol("WM_DELETE_WINDOW", on_closing)

#NEW
#This is a Canopy thing
def printPicture(picture):
    if not isinstance(picture,Picture):
        repValError("repaint(picture): Input is not a picture")
        #raise ValueError
    return picture.printPicture()

def repaint(picture):
    #if not (isinstance(picture, World) or isinstance(picture,Picture)):
    #    print "repaint(picture): Input is not a picture or a world"
    #    raise ValueError
    #picture.repaint()
    if not isinstance(picture,Picture):
        repValError("repaint(picture): Input is not a picture")
        #raise ValueError
    picture.repaint()

## adding graphics to your pictures! ##
#Done
def addLine(picture, x1, y1, x2, y2, acolor=black):
    '''
    Student documentation:

    The addLine function takes a picture , a first x coordinate, a first y coordinate, a second x coordinate, a second y coordinate and a color(the default color is black) as arguments and draws a line from the first coordinate to the second coordinate in the specified color.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(300, 200, red)
    addLine(myPicture, 100, 0, 100, 100, blue)
    show(myPicture, "red picture with a blue line")

    I now have a red picture with a blue vertical line.
    ------------------------------------------
    Developer documentation:
    '''
    if not isinstance(picture, Picture):
        repValError("addLine(picture, x1, y1, x2, y2[, color]): First input is not a picture")
        #raise ValueError
    if not isinstance(acolor, Color):
        repValError("addLine(picture, x1, y1, x2, y2[, color]): Last input is not a color")
        #raise ValueError
    ##g = picture.getBufferedImage().createGraphics()
    ##g.setColor(acolor.color)
    ##g.drawLine(x1 - 1,y1 - 1,x2 - 1,y2 - 1)
    picture.addLine(acolor,x1,y1,x2,y2)

#Done
def addText(picture, x, y, string, acolor=black):
    '''
    Student documentation:

    The addText function takes a picture, a x coordinate, a y coordinate, the text you want to add and a color(the default color is black) as arguments and writes the text in the picture.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(200, 200)
    addText(myPicture, 100, 100, "Hi")
    show(myPicture, "a white picture with a black greeting")

    I now have a white picture with a black greeting.
    ------------------------------------------
    Developer documentation:
    '''
    if not isinstance(picture, Picture):
        repValError("addText(picture, x, y, string[, color]): First input is not a picture")
        #raise ValueError
    if not isinstance(acolor, Color):
        repValError("addText(picture, x, y, string[, color]): Last input is not a color")
        #raise ValueError
    ##g = picture.getBufferedImage().getGraphics()
    ##g.setColor(acolor.color)
    ##g.drawString(string, x - 1, y - 1)
    picture.addText(acolor,x,y,string)

# PamC: Added this function to allow different font styles
#Done
def addTextWithStyle(picture, x, y, string, style, acolor=black):
    if not isinstance(picture, Picture):
        repValError("addTextWithStyle(picture, x, y, string, style[, color]): First input is not a picture")
    if not isinstance(style, QFont):
        repValError("addTextWithStyle(picture, x, y, string, style[, color]): Input is not a style (see makeStyle)")
    if not isinstance(acolor, Color):
        repValError("addTextWithStyle(picture, x, y, string, style[, color]): Last input is not a color")
    picture.addText(acolor,x,y,string,style)

#Done
def addRect(picture, x,y,w,h, acolor=black):
    '''
    Student documentation:

    The addText function takes a picture, a x coordinate, a y coordinate, the width and height of your unfilled rectangle and a color(the default color is black) as arguments and draws an unfilled rectangle in the picture.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(400, 400)
    addRect(myPicture, 100, 100, 200, 200, blue)
    show(myPicture, "a white picture with a blue unfilled rectangle")

    I now have a white picture with a blue unfilled rectangle.
    ------------------------------------------
    Developer documentation:
    '''
    if not isinstance(picture, Picture):
        repValError("addRect(picture, x, y, w, h[, color]): First input is not a picture")
        #raise ValueError
    if not isinstance(acolor, Color):
        repValError("addRect(picture, x, y, w, h[, color]): Last input is not a color")
        #raise ValueError
    ##g = picture.getBufferedImage().getGraphics()
    ##g.setColor(acolor.color)
    ##g.drawRect(x - 1,y - 1,w,h)
    picture.addRect(acolor,x,y,w,h,False)

#Done
def addRectFilled(picture,x,y,w,h, acolor=black):
    '''
    Student documentation:

    The addRectFilled function takes a picture, a x coordinate, a y coordinate, the width and height of your filled rectangle and a color(the default color is black) as arguments and draws a filled rectangle in the picture.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(400, 400)
    addRectFilled(myPicture, 100, 100, 200, 200, red)
    show(myPicture, "a white picture with a red filled rectangle")

    I now have a white picture with a red filled rectangle.
    ------------------------------------------
    Developer documentation:
    '''
    if not isinstance(picture,Picture):
        repValError("addRectFilled(picture, x, y, w, h[, color]): First input is not a picture")
        #raise ValueError
    if not isinstance(acolor, Color):
        repValError("addRectFilled(picture, x, y, w, h[, color]): Last input is not a color")
        #raise ValueError
    ##g = picture.getBufferedImage().getGraphics()
    ##g.setColor(acolor.color)
    ##g.fillRect(x - 1,y - 1,w,h)
    picture.addRect(acolor,x,y,w,h,True)

# PamC: Added the following addOval, addOvalFilled, addArc, and addArcFilled
# functions to add more graphics to pictures.
def addOval(picture, x,y,w,h, acolor=black):
    '''
    Student documentation:

    The addOval function takes a picture, a x coordinate, a y coordinate, the width and height of your unfilled oval and a color(the default color is black) as arguments and draws an unfilled oval in the picture.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(400, 400)
    addOval(myPicture, 100, 100, 200, 200, red)
    show(myPicture, "a white picture with a red unfilled oval")

    I now have a white picture with a red unfilled oval.
    ------------------------------------------
    Developer documentation:
    '''
    if not isinstance(picture, Picture):
        repValError("addOval(picture, x, y, w, h[, color]): First input is not a picture")
        #raise ValueError
    if not isinstance(acolor, Color):
        repValError("addOval(picture, x, y, w, h[, color]): Last input is not a color")
        #raise ValueError
    ##g = picture.getBufferedImage().getGraphics()
    ##g.setColor(acolor.color)
    ##g.drawRect(x - 1,y - 1,w,h)
    picture.addOval(acolor,x,y,w,h,False)

#Done
def addOvalFilled(picture,x,y,w,h,acolor=black):
    '''
    Student documentation:

    The addOvalFilled function takes a picture, a x coordinate, a y coordinate, the width and height of your filled oval and a color(the default color is black) as arguments and draws an filled oval in the picture.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(400, 400)
    addOvalFilled(myPicture, 100, 100, 200, 200, pink)
    show(myPicture, "a white picture with a pink unfilled oval")

    I now have a white picture with a pink unfilled oval.
    ------------------------------------------
    Developer documentation:
    '''
    if not isinstance(picture,Picture):
        repValError("addOvalFilled(picture, x, y, w, h[, color]): First input is not a picture")
        #raise ValueError
    if not isinstance(acolor, Color):
        repValError("addOvalFilled(picture, x, y, w, h[, color]): Last input is not a color")
        #raise ValueError
    picture.addOval(acolor,x,y,w,h,True)

#Done
#Note: Uses degrees
def addArc(picture,x,y,w,h,start,angle,acolor=black):
    if not isinstance(picture,Picture):
        repValError("addArc(picture, x, y, w, h, start, angle[, color]): First input is not a picture")
        #raise ValueError
    if not isinstance(acolor, Color):
        repValError("addArc(picture, x, y, w, h[, color]): Last input is not a color")
        #raise ValueError
    picture.addArc(acolor,x,y,w,h,start,angle,False)

#Note: Uses degrees
def addArcFilled(picture,x,y,w,h,start,angle,acolor=black):
    if not isinstance(picture,Picture):
        repValError("addArcFilled(picture, x, y, w, h[, color]): First First input is not a picture")
        #raise ValueError
    if not isinstance(acolor, Color):
        repValError("addArcFill(picture, x, y, w, h[, color]): Last input is not a color")
        #raise ValueError
    picture.addArc(acolor,x,y,w,h,start,angle,True)

## note the -1; in JES we think of pictures as starting at (1,1) but not
## in the Java.
##
## 29 Oct 2008: -1 changed to Picture._PictureIndexOffset
## note: Nathan Fox got rid of this offset thing
#Done
def getPixel(picture,x,y):
    '''
    Student documentation:

    The getPixel function takes a picture, a x coordinate and a y coordinate as arguments and returns the pixel at that index.
    
    Example:
    from media.py import *

    myPicture =  makeEmptyPicture(200, 200)
    pix = getPixel(myPicture, 100, 100)
    print(pix)

    I now have a pix variable with the pixel at 99,99.
    ------------------------------------------
    Developer documentation:
    '''
    if not isinstance(picture, Picture):
        repValError("getPixel(picture,x,y): First input is not a picture")
        #raise ValueError
    # if ( x < Picture._PictureIndexOffset ) or ( x > getWidth(picture) - 1 + Picture._PictureIndexOffset ):
    #     print("getPixel(picture,x,y): x (= %s) is less than %s or bigger than the width (= %s)" % (x,Picture._PictureIndexOffset,getWidth(picture) - 1 + Picture._PictureIndexOffset)
    #     raise ValueError
    # if ( y < Picture._PictureIndexOffset ) or ( y > getHeight(picture) - 1 + Picture._PictureIndexOffset ):
    #     print "getPixel(picture,x,y): y (= %s) is less than %s or bigger than the height (= %s)" % (y,Picture._PictureIndexOffset,getHeight(picture) - 1 + Picture._PictureIndexOffset)
    #     raise ValueError
    if ( x < 0 ) or ( x > getWidth(picture) - 1 ):
        repValError("getPixel(picture,x,y): x (= %s) is less than %s or bigger than the width (= %s)" % (x, 0, getWidth(picture) - 1))
        #raise ValueError
    if ( y < 0 ) or ( y > getHeight(picture) - 1 ):
        repValError("getPixel(picture,x,y): y (= %s) is less than %s or bigger than the height (= %s)" % (y, 0, getHeight(picture) - 1))
        #raise ValueError

    #return picture.getPixel(x - Picture._PictureIndexOffset, y - Picture._PictureIndexOffset)
    return picture.getPixel(x, y)

#Added as a better name for getPixel
#Done
def getPixelAt(picture,x,y):
    return getPixel(picture,x,y)

#Done
def setRed(pixel,value):
    #value = _checkPixel(value)
    if not isinstance(pixel, Pixel):
        repValError("setRed(pixel,value): Input is not a pixel")
        #raise ValueError
    pixel.setRed(value)

#Done
def getRed(pixel):
    if not isinstance(pixel, Pixel):
        repValError("getRed(pixel): Input is not a pixel")
        #raise ValueError
    return pixel.getRed()

#Done
def setBlue(pixel,value):
    #value = _checkPixel(value)
    if not isinstance(pixel, Pixel):
        repValError("setBlue(pixel,value): Input is not a pixel")
        #raise ValueError
    pixel.setBlue(value)

#Done
def getBlue(pixel):
    if not isinstance(pixel,Pixel):
        repValError("getBlue(pixel): Input is not a pixel")
        #raise ValueError
    return pixel.getBlue()

#Done
def setGreen(pixel,value):
    #value = _checkPixel(value)
    if not isinstance(pixel, Pixel):
        repValError("setGreen(pixel,value): Input is not a pixel")
        #raise ValueError
    pixel.setGreen(value)

def getGreen(pixel):
    if not isinstance(pixel, Pixel):
        repValError("getGreen(pixel): Input is not a pixel")
        #raise ValueError
    return pixel.getGreen()

#Done
def getColor(pixel):
    if not isinstance(pixel, Pixel):
        repValError("getColor(pixel): Input is not a pixel")
        #raise ValueError
    return pixel.getColor()

def setColor(pixel,color):
    if not isinstance(pixel, Pixel):
        repValError("setColor(pixel,color): First input is not a pixel")
        #raise ValueError
    if not isinstance(color, Color):
        repValError("setColor(pixel,color): Second input is not a color")
        #raise ValueError
    pixel.setColor(color)

def getX(pixel):
    if not isinstance(pixel, Pixel):
        repValError("getX(pixel): Input is not a pixel")
        #raise ValueError
    return pixel.getX()# + Picture._PictureIndexOffset

def getY(pixel):
    if not isinstance(pixel,Pixel):
        repValError("getY(pixel): Input is not a pixel")
        #raise ValueError
    return pixel.getY()# + Picture._PictureIndexOffset

#Done
def distance(c1,c2):
    if not isinstance(c1, Color):
        repValError("distance(c1,c2): First input is not a color")
        #raise ValueError
    if not isinstance(c2, Color):
        repValError("distance(c1,c2): Second input is not a color")
        #raise ValueError
    return c1.distance(c2)

#Done
def writePictureTo(picture,filename):
    global mediaFolder
    if not os.path.isabs(filename):
        filename = mediaFolder + filename
    if not isinstance(picture, Picture):
        repValError("writePictureTo(picture,filename): First input is not a picture")
        #raise ValueError
    picture.writeOrFail(filename)
    if not os.path.exists(filename):
        repValError("writePictureTo(picture,filename): Path is not valid")
        #raise ValueError


#New
#Call save dialog then write picture to where saved
def savePicture(picture):
    fil = pickASaveFile()
    #Try to get a format
    #If no format given, yell at the user
    dotloc = fil.rfind(".")
    if dotloc == -1:
        repValError("Error: No file extension provided")
        #raise ValueError("Error: No file extension provided")
    writePictureTo(picture, fil)

# not to be confused with setColor, totally different, don't document/export
def _setColorTo(color, other):
    color.setRGB(other.getRed(), other.getGreen(), other.getBlue())
    return color

#def makeDarker(color):
    #"""This function has side effects on purpose, see p49 """
    #return _setColorTo(color, color.darker())

#Done
def makeDarker(color):
    if not isinstance(color,Color):
        repValError("makeDarker(color): Input is not a color")
        #raise ValueError("makeDarker(color): Input is not a color")
    return Color( color.makeDarker() )

#def makeLighter(color):
  #"""This function has side effects on purpose, see p49"""
  #return _setColorTo(color,color.brighter())

#Done
def makeLighter(color):
    if not isinstance(color,Color):
        repValError("makeLighter(color): Input is not a color")
        #raise ValueError("makeLighter(color): Input is not a color")
    return Color( color.makeLighter() )

#Done
def makeBrighter(color): #This is the same as makeLighter(color)
    if not isinstance(color,Color):
        repValError("makeBrighter(color): Input is not a color")
        #raise ValueError("makeBrighter(color): Input is not a color")
    return Color( color.makeLighter() )

#Done
def makeColor(red,green=None,blue=None):
    return Color( red, green, blue)

#Done
def setAllPixelsToAColor(picture,color):
    #"""This function sets the picture to one color"""
    if not isinstance(picture, Picture):
        repValError("setAllPixelsToAColor(picture,color): First input is not a picture")
        #raise ValueError("setAllPixelsToAColor(picture,color): First input is not a picture")
    if not isinstance(color,Color):
        repValError("setAllPixelsToAColor(picture,color): Second input is not a color")
        #raise ValueError("setAllPixelsToAColor(picture,color): Second input is not a color")
    picture.setAllPixelsToAColor(color)


def copyInto(smallPicture, bigPicture, startX, startY):
    #like copyInto(butterfly, jungle, 20,20)
    if not isinstance(smallPicture, Picture):
        repValError("copyInto(smallPicture, bigPicture, startX, startY): smallPicture must be a picture")
        #raise ValueError("copyInto(smallPicture, bigPicture, startX, startY): smallPicture must be a picture")
    if not isinstance(bigPicture, Picture):
        repValError("copyInto(smallPicture, bigPicture, startX, startY): bigPicture must be a picture")
        #raise ValueError
    if (startX < 0) or (startX > getWidth(bigPicture) - 1):
        repValError("copyInto(smallPicture, bigPicture, startX, startY): startX must be within the bigPicture")
        #raise ValueError
    if (startY < 0) or (startY > getHeight(bigPicture) - 1):
        repValError("copyInto(smallPicture, bigPicture, startX, startY): startY must be within the bigPicture")
        #raise ValueError
    if (startX + getWidth(smallPicture) - 1) > (getWidth(bigPicture) - 1) or \
            (startY + getHeight(smallPicture) - 1) > (getHeight(bigPicture) - 1):
        repValError("copyInto(smallPicture, bigPicture, startX, startY): smallPicture won't fit into bigPicture")
        #raise ValueError

    xOffset = startX
    yOffset = startY

    #for x in range(0, getWidth(smallPicture)):
    #    for y in range(0, getHeight(smallPicture)):
    #        bigPicture.setBasicPixel(x + xOffset, y + yOffset, smallPicture.getBasicPixel(x,y))
    bigPicture.copyInto(smallPicture, xOffset, yOffset)

    return bigPicture

# Alyce Brady's version of copyInto, with additional error-checking on the upper-left corner
# Will copy as much of the original picture into the destination picture as will fit.
#def copyInto(origPict, destPict, upperLeftX, upperLeftY):
#  if not isinstance(origPict, Picture):
#    print "copyInto(origPict, destPict, upperLeftX, upperLeftY): First parameter is not a picture"
#    raise ValueError
#  if not isinstance(destPict, Picture):
#    print "copyInto(origPict, destPict, upperLeftX, upperLeftY): Second parameter is not a picture"
#    raise ValueError
#  if upperLeftX < 1 or upperLeftX > getWidth(destPict):
#    print "copyInto(origPict, destPict, upperLeftX, upperLeftY): upperLeftX must be within the destPict"
#    raise ValueError
#  if upperLeftY < 1 or upperLeftY > getHeight(destPict):
#    print "copyInto(origPict, destPict, upperLeftX, upperLeftY): upperLeftY must be within the destPict"
#    raise ValueError
#  return origPict.copyInto(destPict, upperLeftX-1, upperLeftY-1)
#Done
def duplicatePicture(picture):
    """returns a copy of the picture"""
    if not isinstance(picture, Picture):
        repValError("duplicatePicture(picture): Input is not a picture")
        #raise ValueError
    return Picture(picture)

# Alyce Brady/ Pam Cutter: Function that crops a picture
#def cropPicture(picture, upperLeftX, upperLeftY, width, height):
#  if not isinstance(picture, Picture):
#    print "crop(picture, upperLeftX, upperLeftY, width, height): First parameter is not a picture"
#    raise ValueError
#  if upperLeftX < 1 or upperLeftX > getWidth(picture):
#    print "crop(picture, upperLeftX, upperLeftY, width, height): upperLeftX must be within the picture"
#    raise ValueError
#  if upperLeftY < 1 or upperLeftY > getHeight(picture):
#    print "crop(picture, upperLeftX, upperLeftY, width, height): upperLeftY must be within the picture"
#    raise ValueError
#  return picture.crop(upperLeftX-1, upperLeftY-1, width, height)

##
# Input and Output interfaces
#
# Note: These calls must be done in a threadsafe manner since the JESThread will be
# executing them rather than the GUI's event dispatch thread.  See SimpleInput/Output.java
# for the threadsafe execution.
##

#  radius = SimpleInput.getNumber("Enter the radius of the cylinder")
#  SimpleOutput.showInformation("The volume of the cylinder is %.02f " % volume)

#Done
def requestNumber(message, minn=-2147483647, maxx=2147483647, dec=15):
    #return SimpleInput.getNumber(message)
    tpl = QInputDialog.getDouble(None, "Please enter a number", message,\
        decimals=dec, min=minn, max=maxx)
    if tpl[1]:
        return tpl[0]
    else:
        return None

#Done
def requestInteger(message, minn=-2147483647, maxx=2147483647, stp=1):
    #return SimpleInput.getIntNumber(message)
    tpl = QInputDialog.getInt(None, "Please enter an integer", message,\
        step=stp, min=minn, max=maxx)
    if tpl[1]:
        return tpl[0]
    else:
        return None

#Done
def requestIntegerInRange(message, min, max):
    if min >= max:
        repValError("requestIntegerInRange(message, min, max): min >= max not allowed")
        #raise ValueError

    #return SimpleInput.getIntNumber(message, min, max)
    return requestInteger(message, minn=min, maxx=max)

#Done
def requestString(message):
    tpl = QInputDialog.getText(None, "Please enter some text", message)
    if tpl[1]:
        return tpl[0]
    else:
        return None


#5/15/09 Dorn: Updated input and raw_input to read from the console
#def input(message=None):
#    im = JESInputManager()
#    return eval(im.readInput(message))

#def raw_input(message=None):
#    im = JESInputManager()
#    return im.readInput(message)
    
#Done
def showWarning(message):
    QMessageBox.warning(None, "Warning!", message)

#Done
def showInformation(message):
    QMessageBox.information(None, "Info", message)

#Done
def showError(message):
    QMessageBox.critical(None, "Error!!", message)

# 
# ##
# # Java Music Interface
# ##
# def playNote(note, duration, intensity=64):
#     #JavaMusic.playNote(note, duration, intensity)
#     pass #TODO
# 
# 
##
# General user tools
#

#Done
def pickAFile(sdir = None):
    global mediaFolder
    ## Note: this needs to be done in a threadsafe manner, see FileChooser
    ## for details how this is accomplished.
    #return FileChooser.pickAFile()
    #root.update()
    #This is to prevent stupid windows from hanging around
    #root = tkinter.Tk()
    #root.withdraw()
    #root.lift()
    
    #if platform() == 'Darwin':  # How Mac OS X is identified by Python
    #    system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    
    #root.focus_force()
    #ret = tkinter.filedialog.askopenfilename()
    #root.update()
    #root.destroy()
    if sdir is None:
        ret = QFileDialog.getOpenFileName(directory = mediaFolder)
    else:
        ret = QFileDialog.getOpenFileName(directory = sdir)
    return ret

#New
#Done
def pickASaveFile(sdir = None):
    global mediaFolder
    ## Note: this needs to be done in a threadsafe manner, see FileChooser
    ## for details how this is accomplished.
    #return FileChooser.pickAFile()
    #root.update()
    #This is to prevent stupid windows from hanging around
    #root = tkinter.Tk()
    #root.withdraw()
    #root.lift()
    
    #if platform() == 'Darwin':  # How Mac OS X is identified by Python
    #    system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    
    #root.focus_force()
    #ret = tkinter.filedialog.askopenfilename()
    #root.update()
    #root.destroy()
    if sdir is None:
        ret = QFileDialog.getSaveFileName(directory = mediaFolder)
    else:
        ret = QFileDialog.getSaveFileName(directory = sdir)
    return ret

#Done
def pickAFolder(sdir = None):
    global mediaFolder
    ## Note: this needs to be done in a threadsafe manner, see FileChooser
    ## for details how this is accomplished.
    #dir = FileChooser.pickADirectory() TODO
    #root = tkinter.Tk()
    #root.withdraw()
    #root.lift()
    
    #if platform() == 'Darwin':  # How Mac OS X is identified by Python
    #    system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
    
    #root.focus_force()
    #dirc = tkinter.filedialog.askdirectory()
    #root.update()
    #root.destroy()
    if sdir is None:
        dirc = QFileDialog.getExistingDirectory(directory = mediaFolder)
    else:
        dirc = QFileDialog.getExistingDirectory(directory = sdir)
    if ( dirc != None ):
        return dirc + os.sep
    return None

def quit():
    sys.exit(0)

# ##
# # MediaTools interface
# #
# # TODO modify viewer.changeToBaseOne
# 
COL_BLOCK_SIZE = 20
#Need this mini-class for registering mouse clicks on picture in explorer
class ClickableLabel(QLabel):
    #Need to include the explorer so we can talk to it
    def __init__(self, parent, pexplore):
        super().__init__(parent)
        self.pexplore = pexplore
    
    #Here's where the mouse click is registered
    def mousePressEvent(self, QMouseEvent):
        self.pexplore.imageClicked(QMouseEvent.pos())

#Crosshair on the image explorer
class Crosshair:
    #Construct a crosshair for a given picture
    def __init__(self, pic):
        #Keep track of the picture
        self.pic = pic
        #It starts un-rendered
        self.is_rendered = False
        #It doesn't have a position initially
        self.x = None
        self.y = None
        #There are no saved pixels initially
        self.saved_pixels = []
        #Constants
        #self.COLOR = white
        self.SIZE = 7
    
    #Set the crosshair's position
    #Unrender it, move it, render it
    def setPosition(self, x, y):
        self.unrender()
        self.x = x
        self.y = y
        self.render()
    
    #Un-draw the crosshair
    def unrender(self):
        for pix in self.saved_pixels:
            #Re-draw the pixel the way it was
            self.pic.setPixel(*pix)
        #Un-save the pixels
        self.saved_pixels = []
    
    #Draw the crosshair
    def render(self):
        #+ sign SIZExSIZE, adaptive color
        w = getWidth(self.pic)
        h = getHeight(self.pic)
        #What color is the pixel?
        pcolor = getColor(getPixel(self.pic, self.x, self.y)).getRGB()
        #Is it dark or light?
        pcolorval = pcolor[0]+pcolor[1]+pcolor[2]
        if pcolorval <= 382:
            #It's dark, so use a white crosshair
            color = white
        else:
            #It's light, so use a dark crosshair
            color = black
        for x in range(self.x-self.SIZE//2, self.x+self.SIZE//2+1):
            if x >= 0 and x < w and x != self.x:
                #Save what's currently there
                self.saved_pixels.append((x, self.y, getColor(getPixel(self.pic, x, self.y))))
                #Make it white
                self.pic.setPixel(x, self.y, color)
        for y in range(self.y-self.SIZE//2, self.y+self.SIZE//2+1):
            if y >= 0 and y < w and y != self.y:
                #Save what's currently there
                self.saved_pixels.append((self.x, y, getColor(getPixel(self.pic, self.x, y))))
                #Make it white
                self.pic.setPixel(self.x, y, color)

#Emulate the JES Picture Explorer
class PictureExplorer(QWidget):
    #TODO make look nice
    #TODO box around color block
    #TODO box around picture
    
    #Constructor
    #Should create window, populate with (0,0)
    #remember it globally (to avoid garbage collection issues)
    #and show it
    def __init__(self, pic):
        super().__init__()
        self.setWindowTitle("Image Explorer: " + pic.title)
        self.pic = duplicatePicture(pic)
        self.drawingPic = pic
        layout = QVBoxLayout()
        self.setLayout(layout)
        #self.window.setLayout(QGridLayout())
        #Starting coords
        self.coord_x = 0
        self.coord_y = 0
        #Frame for X and Y
        self.XYFrame = QFrame(self)
        layoutXY = QHBoxLayout()
        self.XYFrame.setLayout(layoutXY)
        self.block_edit = False
        #X
        xlabel = QLabel(self.XYFrame)
        xlabel.setText("X:")
        layoutXY.addWidget(xlabel)
        #xwidget = QSpinBox(self.XYFrame)
        self.xwidget = QSpinBox(self.XYFrame)
        self.xwidget.setRange(0, pic.getWidth()-1)
        self.xwidget.setValue(self.coord_x)
        #Testing connections
        #QObject.connect(xwidget, SIGNAL('valueChanged(int)'), self, SLOT('test(int)'))
        QObject.connect(self.xwidget, SIGNAL('valueChanged(int)'), self, SLOT('updatedPos()'))
        layoutXY.addWidget(self.xwidget)
        #Y
        ylabel = QLabel(self.XYFrame)
        ylabel.setText("Y:")
        layoutXY.addWidget(ylabel)
        self.ywidget = QSpinBox(self.XYFrame)
        self.ywidget.setRange(0, pic.getHeight()-1)
        self.ywidget.setValue(self.coord_y)
        QObject.connect(self.ywidget, SIGNAL('valueChanged(int)'), self, SLOT('updatedPos()'))
        layoutXY.addWidget(self.ywidget)
        layout.addWidget(self.XYFrame)
        #Frame for color stuff
        self.colFrame = QFrame(self)
        layoutCol = QHBoxLayout()
        self.colFrame.setLayout(layoutCol)
        #RGB text
        self.rgblabel = QLabel(self.colFrame)
        #col = getColor(getPixel(pic,self.coord_x,self.coord_y)).getRGB()
        #self.rgblabel.setText("R: " + str(col[0]) + " G: " + str(col[1]) + \
        #    " B: " + str(col[2]))
        layoutCol.addWidget(self.rgblabel)
        colloclabel = QLabel(self.colFrame)
        colloclabel.setText("Color at location:")
        layoutCol.addWidget(colloclabel)
        #Color block
        # colimg = QImage(COL_BLOCK_SIZE, COL_BLOCK_SIZE, QImage.Format_RGB32)
        # colimg.fill(QColor(*col)) #TODO
        self.colLabel = QLabel(self.colFrame)
        #self.setColorBlock(*col)
        self.updateColorStuff()
        # pixmap1 = QPixmap.fromImage(colimg)
        # self.colLabel.setPixmap(pixmap1)
        layoutCol.addWidget(self.colLabel)
        layout.addWidget(self.colFrame)
        #Crosshair
        self.crosshair = Crosshair(self.drawingPic)
        self.crosshair.setPosition(0, 0)
        #Picture window
        #self.picLabel = QLabel(self)
        self.picLabel = ClickableLabel(self, self)
        pixmap2 = QPixmap.fromImage(self.drawingPic.image)
        self.picLabel.setPixmap(pixmap2)
        layout.addWidget(self.picLabel)
        #Resize the window
        self.resize(pic.getWidth(), pic.getHeight() + COL_BLOCK_SIZE)
        #Remember the window
        keepAround.append(self)
        #Show the window
        self.show()
        self.activateWindow()
        self.raise_()
        self.activateWindow()
        QApplication.processEvents()
    
    #Update color text and color block
    #based on self.coord_x and self.coord_y
    def updateColorStuff(self):
        #Get the color
        col = getColor(getPixel(self.pic,self.coord_x,self.coord_y)).getRGB()
        #Color text
        self.rgblabel.setText("R: " + str(col[0]) + " G: " + str(col[1]) + \
            " B: " + str(col[2]))
        #Color block
        colimg = QImage(COL_BLOCK_SIZE, COL_BLOCK_SIZE, QImage.Format_RGB32)
        colimg.fill(QColor(*col))
        pixmap1 = QPixmap.fromImage(colimg)
        self.colLabel.setPixmap(pixmap1)
    
    #Update crosshair position and show it
    def updateCrosshair(self):
        #Move the crosshair
        self.crosshair.setPosition(self.coord_x, self.coord_y)
        #Redraw the picture
        pixmap2 = QPixmap.fromImage(self.drawingPic.image)
        self.picLabel.setPixmap(pixmap2)
    
    # @pyqtSlot(int)
    # def test(self, x):
    #     print("hello " + str(x))
    
    #Position was updated via x/y boxes
    #Update color and label accordingly
    @pyqtSlot()
    def updatedPos(self):
        #Only do this if we manually changed the numbers
        if not self.block_edit:
            #Update the current coords
            self.coord_x = self.xwidget.value()
            self.coord_y = self.ywidget.value()
            #Update the stuff that can change
            self.updateColorStuff()
            #Update the crosshair
            self.updateCrosshair()
            #Repaint the window
            self.update()
            QApplication.processEvents()
    
    #Clicked on image
    def imageClicked(self, pt):
        #Make sure we don't issue duplicate updates
        self.block_edit = True
        #Update the current coords
        self.coord_x = pt.x()
        self.coord_y = pt.y()
        #Change the spinboxes to the new coords
        self.xwidget.setValue(self.coord_x)
        self.ywidget.setValue(self.coord_y)
        #Update the stuff that can change
        self.updateColorStuff()
        #Update the crosshair
        self.updateCrosshair()
        #Repaint the window
        self.update()
        QApplication.processEvents()
        #Manual updates are safe again
        self.block_edit = False

##START OF SOUND

#Emulate the JES Sound Explorer
class SoundExplorer(QWidget):
    #TODO make look nice
    #TODO selections
    
    #TODO make these variable/scrollable
    PIC_WIDTH = 600
    PIC_HEIGHT = 200
    EXTRA_HEIGHT = 300
    
    #Constructor
    #Should create window, populate with default values
    #remember it globally (to avoid garbage collection issues)
    #and show it
    def __init__(self, sound):
        super().__init__()
        
        self.sound = sound
        self.block_edit = False
        
        title = "Sound"
        if sound.fileName is not None:
            title = sound.fileName
        self.setWindowTitle("Sound Explorer: " + title)
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        #What's selected?
        self.index = 0
        self.value = getSampleValueAt(sound, self.index)
        
        #Top row of buttons
        self.playFrame = QFrame(self)
        layoutPlay = QHBoxLayout()
        self.playFrame.setLayout(layoutPlay)
        self.playButton = QPushButton("Play Entire Sound", self.playFrame)
        self.playButton.clicked.connect(sound.play)
        self.playBeforeButton = QPushButton("Play Before", self.playFrame)
        def lpb():
            sound.play(0, self.index)
        self.playBeforeButton.clicked.connect(lpb)
        self.playAfterButton = QPushButton("Play After", self.playFrame)
        def lpa():
            sound.play(self.index)
        self.playAfterButton.clicked.connect(lpa)
        self.stopButton = QPushButton("Stop Playing", self.playFrame)
        self.stopButton.clicked.connect(sound.stopPlaying)
        layoutPlay.addWidget(self.playButton)
        layoutPlay.addWidget(self.playBeforeButton)
        layoutPlay.addWidget(self.playAfterButton)
        layoutPlay.addWidget(self.stopButton)
        layout.addWidget(self.playFrame)
        
        #Second row of buttons
        #TODO selections
        
        #Sound image
        self.imgFrame = QFrame(self)
        imgLayout = QHBoxLayout()
        self.imgFrame.setLayout(imgLayout)
        self.picLabel = ClickableLabel(self, self)
        self.pic = sound.getImageRep(SoundExplorer.PIC_WIDTH, SoundExplorer.PIC_HEIGHT)
        self.drawingPic = duplicatePicture(self.pic)
        pixmap = QPixmap.fromImage(self.drawingPic.image)
        self.picLabel.setPixmap(pixmap)
        imgLayout.addWidget(self.picLabel)
        layout.addWidget(self.imgFrame)
        
        #Index/value row
        self.indexValueFrame = QFrame(self)
        layoutIV = QHBoxLayout()
        self.indexValueFrame.setLayout(layoutIV)
        self.ilabel = QLabel(self.indexValueFrame)
        self.ilabel.setText("Current Index:")
        layoutIV.addWidget(self.ilabel)
        self.iwidget = QSpinBox(self.indexValueFrame)
        self.iwidget.setRange(0, getLength(sound))
        self.iwidget.setValue(self.index)
        #QObject.connect(self.ywidget, SIGNAL('valueChanged(int)'), self, SLOT('updatedPos()'))
        self.iwidget.valueChanged.connect(self.updatedPos)
        layoutIV.addWidget(self.iwidget)
        self.vlabel = QLabel(self.indexValueFrame)
        self.vlabel.setText("Sample Value:")
        layoutIV.addWidget(self.vlabel)
        self.vwidget = QLabel(self.indexValueFrame)
        self.vwidget.setText(str(self.value))
        #QObject.connect(self.ywidget, SIGNAL('valueChanged(int)'), self, SLOT('updatedPos()'))
        #self.iwidget.valueChanged(int).connect(self.updatedPos())
        layoutIV.addWidget(self.vwidget)
        layout.addWidget(self.indexValueFrame)
        
        #Samples between pixels row
        self.sbetweenFrame = QFrame(self)
        layoutSB = QHBoxLayout()
        self.sbetweenFrame.setLayout(layoutSB)
        self.sblabel = QLabel(self.sbetweenFrame)
        self.sblabel.setText("The number of samples between pixels:")
        layoutSB.addWidget(self.sblabel)
        #TODO make variable
        self.sbwidget = QLabel(self.sbetweenFrame)
        self.sbwidget.setText(str(getLength(sound) // SoundExplorer.PIC_WIDTH))
        layoutSB.addWidget(self.sbwidget)
        layout.addWidget(self.sbetweenFrame)
        
        #Zoom row
        #TODO zoom
        
        #Resize the window
        self.resize(self.drawingPic.getWidth(), self.drawingPic.getHeight() + SoundExplorer.EXTRA_HEIGHT)
        #Remember the window
        keepAround.append(self)
        #Show the window
        self.show()
        self.activateWindow()
        self.raise_()
        self.activateWindow()
        QApplication.processEvents()
    
    #Update value position and show it
    def updateSelection(self):
        self.drawingPic = duplicatePicture(self.pic)
        #Draw the selection line
        x_coord = int(self.index * (SoundExplorer.PIC_WIDTH / getLength(self.sound)))
        addLine(self.drawingPic, x_coord, 0, x_coord, SoundExplorer.PIC_HEIGHT-1, cyan)
        pixmap = QPixmap.fromImage(self.drawingPic.image)
        self.picLabel.setPixmap(pixmap)
    
    # @pyqtSlot(int)
    # def test(self, x):
    #     print("hello " + str(x))
    
    #Position was updated via index box
    #Update things
    #@pyqtSlot()
    def updatedPos(self):
        #Only do this if we manually changed the numbers
        if not self.block_edit:
            #New index
            self.index = self.iwidget.value()
            self.value = getSampleValueAt(self.sound, self.index)
            self.vwidget.setText(str(self.value))
            #Update
            self.updateSelection()
            #Repaint the window
            self.update()
            QApplication.processEvents()
    
    #Clicked on image
    def imageClicked(self, pt):
        #Make sure we don't issue duplicate updates
        self.block_edit = True
        #Update the index
        self.index = int(pt.x() * (getLength(self.sound) / SoundExplorer.PIC_WIDTH))
        self.value = getSampleValueAt(self.sound, self.index)
        #Change the widgets to the new coords
        self.iwidget.setValue(self.index)
        self.vwidget.setText(str(self.value))
        #Update the stuff that can change
        self.updateSelection()
        #Repaint the window
        self.update()
        QApplication.processEvents()
        #Manual updates are safe again
        self.block_edit = False

#END OF SOUND

#Open explorer tool for media (currently only pictures and sound)
#Sound
def explore(media):
    if isinstance(media, Picture):
        openPictureTool(media)
    elif isinstance(media, Sound):
        openSoundTool(media)
    else:
        repValError("Exploration of this media is not supported")
        #raise ValueError

#Try to mimic functionality of JES picture explorer
#Done
def openPictureTool(picture):
    #import PictureExplorer
    thecopy = duplicatePicture(picture)
    #Constructor has side effect of showing it
    PictureExplorer(thecopy)
# 
# #    viewer.changeToBaseOne();
#     #viewer.setTitle(getShortPath(picture.getFileName() ))
#     pass #TODO
# 
# def openFrameSequencerTool(movie):
#     #FrameSequencerTool.FrameSequencerTool(movie)
#     pass #TODO

#Try to mimic functionality of JES sound explorer
def openSoundTool(sound):
    #import SoundExplorer
    thecopy = duplicateSound(sound)
    #Constructor has side effect of showing it
    SoundExplorer(thecopy)

# #Done
# def explore(someMedia):
#     if isinstance(someMedia, Picture):
#         openPictureTool(someMedia)
#     elif isinstance(someMedia, Sound):
#         openSoundTool(someMedia)
#     elif isinstance(someMedia, Movie):
#         openFrameSequencerTool(someMedia)
#     else:
#         print("explore(someMedia): Input is not a Picture, Sound, or Movie")
#         raise ValueError
# 
# # let's try the turtles...
# #import Turtle
# #import World
# #TODO use turtle package
# 
# def turn(turtle, degrees=90):
#     #if not isinstance(turtle, Turtle):
#     #    print "turn(turtle[, degrees]): Input is not a turtle"
#     #    raise ValueError
#     #else:
#     #    turtle.turn(degrees)
#     pass #TODO
# 
# def turnRight(turtle):
#     #if not isinstance(turtle,Turtle):
#     #    print "turnRight(turtle): Input is not a turtle"
#     #    raise ValueError
#     #else:
#     #    turtle.turnRight()
#     pass #TODO
# 
# def turnToFace(turtle, x, y=None):
#     #if y == None:
#     #    if not (isinstance(turtle, Turtle) and isinstance(x, Turtle)):
#     #        print "turnToFace(turtle, turtle): First input is not a turtle"
#     #        raise ValueError
#     #    else:
#     #        turtle.turnToFace(x)
#     #else:
#     #    if not isinstance(turtle, Turtle):
#     #        print "turnToFace(turtle, x, y): Input is not a turtle"
#     #        raise ValueError
#     #    else:
#     #        turtle.turnToFace(x, y)
#     pass #TODO
# 
# def turnLeft(turtle):
#     #if not isinstance(turtle, Turtle):
#     #    print "turnLeft(turtle): Input is not a turtle"
#     #    raise ValueError
#     #else:
#     #    turtle.turnLeft()
#     pass #TODO
# 
# def forward(turtle, pixels=100):
#     #if not isinstance(turtle,Turtle):
#     #    print "forward(turtle[, pixels]): Input is not a turtle"
#     #    raise ValueError
#     #else:
#     #    turtle.forward(pixels)
#     pass #TODO
# 
# def backward(turtle, pixels=100):
#     #if not isinstance(turtle, Turtle):
#     #    print "backward(turtle[, pixels]): Input is not a turtle"
#     #    raise ValueError
#     #if (None == pixels):
#     #    turtle.backward()
#     #else:
#     #    turtle.backward(pixels)
#     pass #TODO
# 
# def moveTo(turtle, x, y):
#     #if not isinstance(turtle,Turtle):
#     #    print "moveTo(turtle, x, y): Input is not a turtle"
#     #    raise ValueError
#     #turtle.moveTo(x,y)
#     pass #TODO
# 
# def makeTurtle(world):
#     #if not (isinstance(world, World) or isinstance(world, Picture)):
#     #    print "makeTurtle(world): Input is not a world or picture"
#     #    raise ValueError
#     #turtle = Turtle(world)
#     #return turtle
#     pass #TODO
# 
# def penUp(turtle):
#     #if not isinstance(turtle, Turtle):
#     #    print "penUp(turtle): Input is not a turtle"
#     #    raise ValueError
#     #turtle.penUp()
#     pass #TODO
# 
# def penDown(turtle):
#     #if not isinstance(turtle, Turtle):
#     #    print "penDown(turtle): Input is not a turtle"
#     #    raise ValueError
#     #turtle.penDown()
#     pass #TODO
# 
# def drop(turtle, picture):
#     #if not isinstance(turtle, Turtle):
#     #    print "drop(turtle, picture): First input is not a turtle"
#     #    raise ValueError
#     #if not isinstance(picture,Picture):
#     #    print "drop(turtle, picture): Second input is not a picture"
#     #    raise ValueError
#     #turtle.drop(picture)
#     pass #TODO
# 
# def getXPos(turtle):
#     #if not isinstance(turtle, Turtle):
#     #    print "getXPos(turtle): Input is not a turtle"
#     #    raise ValueError
#     #return turtle.getXPos()
#     pass #TODO
# 
# def getYPos(turtle):
#     #if not isinstance(turtle,Turtle):
#     #    print "getYPos(turtle): Input is not a turtle"
#     #    raise ValueError
#     #return turtle.getYPos()
#     pass #TODO
# 
# def getHeading(turtle):
#     #if not isinstance(turtle,Turtle):
#     #    print "getHeading(turtle): Input is not a turtle"
#     #    raise ValueError
#     #return turtle.getHeading()
#     pass #TODO
# 
# ## add these things: turnToFace(turtle, another turtle)
# ## getHeading, getXPos, getYPos
# 
# ## world methods
# def makeWorld(width=None, height=None):
#     #if(width and height):
#     #    w = World(width, height)
#     #else:
#     #    w = World()
#     #return w
#     pass #TODO
# 
# def getTurtleList(world):
#     #if not isinstance(world, World):
#     #    print "getTurtleList(world): Input is not a world"
#     #    raise ValueError
#     #return world.getTurtleList()
#     pass #TODO
# 
# # end of stuff imported for worlds and turtles
# 
# used in the book
#Done
#This is dumb
def printNow(text):
    print(text)
# 
# class Movie:
#     #TODO probably needs major overhaul
#     def __init__(self): # frames are filenames
#         self.frames = []
#         self.dir = None
# 
#     def addFrame(self, frame):
#         self.frames.append(frame)
#         self.dir = None
# 
#     def __len__(self):
#         return len(self.frames)
# 
#     def __str__(self):
#         return "Movie, frames: "+str(len(self))
# 
#     def __repr__(self):
#         return "Movie, frames: "+str(len(self))
# 
#     def __getitem__(self,item):
#         return self.frames[item]
# 
#     def writeFramesToDirectory(self, directory):
#         import FrameSequencer
#         fs = FrameSequencer(directory)
#         #for frameindex in range(0, self.listModel.size()):
#             #fs.addFrame(Picture(self.listModel.get(frameindex)))
#             #fs.play(self.fps)
#         for frameindex in range(0, len(self.frames)):
#             fs.addFrame(Picture(self.frames[frameindex]))
#         self.dir = directory
# 
#     def play(self):
#         import java.util.ArrayList as ArrayList
#         list = ArrayList()
#         for f in self.frames:
#             list.add( makePicture(f) )
#         MoviePlayer(list).playMovie()
# 
#     def writeQuicktime(self, destPath, framesPerSec = 16):
#         global mediaFolder
#         if not os.path.isabs(destPath):
#             destPath = mediaFolder + destPath
#         destPath = "file://"+destPath
#         if framesPerSec <= 0:
#             print("writeQuicktime(path[, framesPerSec]): Frame Rate must be a positive number")
#             raise ValueError
#         if self.frames == []: #Is movie empty?
#             print("writeQuicktime(path[, framesPerSec]): Movie has no frames. Cannot write empty Movie")
#             raise ValueError
#         elif self.dir == None and len(self.frames) == 1: #Is movie only 1 frame but never written out
#             frame = self.frames[0]
#             self.dir = frame[:(frame.rfind(os.sep))]
#         elif self.dir == None and len(self.frames) > 1: #Are movie frames all in the same directory? 
#             sameDir = 1
#             frame = self.frames[0]
#             frame = frame.replace('/', os.sep)
#             framesDir = frame[:(frame.rfind(os.sep))] #Parse directory of first frame
#             thisDir = framesDir
#             frameNum = 1
#             while(sameDir and frameNum < len(self.frames)):
#                 frame = self.frames[frameNum]
#                 frame = frame.replace('/', os.sep) #Eliminate possibility of / vs. \ causing problems
#                 thisDir = frame[:(frame.rfind(os.sep))]
#                 frameNum = frameNum+1
#                 if(framesDir != thisDir):
#                     sameDir = 0
#             if(sameDir): #Loop ended because we ran out of frames
#                 self.dir = framesDir
#             else: #Loop ended because sameDir became false
#                 print("writeQuicktime(path[, framesPerSec]): Your frames are in different directories. Call writeFramesToDirectory() first, then try again.")
#                 raise ValueError
#         writer = MovieWriter(self.dir, framesPerSec, destPath)
#         writer.writeQuicktime()
#         
#     def writeAVI(self, destPath, framesPerSec = 16):
#         global mediaFolder
#         if not os.path.isabs(destPath):
#             destPath = mediaFolder + destPath
#         destPath = "file://"+destPath
#         if framesPerSec <= 0:
#             print("writeAVI(path[, framesPerSec]): Frame Rate must be a positive number")
#             raise ValueError
#         if self.frames == []: #Is movie empty?
#             print("writeAVI(path[, framesPerSec]): Movie has no frames. Cannot write empty Movie")
#             raise ValueError
#         elif self.dir == None and len(self.frames) == 1: #Is movie only 1 frame but never written out
#             frame = self.frames[0]
#             self.dir = frame[:(frame.rfind(os.sep))]
#         elif self.dir == None and len(self.frames) > 1: #Are movie frames all in the same directory? 
#             sameDir = 1
#             frame = self.frames[0]
#             frame = frame.replace('/', os.sep)
#             framesDir = frame[:(frame.rfind(os.sep))] #Parse directory of first frame
#             thisDir = framesDir
#             frameNum = 1
#             while(sameDir and frameNum < len(self.frames)):
#                 frame = self.frames[frameNum]
#                 frame = frame.replace('/', os.sep)
#                 thisDir = frame[:(frame.rfind(os.sep))]
#                 frameNum = frameNum+1
#                 if(framesDir != thisDir):
#                     sameDir = 0
#             if(sameDir): #Loop ended because we ran out of frames
#                 self.dir = framesDir
#             else: #Loop ended because sameDir became false
#                 print("writeAVI(path[, framesPerSec]): Your frames are in different directories. Call writeFramesToDirectory() first, then try again.")
#                 raise ValueError
#         writer = MovieWriter(self.dir, framesPerSec, destPath)
#         writer.writeAVI()
# #Done
# def playMovie( movie ):
#     if isinstance( movie, Movie ):
#         movie.play()
#     else:
#         print("playMovie( movie ): Input is not a Movie")
#         raise ValueError
# 
# #Done
# def writeQuicktime(movie, destPath, framesPerSec = 16):
#     if not (isinstance(movie, Movie)):
#         print("writeQuicktime(movie, path[, framesPerSec]): First input is not a Movie")
#         raise ValueError
#     if framesPerSec <= 0:
#         print("writeQuicktime(movie, path[, framesPerSec]): Frame rate must be a positive number")
#         raise ValueError
#     movie.writeQuicktime(destPath, framesPerSec)
# 
# #Done
# def writeAVI(movie, destPath, framesPerSec = 16):
#     if not (isinstance(movie, Movie)):
#         print("writeAVI(movie, path[, framesPerSec]): First input is not a Movie")
#         raise ValueError
#     if framesPerSec <= 0:
#         print("writeAVI(movie, path[, framesPerSec]): Frame rate must be a positive number")
#         raise ValueError
#     movie.writeAVI(destPath, framesPerSec)
# 
# #Done
# def makeMovie():
#     return Movie()
# 
# #Done
# def makeMovieFromInitialFile(filename):
#     import re
#     movie = Movie()
# 
#     #filename = filename.replace(os.altsep, os.sep)
#     filename = filename.replace('/',os.sep) #Hack fix because os.altsep is not defined for Windows as of Python 2.2
#     sep_location = filename.rfind(os.sep)
#     if(-1 == sep_location):
#         filename = mediaFolder + filename
# 
#     movie.directory = filename[:(filename.rfind(os.sep))]
#     movie.init_file = filename[(filename.rfind(os.sep))+1:]
#     regex = re.compile('[0-9]+')
#     file_regex = regex.sub('.*', movie.init_file)
# 
#     for item in os.listdir(movie.directory):
#         if re.match(file_regex, item):
#             movie.addFrame(movie.directory + os.sep + item)
# 
#     return movie
# 
# #Done
# def addFrameToMovie(a, b):
#     frame = None
#     movie = None
#     if a.__class__ == Movie:
#         movie = a
#         frame = b
#     else:
#         movie = b
#         frame = a
# 
#     if not (isinstance(movie,Movie) and isinstance(frame,String)):
#    # if movie.__class__ != Movie or frame.__class__ != String:
#         print("addFrameToMovie(frame, movie): frame is not a string or movie is not a Movie object")
#         raise ValueError
# 
#     movie.addFrame(frame)
# 
# #Done
# def writeFramesToDirectory(movie, directory=None):
#     if not isinstance(movie, Movie):
#         print("writeFramesToDirectory(movie[, directory]): movie is not a Movie object")
#         raise ValueError
# 
#     if directory == None:
#         directory = user.home
# 
#     movie.writeFramesToDirectory(directory)
# 
# #def playMovie(movie):
# #    if not isinstance(movie, Movie):
# #        print "playMovie(movie): movie is not a Movie object."
# #        raise ValueError
# #    movie.play()
