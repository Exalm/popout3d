#! /usr/bin/python3
'''
--------------------------------------------------------------------------------
Popout3D Stereo Image Creation

Copyright 2015-2018 Chris Rogers <popout3d@yahoo.com>

GNU GENERAL PUBLIC LICENSE GPLv3

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have a copy of the GNU General Public License
    in /usr/share/common-licenses/GPL-3. If not, 
    see <http://www.gnu.org/licenses/>.

--------------------------------------------------------------------------------
Useful - symbolic link ln -fs "/usr/share/popout3d/popout3d.py" "/usr/bin/popout3d"
      Needs removing after removing package.

Files:
    help, preferences, icon, startscreen
    program, ui program (ui bytecode gets created automatically)

--------------------------------------------------------------------------------
V1.1 changes from V1.0
Addition of image display

V1.1.1 changes from V1.1
When changing file, folder or view, change viewind to -1 to make sure it starts on firstview image.
Revise selection of files.
Image view ration 3:4.
Show new images.
avail
V1.2
Remove print statements including one in statusbar.
Remove self.tr
Change gui from .ui to .py.
Change version check in preferences upload to '1'.
Improve some messages.
Move messages from textEdit box to StatusBar and file/folder info to title bar
Add directories to lists.
For Python3:
    Change xrange to range.
    Update dependencies.
    Change to /usr/bin/python3.
    From PyQt5 import QtCore, QtGui, Qtmenuitems and change QtGui to Qtmenuitems in several places.
    Scale image display.
    Separate data folder.

V1.3
Used fuser for locking

V1.3.1
Switch from ImageMagick/Wadd to Python PIL (or pillow).
Make sure image folder is always created.
Comments.
Improve file locking.

V1.4 3/2/2016
Changed File to Set
Corrected global variables and passed parameters.
Tidied up the defs which choose view style and left/right so they scroll through images more neatly.
Separate def for loading preferences.
Revised preferences file.
Rearranged options on GUI into two columns and added progress panel and image title.
Remove most progress messages which were unhelpful.
Gtk option.
Switched spawned file from Bash to Python and added merge process to it.
Set maximum size of image display.
Remove old config files.

V1.4.1 28/3/2017
Remove previous files from view panel when processing.
Remove '>' from message about Forward button.
In Debreate - add email to description.
            - change architecture to amd64

V1.4.2 11/04/2017
Convert statusbar messages to popups.
Don't allow starting processing again if processing is already running.
Use gi.require_version('Gtk', '3.0')
Clear image when deleting file.
viewImage split into findImage and viewImage.  
Stop picture making window bigger than screen - Change picture size when window size changes.
Sort out firstview variable
Start window maximized.
Increase startup image size, don't show filename.
Fix radio buttons.

V1.4.3 
Fix variable name in popout3d_spawn.py. (08/05/2017 1.4.2-1 on GetDeb)
Email address on startup image. (08/05/2017 1.4.2-1 on GetDeb)
No need to import 'time'.
Change email address 08/01/2018 (1.4.2-2 on GetDeb NOT YET)
Remove '.' from name of workfile. 
'''

import sys, os, shutil, subprocess #1.4.3 , time
from PIL import Image

# qt ***************************************************************************
#from PyQt5 import QtCore, QtGui, Qtmenuitems 
#from popout3d_ui import Ui_window1
# gtk **************************************************************************

#V1.4.2
try:
    import gi
except:
    sys.exit('Failed to import gi')

try:
    gi.require_version('Gtk', '3.0')
except:
    sys.exit('gi wrong version')
#V1.4.2

from gi.repository import Gtk, GdkPixbuf
# ******************************************************************************

# create global variables and set default values
form = ''                                               # format in words
formlet = ''                                            # firstview letter of format
style = ''                                              # style in words
stylelet = ''                                           # firstview letter of style
stylecode = ''                                          # style in align-image-stack code

viewlist = []                                           # list of images to view
viewind = -1                                            # array index of image to view
firstview = True #V1.4.2
startupimage = True  #V1.4.2
setprefs = True #V1.4.2
version = 'Popout3D V1.4.2'                             # program version
progdir = '/usr/share/popout3d/'                        # program folder                                           
preffile = 'popout3d.dat'                               # name of user preference file
helpfile = 'popout3d_help.html'                         # name of help file
startfile = 'popout3d_start.png'                        # name of image file shown at startup
homedir = os.getenv('HOME') + '/'                       # get homedir folder
prefdir = homedir + 'popout3d/'                         # folder for preference file #1.4.3 remove dot
workdir = homedir + 'popout3d/work/'                    # folder for images being worked on #1.4.3 remove dot
mydir = homedir                                         # set current folder
myfile = '{none}'                                       # current file
myext = '{none}'                                        # current extentsion
spawnprog = 'popout3d_spawn.py'                         # name of spawned program
spawnlock = 'spawn.lock'                                # name of lock file spawned progam
spawntext = 'spawn.txt'                                 # name of text output file from spawned progam
# statusmessage = ''                                    # message for statusbar ~~~~~

os.chdir(mydir)                                         # start in mydir folder


def getPreferences():
    global version, mydir, myfile, myext, form, formlet, style, stylelet, stylecode, view

    # create hidden folder
    if not os.path.isdir(prefdir):
        result = os.system('mkdir '+ prefdir)
        if result != 0:
            sys.exit(result)                                           

    # create data folder
    if os.path.isdir(workdir):
        shutil.rmtree(workdir, True)

    result = os.system('mkdir '+ workdir)
    if result != 0:
        sys.exit(result)

    # copy default preferences file to preference folder
    if not os.path.isfile(prefdir + preffile):
        shutil.copyfile(progdir + preffile, prefdir + preffile)

    # create preferences array
    prefdata = []
    for i in range(7):
        prefdata.append('')

    # load preferences file
    with open(prefdir + preffile, 'r') as infile:
        for i in range(0, 7):
            prefdata[i] = infile.readline() ; prefdata[i] = prefdata[i][:-1] # take linefeed off end of string

    # set preferences data
    if prefdata[0] == 'Popout3D V1.4.2':

        version = prefdata[0]

        if os.path.exists(prefdata[1]):
            mydir = prefdata[1]
        else:
            mydir = homedir

        myfile = prefdata[2] ; myext = prefdata[3]

        if prefdata[4] in ['Anaglyph', 'Side-by-Side', 'Crossover']:
            form = prefdata[4]
        else:
            form = 'Anaglyph'

        if prefdata[5] in ['Level','Popout']:
            style = prefdata[5]
        else:
            style = 'Level'

        if prefdata[6] in ['New','Set','Folder']:
            view = prefdata[6]
        else:
            view = 'Folder'

    else:
        # copy default preferences file and use standard values this time
        shutil.copyfile(progdir + preffile, prefdir + preffile)

        mydir = homedir
        myfile = '{none}'
        myext = '{none}'
        form = 'Anaglyph'
        style = 'Level'
        view = 'New'

    formlet = form[0:1] ; stylelet = style[0:1]
    if style == 'Level':
        stylecode = 'A'
    else:
        stylecode = 'P'

''' ~~~~~
def showstatus(self, which, message):
    # global statusmessage #V1.4.2

    if which == 'new':
        statusmessage = message
    else:
        statusmessage = statusmessage + message

    if len(statusmessage) > 150:
        statusmessage = statusmessage.partition('. ')[2] # drop firstview sentence

    #self.statusBar().showMessage(statusmessage) # qt *****
    self.labelStatusbar.set_text(statusmessage) # gtk *****
'''
def showTitle(self, message):
    #self.setWindowTitle(message) # qt *****
    self.window.set_title(message) # gtk *****

def showTip(self):
    if view == 'New':
        #self.ui.??.setText('New Images') # qt *****
        self.labelView.set_label('New Images') # gtk *****
    elif view == 'Folder':
        #self.ui.??.setText('Images in this Folder') # qt *****
        self.labelView.set_label('Images in this Folder') # gtk *****
    else: # File
        #self.ui.??.setText('Images in this Set') # qt *****
        self.labelView.set_label('Images in this Set') # gtk *****

def clearImage(self):
    # qt ***********************************************************************
    # here clear image1 label
    # self.ui.label.clear()
    # gtk **********************************************************************
    self.image1.clear()
    self.labelImage1.set_text('')
    # **************************************************************************

def showMessage(self, which, message):
    # qt ***********************************************************************
    '''
    if which == 'warn':
        result = Qtmenuitems.QMessageBox.question(self, 'Warning', message, Qtmenuitems.QMessageBox.Close)
    else: # 'ask'
        result = Qtmenuitems.QMessageBox.question(self, 'Are you sure?', message, Qtmenuitems.QMessageBox.No, Qtmenuitems.QMessageBox.Yes)
        if result == 16384:
            return('Y')
        else:
            return('N')
    '''        
    # gtk **********************************************************************
    if which == 'warn':
        self.messageWarning.format_secondary_text(message)
        self.result = self.messageWarning.run() ; self.messageWarning.hide()
    else: # 'ask'
        self.messageQuestion.format_secondary_text(message)
        self.result = self.messageQuestion.run() ; self.messageQuestion.hide()
        if self.result == Gtk.ResponseType.YES:
            return('Y')
        else:
            return('N')
        
    # **************************************************************************

#===============================================================================
# progress panels GTK - no Qt written
def showProgress(self):

    showTip(self)
    # queuing and processing
    if view == 'New':

        # queuing
        dirlist = ''
        for filename in os.listdir(workdir):
            newfile, newext = os.path.splitext(filename) 
            if newext == '.queue':
                dirlist = dirlist + newfile+'\n'
        self.labelQueuing.set_text(dirlist) 

        # processing
        dirlist = ''
        for filename in os.listdir(workdir):
            newfile, newext = os.path.splitext(filename) 
            if newext == '.process':
                dirlist = dirlist + newfile+'\n'
        self.labelProcessing.set_text(dirlist) 

    else: # Folder or Set

        # queuing
        self.labelQueuing.set_text('') 

        # processing
        self.labelProcessing.set_text('') 

    # viewing
    dirlist = ''
    for i in viewlist:
        f = '3D'+i[0]+'.'+i[1]
        dirlist = dirlist + f +'\n'
    self.labelViewing.set_text(dirlist) 

#===============================================================================
# make list of viewable 3D images, merge one aligned pair if available
def makeViewlist(self):
    global viewlist, viewind
    
    clearImage(self)
    viewlist = []

    if view == 'New':
        # dirlist = '' #V1.4.1
        for filename in os.listdir(workdir):
            newfile, newext = os.path.splitext(filename)
            if newext == '.view':
                newfile, newext = os.path.splitext(newfile)
                viewlist.append([newfile, newext[1:]])
    else:
        # search through myDir for suitable files
        for newfile in os.listdir(mydir):
            if (newfile[0:2] == '3D'
              and (newfile.endswith('.jpg') or newfile.endswith('.JPG')
              or newfile.endswith('.tiff') or newfile.endswith('.TIFF')
              or newfile.endswith('.tif') or newfile.endswith('.TIF')
              or newfile.endswith('.png') or newfile.endswith('.PNG'))):
                newfile, newext = os.path.splitext(newfile)

                if (view == 'Set' # only add file to viewlist if it is selected file
                  and myfile == newfile[2:len(myfile)+2] and myext == newext[1:]):
                    viewlist.append([newfile[2:], newext[1:]])
                elif view == 'Folder': # only add file to viewlist if it is in selected folder
                    viewlist.append([newfile[2:], newext[1:]])

        viewlist = sorted(viewlist)
        viewind = 0

#===============================================================================
# View image #V1.4.2
def viewImage(self, fn):
    global startupimage
    # qt ***************************************************************
    '''
    # here show current image name
    #myPixmap = QtGui.QPixmap(mydir+'3D'+viewlist[viewind][0]+'.'+viewlist[viewind][1])
    myPixmap = QtGui.QPixmap(fn)
    myPixmap = myPixmap.scaledToWidth(1000)
    self.ui.label.setPixmap(myPixmap)
    '''
    # gtk **************************************************************
    #self.labelImage1.set_text('3D'+viewlist[viewind][0]+'.'+viewlist[viewind][1]) #V1.4.2
    #pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(mydir+'3D'+viewlist[viewind][0]+'.'+viewlist[viewind][1], 900, 550, True) # width, height, preserve_active_ratio #V1.4.2

    self.labelImage1.set_text(fn) #V1.4.2
    
    # get size of window

    if startupimage:
        self.labelImage1.set_text('') #V1.4.2
        w = 2000 ; h = 750 ; startupimage = False
    else:
        self.labelImage1.set_text(fn) #V1.4.2
        allocation = self.alignment1.get_allocation()
        w = allocation.width-25; h = allocation.height-25

    # retrieve image and adjust
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(fn, w, h, True) # file, width, height, preserve_active_ratio
    self.image1.set_from_pixbuf(pixbuf)
# ******************************************************************
        
#===============================================================================
# Check value of viewlist indicator, then show image 
# Check value of viewlist indicator, then find image #V1.4.2
def findImage(self): #V1.4.2
    global viewind

    # make sure viewing list indicator hasn't gone off the end
    if viewind < 0:
        viewind = 0
    elif viewind > len(viewlist) -1:
        viewind = len(viewlist) -1

    # provided viewing list isn't empty, select the currently indicated image from the viewlist #V1.4.2 and show it.
    if len(viewlist) > 0:
        if os.path.isfile(mydir+'3D'+viewlist[viewind][0]+'.'+viewlist[viewind][1]):
            viewImage(self, mydir+'3D'+viewlist[viewind][0]+'.'+viewlist[viewind][1])

#===============================================================================
# check each pair of images is valid, then write a .queue file
def processPair(self, newfile, newext, leftn, rightn):
    # global statusmessage #V1.4.2, newlist

    imageL = mydir+newfile+str(leftn)+'.'+newext
    imageR = mydir+newfile+str(rightn)+'.'+newext

    # open images and get image type and size
    try:
        img = Image.open(imageL)
    except:
        print ('Unable to load left image')
        sys.exit()
    img.load()
    imageLF = img.format ; imageLS = img.size

    try:
        img = Image.open(imageR)
    except:
        print ('Unable to load right image')
        sys.exit()
    img.load()
    imageRF = img.format ; imageRS = img.size

    # images match on type an size align them, else warn they are incompatible and skip them
    if imageLF == imageRF and imageLS == imageRS:

        # if there are no lock files, call the alignment program
        # Quotes are used around the filenames to deal with special characters like "("

        queuefile = workdir+newfile+str(leftn)+'+'+str(rightn)+formlet+stylelet+'.'+newext+'.queue'
        if not os.path.isfile(queuefile):
            with open(queuefile, 'w') as fn:
                fn.write('')
            #showstatus(self,'new','To update the progress panels press [Forward]. ') #V1.4.2

    else:
        if imageLF != imageRF:
            #result = Qtmenuitems.QMessageBox.question(self, 'Warning', 'Files ' + newfile+str(leftn)+'.'+newext + ' and ' + newfile+str(rightn)+'.'+newext + ' can not be used, they are different filetypes. ', Qtmenuitems.QMessageBox.Close)
            showMessage(self,  'warn', 'Cannot use ' + newfile+str(leftn)+'.'+newext + ' and ' + newfile+str(rightn)+'.'+newext + ' , they are different filetypes. ')
        if imageLS != imageRS:
            #result = Qtmenuitems.QMessageBox.question(self, 'Warning', 'Files ' + newfile+str(leftn)+'.'+newext + ' and ' + newfile+str(rightn)+'.'+newext + ' can not be used, they are different sizes. ', Qtmenuitems.QMessageBox.Close)
            showMessage(self, 'warn' + newfile+str(leftn)+'.'+newext + ' and ' + newfile+str(rightn)+'.'+newext + ' can not be used, they are different sizes. ')

#===============================================================================
# loop through set of images to call processPair for each valid pair
def processSet(self, newfile, newext):

    # global statusmessage #V1.4.2    

    # find out how many images there are in this set
    imagestodo = 0 # count of number of input files
    for i in range (0, 9):
        if os.path.isfile(mydir+newfile+str(i)+'.'+newext):
            imagestodo = imagestodo + 1

    # if there are at least two images in the set, repeatedly call processPair to process them, else warning statusmessage
    if imagestodo == 0:
        pass # showstatus(self, 'new', 'There are no suitable images in the set ' + newfile + '*.' + newext + '. ')
    elif imagestodo == 1:
        pass # showstatus(self, 'new', 'There is only one file in the set ' + newfile + '*.' + newext + ', at least two are needed. ')
    else:
        # loop through all valid image pairs

        leftn = 0 ; rightn = 1 # left and right image numbers
        while leftn < 9: # can only deal with single digit image numbers

            rightn = leftn + 1
            while rightn < 10: # highest possible image number is 9

                # both files exist but so does a 3D file so do nothing
                if (os.path.isfile(mydir+newfile+str(leftn)+'.'+newext) and os.path.isfile(mydir+newfile+str(rightn)+'.'+newext)
                  and os.path.isfile(mydir+'3D'+newfile+str(leftn)+'+'+str(rightn)+formlet+stylelet+'.'+newext)):
                    # showstatus(self, 'add', '3D'+newfile+str(leftn)+'+'+str(rightn)+formlet+stylelet+'.'+newext+' already exists. ') #V1.4.2
                    showMessage(self, 'warn', '3D'+newfile+str(leftn)+'+'+str(rightn)+formlet+stylelet+'.'+newext+' already exists. ') #V1.4.2

                # both files exist and there is no 3D file
                elif (os.path.isfile(mydir+newfile+str(leftn)+'.'+newext) and os.path.isfile(mydir+newfile+str(rightn)+'.'+newext)
                  and not os.path.isfile(mydir+'3D'+newfile+str(leftn)+'+'+str(rightn)+formlet+stylelet+'.'+newext)):
                    processPair(self, newfile, newext, leftn, rightn)
        
                # else there is a gap in the sequence so do nothing

                rightn = rightn + 1
            leftn = leftn + 1

# qt ***************************************************************************
# Load the UI, define UI class and actions
'''
class MyWindowClass(Qtmenuitems.QMainWindow):
    def __init__(self, parent = None):
        Qtmenuitems.QMainWindow.__init__(self, parent)
        self.ui = Ui_window1()

        self.ui.setupUi(self)
        # Bind the event handlers to the radio buttons, no need for Quit as it is handled by GUI
        self.ui.imagemenuitemFolder.triggered.connect(self.imagemenuitemFolder)
        self.ui.imagemenuitemSet.triggered.connect(self.imagemenuitemSet)
        self.ui.imagemenuitemPreferences.triggered.connect(self.imagemenuitemPreferences)
        self.ui.imagemenuitemHelp.triggered.connect(self.imagemenuitemHelp)
        self.ui.imagemenuitemAbout.triggered.connect(self.imagemenuitemAbout)

        self.ui.radiobuttonAnaglyph.clicked.connect(self.radiobuttonAnaglyph)
        self.ui.radiobuttonSidebyside.clicked.connect(self.radiobuttonSidebyside)
        self.ui.radiobuttonCrossover.clicked.connect(self.radiobuttonCrossover)
        self.ui.radiobuttonLevel.clicked.connect(self.radiobuttonLevel)
        self.ui.radiobuttonPopout.clicked.connect(self.radiobuttonPopout)
        self.ui.radiobuttonNew.clicked.connect(self.radiobuttonNew)
        self.ui.radiobuttonSet.clicked.connect(self.radiobuttonSet)
        self.ui.radiobuttonFolder.clicked.connect(self.radiobuttonFolder)
        self.ui.buttonFolder.clicked.connect(self.buttonFolder)
        self.ui.buttonSet.clicked.connect(self.buttonSet)
        self.ui.buttonBack.clicked.connect(self.buttonBack)
        self.ui.buttonForward.clicked.connect(self.buttonForward)
        self.ui.buttonDelete.clicked.connect(self.buttonDelete)
        self.ui.fileDialog = Qtmenuitems.QFileDialog(self)
        '''
# gtk ******************************************************************
class GUI:
    def __init__(self):
        global firstview, setprefs

        self.gladefile = progdir+'popout3d.glade'

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)

        self.window = self.builder.get_object('window1')
        self.labelImage1 = self.builder.get_object('labelImage1')
        self.window.show()
        self.builder.connect_signals(self)


        # self.labelStatusbar = self.builder.get_object('labelStatusbar') #V1.4.2
        self.labelQueuing = self.builder.get_object('labelQueuing')
        self.labelProcessing = self.builder.get_object('labelProcessing')
        self.labelViewing = self.builder.get_object('labelViewing')
        self.labelView = self.builder.get_object('labelView')

        self.messageQuestion = self.builder.get_object('messagedialogQuestion')
        self.messageWarning = self.builder.get_object('messagedialogWarning')
        self.dialogboxAbout = self.builder.get_object('dialogboxAbout')
        self.dialogHelp = self.builder.get_object('dialogHelp')
        self.image1 = self.builder.get_object('image1')
        self.alignment1 = self.builder.get_object('alignment1') #V1.4.2 for available size

        self.labelBack = self.builder.get_object('buttonBack')
        self.labelForward = self.builder.get_object('buttonForward')

        self.activeAnaglyph = self.builder.get_object('radiobuttonAnaglyph')
        self.activeSidebyside = self.builder.get_object('radiobuttonSidebyside')
        self.activeCrossover = self.builder.get_object('radiobuttonCrossover')

        self.activeLevel = self.builder.get_object('radiobuttonLevel')
        self.activePopout = self.builder.get_object('radiobuttonPopout')

        self.activeNew = self.builder.get_object('XradiobuttonNew')
        self.activeFolder= self.builder.get_object('radiobuttonFolder')
        self.activeSet = self.builder.get_object('radiobuttonSet')

        # **********************************************************************        

        # set preference variables and set title
        getPreferences()     
        showTitle(self, version + '          Folder: ' + mydir + '          File Set: ' + myfile + '*.' + myext)

        # qt *******************************************************************
        '''
        if form == 'Anaglyph':
            self.ui.radiobuttonAnaglyph.setChecked(True)
        elif form == 'Side-by-Side':
            self.ui.radiobuttonSidebyside.setChecked(True)
        else:
            self.ui.radiobuttonCrossover.setChecked(True)

        if style == 'Level':
            self.ui.radiobuttonLevel.setChecked(True)
        else:
            self.ui.radiobuttonPopout.setChecked(True)

        if view == 'Folder':
            self.ui.radiobuttonFolder.setChecked(True)          
        elif view == 'Set':
            self.ui.radiobuttonSet.setChecked(True)
        else:
            self.ui.radiobuttonNew.setChecked(True)
            self.ui.tip.setText('Merge')
        '''
        # gtk ******************************************************************
        # activating any of these triggers the one activated and the one de-activated
        
        if form == 'Anaglyph':
            self.activeAnaglyph.set_active(True)
        elif form == 'Side-by-Side':
            self.activeSidebyside.set_active(True)
        else:
            self.activeCrossover.set_active(True)

        if style == 'Level':
            self.activeLevel.set_active(True)
        else:
            self.activePopout.set_active(True)
        
        setprefs = True
        if view == 'New':
            self.activeNew.set_active(True)
        elif view == 'Folder':
            self.activeFolder.set_active(True)
        else:
            self.activeSet.set_active(True)
        setprefs = False
        
        self.window.maximize() #V1.4.2

        # quickstart image
        if os.path.isfile(progdir+startfile):
            viewImage(self, progdir+startfile) #V1.4.2

    # ==========================================================================
    # definitions ==============================================================

    # qt ***********************************************************************
    '''
    No need for window destroy, imagemenuitemQuit or Quit button definition as it is handled by GUI
    '''
    # gtk **********************************************************************
    def on_window1_destroy(self, object): # close window with 0 or X
        Gtk.main_quit()

    def imagemenuitemQuit(self, menuitem): # quit with File>Quit
        Gtk.main_quit()
       
    def buttonQuit(self, menuitem): # quit with Quit button
        Gtk.main_quit()
    # **************************************************************************
    
    # menu bar choose folder
    def imagemenuitemFolder(self, menuitem):
        global mydir, myfile, myext # statusmessage #V1.4.2

        # qt *******************************************************************
        # newdir = Qtmenuitems.QFileDialog.getExistingDirectory(self, 'Select the Folder where the images are', directory = homedir) 
        # gtk ******************************************************************
        filechooserdialog = Gtk.FileChooserDialog(title='Select the Folder where the images are',
          action=Gtk.FileChooserAction.SELECT_FOLDER,
          parent=self.window,
          buttons=["Cancel", Gtk.ResponseType.CANCEL, "Select",Gtk.ResponseType.OK])
        filechooserdialog.set_current_folder (mydir)
        response = filechooserdialog.run()    
        filechooserdialog.hide()

        if response == Gtk.ResponseType.OK:
            newdir = filechooserdialog.get_filename()
        else: # answered No or closed window
            newdir = '{none}'   
        
        # **********************************************************************
        newdir = newdir+'/'
        if newdir[0:len(homedir)] == homedir:
            mydir = newdir; os.chdir(mydir) # filename is original name less ending digit
            myfile = '{none}' ;  myext = '{none}' # as it may be a set which is not in the new folder
        else:
            showMessage(self, 'warn', 'Folder not changed')

        showTitle(self, version + '          Folder: ' + mydir + '          File Set: ' + myfile + '*.' + myext)
        # update viewlist
        makeViewlist(self)
        findImage(self)
        showProgress(self)

    # menu bar choose set
    def imagemenuitemSet(self, menuitem):
        global mydir, myfile, myext # statusmessage #V1.4.2

        # qt *******************************************************************
        '''
        newfile, _ = Qtmenuitems.QFileDialog.getOpenFileName(self, 'Select any file from a set of images', folder = mydir, filter = '*.jpg *.JPG *.jpeg *.JPEG *.tiff *.TIFF *.tif *.TIF *.png *.PNG')
        newfile = str(newfile) # filename is not string type
        '''
        # gtk ******************************************************************
        filechooserdialog = Gtk.FileChooserDialog(title="Select any file from a set of images",
          action=Gtk.FileChooserAction.OPEN, 
          parent=self.window,
          buttons=["Cancel", Gtk.ResponseType.CANCEL, "Select",Gtk.ResponseType.OK])
        filechooserdialog.set_current_folder (mydir)
        fileFilter = Gtk.FileFilter() ; fileFilter.add_pattern('*.JPG') ; fileFilter.set_name('Image files') ; filechooserdialog.add_filter(fileFilter)
        response = filechooserdialog.run()    
        filechooserdialog.hide()
        
        if response == Gtk.ResponseType.OK:
            newfile = filechooserdialog.get_filename()
        else: # answered No or closed window
            newfile = '{none}'   
        
        # **********************************************************************

        if newfile[0:len(homedir)] == homedir:
            newdir, newfile = os.path.split(newfile)
            if newfile[0:2] != '3D':
                os.chdir(newdir)
                newfile, newext = os.path.splitext(newfile)
                if newfile[len(newfile)-1:] in ['0','1','2','3','3','5','6','7','8','9']:
                    mydir = newdir +'/' ; myfile = newfile[:-1]; myext = newext[1:] # filename is original name less ending digit
                else:
                    showMessage(self, 'warn', 'Filename must end in a digit.')       

        if myfile == '':
            myfile = '{none}' ; myext = '{none}'
            showMessage(self, 'warn', 'No file selected')
        else:
            showTitle(self, version + '          Folder: ' + mydir + '          File Set: ' + myfile + '*.' + myext)
            # update viewlist
            makeViewlist(self)
            findImage(self)
            showProgress(self)

    # menu bar save preferences
    def imagemenuitemPreferences(self, menuitem):
        result = showMessage(self, 'ask', 'This will save your current settings as the defaults.')
        if result == 'Y':
            with open(prefdir + preffile, 'w') as fn:
                fn.write(version+'\n')
                fn.write(mydir+'\n')
                fn.write(myfile+'\n')
                fn.write(myext+'\n')
                fn.write(form+'\n')
                fn.write(style+'\n')
                fn.write(view+'\n')

    # menu bar help
    def imagemenuitemHelp(self, menuitem):

        # qt *******************************************************************
        '''
        self.helpPanel = Qtmenuitems.QDialog()
        self.helpPanel.setModal(True)
        self.helpPanel.setWindowTitle('Help')
        helptext = Qtmenuitems.QTextEdit(self.helpPanel)
        with open(progdir + helpfile, 'r') as infile:
            result = infile.read()
        helptext.setHtml(result)
        helptext.setReadOnly(-1)
        helptext.resize(800, 500)
        self.helpPanel.show()
        helptext.show()
        '''
        # Gtk*******************************************************************
        self.response = self.dialogHelp.run() ; self.dialogHelp.hide()
        # **********************************************************************

    # menu bar about
    def imagemenuitemAbout(self, menuitem):
        # qt ******************************************************************
        '''
        result = Qtmenuitems.QMessageBox.about(self, 'About this program',
            '       '+version+'\n'+
            '     Stereo Image Creation\n\n'+
            'Copyright (C) 2015 Chris Rogers\n'+
            ' GNU GENERAL PUBLIC LICENSE\n\n'+
            '  The clever stuff is done by\n'+
            '    Hugin - Image Alignment\n'+
            ' http://hugin.sourceforge.net/')
        '''
        # gtk ******************************************************************
        
        self.response = self.dialogboxAbout.run() ;    self.dialogboxAbout.hide()
        
        # **********************************************************************
        
    # form actions
    def radiobuttonAnaglyph(self, menuitem):
        global form, formlet
        if menuitem.get_active():
            form = 'Anaglyph' ; formlet = 'A'

    def radiobuttonSidebyside(self, menuitem):
        global form, formlet
        if menuitem.get_active():
            form = 'Side-by-Side' ; formlet = 'S'

    def radiobuttonCrossover(self, menuitem):
        global form, formlet
        if menuitem.get_active():
            form = 'Crossover' ; formlet = 'C'

    # style actions
    def radiobuttonLevel(self, menuitem):
        global style, stylelet, stylecode
        if menuitem.get_active():
            style = 'Level' ; stylelet = 'L' ; stylecode = 'A'

    def radiobuttonPopout(self, menuitem):
        global style, stylelet, stylecode
        if menuitem.get_active(): 
            style = 'Popout' ; stylelet = 'P' ; stylecode = 'P'

    '''
    # process folder #V1.4.2
    def buttonFolder(self, menuitem):
        # global statusmessage #V1.4.2
        # showstatus(self, 'new', '') # qt was self.statusBar().clearMessage() #V1.4.2

        todolist = []; 
        for newfile in os.listdir(mydir):
            if (newfile[0:2] != '3D' and
                    (newfile.endswith('.jpg') or newfile.endswith('.JPG')
                    or newfile.endswith('.tiff') or newfile.endswith('.TIFF')
                    or newfile.endswith('.tif') or newfile.endswith('.TIF')
                    or newfile.endswith('.png') or newfile.endswith('.PNG'))):
                newfile, newext = os.path.splitext(newfile)
                if newfile[-1:] in ['0','1','2','3','3','5','6','7','8','9'] and [newfile[:-1], newext[1:]] not in todolist:
                    todolist.append([newfile[:-1], newext[1:]])

        todolist = sorted(todolist)

        if todolist != []:

            for newfile in todolist:
                # filename style is name less last digit - there's no 3D at the beginning
                processSet(self, newfile[0], newfile[1])

            # run spawnprog if not already running
            if os.path.isfile(workdir+spawnlock):
                # showstatus(self,'new','Processing already running.') #V1.4.2
                showMessage(self, 'warn', 'Processing already running.') #V1.4.2
            else:
                with open(workdir+spawntext, 'w') as f: # output to text file
                    subprocess.Popen([progdir+spawnprog, workdir, mydir], stdout = f) # run spawnprog
        else:
            showMessage(self, 'warn', 'There are no suitable files.')

        # remove .view files #V1.4.1
        for fn in os.listdir(workdir):
            dummy, fx = os.path.splitext(fn) 
            if fx == '.view':
                os.remove(workdir+fn)
        makeViewlist(self)
        showProgress(self)
    '''

    # process folder #V1.4.2
    def buttonFolder(self, menuitem):
        # global statusmessage #V1.4.2
        # showstatus(self, 'new', '') # qt was self.statusBar().clearMessage() #V1.4.2

        # check processing isn't already running
        if os.path.isfile(workdir+spawnlock):
            # showstatus(self,'new','Processing already running.') #V1.4.2
            showMessage(self, 'warn', 'Processing already running.') #V1.4.2
        else:
            clearImage(self)

            todolist = []; 
            for newfile in os.listdir(mydir):
                if (newfile[0:2] != '3D' and
                        (newfile.endswith('.jpg') or newfile.endswith('.JPG')
                        or newfile.endswith('.tiff') or newfile.endswith('.TIFF')
                        or newfile.endswith('.tif') or newfile.endswith('.TIF')
                        or newfile.endswith('.png') or newfile.endswith('.PNG'))):
                    newfile, newext = os.path.splitext(newfile)
                    if newfile[-1:] in ['0','1','2','3','3','5','6','7','8','9'] and [newfile[:-1], newext[1:]] not in todolist:
                        todolist.append([newfile[:-1], newext[1:]])

            if todolist != []:

                todolist = sorted(todolist)

                for newfile in todolist:
                    # filename style is name less last digit - there's no 3D at the beginning
                    processSet(self, newfile[0], newfile[1])

                with open(workdir+spawntext, 'w') as f: # output to text file
                    subprocess.Popen([progdir+spawnprog, workdir, mydir], stdout = f) # run spawnprog
            else:
                showMessage(self, 'warn', 'There are no suitable files.')

            # remove .view files #V1.4.1
            for fn in os.listdir(workdir):
                dummy, fx = os.path.splitext(fn) 
                if fx == '.view':
                    os.remove(workdir+fn)

            makeViewlist(self)
            showProgress(self)

    # process file set #V1.4.2
    def buttonSet(self, menuitem):
        # global statusmessage #V1.4.2
        # showstatus(self, 'new', '') # qt was self.statusBar().clearMessage() #V1.4.2

        # check processing isn't already running
        if os.path.isfile(workdir+spawnlock):
            # showstatus(self,'new','Processing already running.') #V1.4.2
            showMessage(self, 'warn', 'Processing already running.') #V1.4.2
        else:
            clearImage(self)


            if myfile != '{none}' and myext != '{none}':

                todolist = [myfile, myext]

                # filename style is name less last digit - there's no 3D at the beginning
                processSet(self, myfile, myext)

            else:
                #result = Qtmenuitems.QMessageBox.question(self, 'Warning', 'Select a file first', Qtmenuitems.QMessageBox.Close)
                showMessage(self, 'warn', 'Select a file first')

            # start spawn program
            with open(workdir+spawntext, 'w') as f: # output to text file
                subprocess.Popen([progdir+spawnprog, workdir, mydir], stdout = f) # run spawnprog

            # remove .view files #V1.4.1
            for fn in os.listdir(workdir):
                dummy, fx = os.path.splitext(fn) 
                if fx == '.view':
                    os.remove(workdir+fn)

            makeViewlist(self)
            showProgress(self)
    '''
    # process file set
    def buttonSet(self, menuitem):
        # global statusmessage #V1.4.2

        # showstatus(self, 'new', '') # qt was self.statusBar().clearMessage() #V1.4.2
        clearImage(self)

        if myfile != '{none}' and myext != '{none}':

            todolist = [myfile, myext]

            # filename style is name less last digit - there's no 3D at the beginning
            processSet(self, myfile, myext)

            # run spawn file if not already running
            if os.path.isfile(workdir+spawnlock):
                # showstatus(self,'new','Processing already running.') #V1.4.2
                showstatus(self,'new','Processing already running.') #V1.4.2 <<<<<
            else:
                with open(workdir+spawntext, 'w') as f:	# output to text file 
                    subprocess.Popen([progdir+spawnprog, workdir, mydir], stdout = f) # run spawnprog

        else:
            #result = Qtmenuitems.QMessageBox.question(self, 'Warning', 'Select a file first', Qtmenuitems.QMessageBox.Close)
            showMessage(self, 'warn', 'Select a file first')

        # remove .view files #V1.4.1
        for fn in os.listdir(workdir):
            dummy, fx = os.path.splitext(fn) 
            if fx == '.view':
                os.remove(workdir+fn)
        makeViewlist(self)
        showProgress(self)
    '''

    def radiobuttonNew(self, menuitem):
        global view
        if menuitem.get_active():
            view = 'New'
            makeViewlist(self)
            if not setprefs: findImage(self)
            showProgress(self)

    # view folder
    def radiobuttonFolder(self, menuitem):
        global view
        if menuitem.get_active():
            view = 'Folder'
            makeViewlist(self)
            if not setprefs: findImage(self)
            showProgress(self)

    # view file
    def radiobuttonSet(self, menuitem):
        global view
        if menuitem.get_active():
            view = 'Set'
            makeViewlist(self)
            if not setprefs: findImage(self)
            showProgress(self)
        
    def buttonBack(self, menuitem):
        global viewind        
        viewind = viewind - 1
        findImage(self)
        showProgress(self)

    def buttonForward(self, menuitem):
        global viewind, firstview

        if firstview: #~~~~~
            viewind = 0
            firstview = False
        else:
            viewind = viewind + 1
        
        if view == 'New':
            makeViewlist(self)
        findImage(self)
        showProgress(self)

    def buttonDelete(self, menuitem):
        # filename style of finished file, but 3D at the beginning has to be added
        if viewind > -1:
            if os.path.isfile(mydir+'3D'+viewlist[viewind][0]+'.'+viewlist[viewind][1]):
                #result = Qtmenuitems.QMessageBox.question(self, 'Delete file.', 'Delete ' + mydir+'3D'+viewlist[viewind][0]+'.'+viewlist[viewind][1] + '?', Qtmenuitems.QMessageBox.No, Qtmenuitems.QMessageBox.Yes)
                result = showMessage(self, 'ask', 'Delete ' + mydir+'3D'+viewlist[viewind][0]+'.'+viewlist[viewind][1] + '?')
                if result == 'Y': # Yes
                    clearImage(self) #V1.4.2
                    os.remove(mydir+'3D'+viewlist[viewind][0]+'.'+viewlist[viewind][1])
                    del viewlist[viewind]
                    findImage(self)
                    showProgress(self)

# qt ***************************************************************************
'''
app = Qtmenuitems.QApplication(sys.argv)
myWindow = MyWindowClass()
myWindow.show()
sys.exit(app.exec_())
'''
# Gtk***************************************************************************
if __name__ == '__main__':
    main = GUI()
    Gtk.main()

# ******************************************************************************
