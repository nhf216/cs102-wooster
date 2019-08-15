#This script lets the user select their media.py file, and then it adds
#its location to the Python path for the current session
#This allows the user to avoid having to put media.py in the same directory
#as any files that depend on it.
import sys
import os
try:
    import PyQt5.QtWidgets as QtGui
except ImportError:
    import PyQt4.QtGui as QtGui
# Create an PyQT4tg in Canopy, there already is one
root = QtGui.QApplication.instance()
if root is None:
    #We're not running in Canopy
    #Need to launch a new application
    root = QtGui.QApplication(sys.argv)
media = QtGui.QFileDialog.getOpenFileName(caption = "Select media.py", filter = "media.py")
if media != '':
    if isinstance(media, tuple):
        media = media[0]
    media_loc = media[:media.rfind(os.sep)+1]
    if media_loc not in sys.path:
        sys.path.append(media_loc)
    print("Success!")
