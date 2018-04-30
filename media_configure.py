#This script lets the user select their media.py file, and then it adds
#its location to the Python path for the current session
#This allows the user to avoid having to put media.py in the same directory
#as any files that depend on it.
import sys
import os
import PyQt4.QtGui
# Create an PyQT4 application object.
#If we're running in Canopy, there already is one
root = PyQt4.QtGui.QApplication.instance()
if root is None:
    #We're not running in Canopy
    #Need to launch a new application
    root = PyQt4.QtGui.QApplication(sys.argv)
media = PyQt4.QtGui.QFileDialog.getOpenFileName(caption = "Select media.py", filter = "media.py")
if media != '':
    media_loc = media[:media.rfind(os.sep)+1]
    if media_loc not in sys.path:
        sys.path.append(media_loc)
    print("Success!")