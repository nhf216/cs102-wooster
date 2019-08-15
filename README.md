# cs102-wooster
The goal of this project is to take media programming functionality from Jython Environment for Students (JES) and implement it in Python 3 without Java. This codebase is used in CSCI 102: Multimedia Computing at The College of Wooster.

This code depends on `PyQt5` or on both `PyQt4` and `PIL`/`pillow`.  It supports `PyQt4` because we often run the code in Enthought Canopy in our course.  Canopy currently has `PyQt4` in its package manager, but it does not have `PyQt5` yet. The `PIL`/`pillow` dependency is also due to Canopy, in particular, a bug in their version of `PyQt4` that causes most common image formats, most notably JPEG, not to be supported on Windows. `PyQt5` support was added in December 2018 to facilitate portability of this module outside Canopy. It is still experimental; please report any bugs found.

## Installation
Since this module is intended for use by students with no prior programming experience, the recommended installation method is simple but inflexible. Simply download the file `media.py` and save it in the same directory as the Python program(s) you are working on, or in the same directory as your Python command-line session if not using Canopy. Then, you can import the `media` module as you would import any other module. If you are running a Python command-line session in a directory where `media.py` is not saved, you can run the script `media_configure.py` and browse to where you saved `media.py` to make Python "aware" of the `media` module for the current session, after which you can import `media` as normal.

## Notable Differences from JES
Most notably, this project uses Python 3, whereas JES uses Python 2. Aside from that, JES includes its own IDE designed to teach Python to the user and visually assist with programming. The `media` module here is derived from JES's `media` module, but we do not wrap ours in a custom IDE. Instead, our `media` module can be used with the user's IDE of choice. Some of the most helpful items from JES's drop-down menus are implemented by functions in our `media` module.

In addition, JES contains a debugger and gives simpler error messages when something goes wrong when running code. Our `media` module makes no effort, aside from descriptive error messages, to include a debugger or to deviate from standard Python error messages. In particular, students will rapidly become familiar with seeing stack traces. For beginners, use of an IDE with a simple debugger is recommended.

Some features of JES, particularly those that Wooster's course does not use, may be lacking functionality in our `media` module or be entirely absent. In particular, use caution when attempting to use functions in our codebase related to videos.

Finally, here are a few design choices that are different from JES:

- When working with color components outside of the range 0 to 255, JES takes the components mod 256, where `media` treats anything less than 0 as 0 and anything greater than 255 as 255.
- Avoid using the `sleep` function from Python's `time` module when creating animations with the `media` module. Instead, use the `media` module's own `sleep` function, which continues to play any currently playing sounds while waiting for the next image update.
- JES only supports JPEG images. Our `media` module supports most common image file types. PNGs are the most reliable, especially on Windows.
- JES only supports mono channel WAV sounds with 22050 samples per second. Our `media` module still only supports WAV files, but it supports a wider range of sample rates, and it supports stereo. Just be careful when operating on multiple sounds to ensure that they have the same metadata, or the result will be weird. When in doubt, it is recommended to use mono and 22050 samples per second for everything.

## Notable Additions to JES
Our codebase implements a number of additional media functions that JES does not have.

- `savePicture(picture)` and `saveSound(sound)`: These functions allow you to save a Picture or a Sound object that you've been working with using a file save dialog. They are analogous to the JES (and `media`) function `pickAFile()` that allows you to choose a file from a file open dialog.
- `pickASaveFile()`: This function works like `pickAFile` in that it opens a file chooser dialog, lets you choose a file, and returns the path of the chosen file. This function uses a save dialog rather than an open dialog. It does not actually save anything; it just returns the chosen path.
- `copyIntoWithCutoff(smallPicture, bigPicture, startX, startY)`: This works exactly like the JES (and `media`) function `copyInto`, but it lets you copy an image into another image where part of the copied image would go off the background image.
- `getRedComponent(color)`, `getGreenComponent(color)`, `getBlueComponent(color)`: These function allow accessing the components of a Color object.
- `explore(media)`: This function, which can take a Picture or Sound object as input, simulates JES's picture and sound explorers from its MediaTools menu. The sound explorer in particular is not quite as high quality as JES's sound explorer.
- `printSoundMetadata(sound)`: This function displays some useful information about a Sound object.
- `getSampleSize(sample)`: This function returns the number of bits in the given Sample object.
- `getSampleIndex(sample)`: This function, analogous to `getX(pixel)` and `getY(pixel)` for Pixels, returns the index of the given Sample object in its Sound.
- `pureTone(freq, amp, dur)`: Generates a pure tone of the specified frequency, amplitude, and duration.
- `printPicture(picture)`: If using Canopy and if `PIL`/`pillow` is installed, using this function in the command prompt portion of the GUI will display the given Picture object in the command prompt instead of in a separate window. Otherwise, do not use this function.
