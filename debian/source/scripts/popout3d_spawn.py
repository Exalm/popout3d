#! /usr/bin/python3
# popout3d_spawn.py
# Version as popout3d.py

'''
--------------------------------------------------------------------------------
Popout3D Stereo Image Creation

Copyright 2015-2017 Chris Rogers <popout3d.software@gmail.com>

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
    in /usr/share/common-licenses/GPL-3.  
    If not, see <http://www.gnu.org/licenses/>.

--------------------------------------------------------------------------------
'''

import os, sys
from PIL import Image

workdir = sys.argv[1] ; mydir = sys.argv[2]
spawnlock = 'spawn.lock'

if os.path.isfile(workdir+spawnlock):
    exit # spawn lock exists so something already running
else:
    with open(workdir+spawnlock, 'w') as fn: # create spawn lock
        fn.write('')    
    # remove all .view files, should have been done in main program already
    for fn in os.listdir(workdir):
        dummy, fx = os.path.splitext(fn) 
        if fx == '.view':
            os.remove(workdir+fn)

#---------------------------------------
# each loop does one pair of images
for wholefilename in os.listdir(workdir): # 'example0+1AL.JPG.lock'
    # 'example0+1AL.JPG' '.lock'
    filename, flag = os.path.splitext(wholefilename)

    if flag == '.queue':

        #---------------------------------------
        # parse filename
        name, ext = os.path.splitext(filename)     # 'example0+1AL' '.JPG'
        origname  = name[0:-5]                     # 'example'
        left      = name[-5] ; right = name[-3]    # '0' '1'
        formlet   = name[-2] ; stylelet = name[-1] # 'A' 'L'

        if stylelet == 'L':
            stylecode = 'A'
        else:
            stylecode = 'P'
        
        #---------------------------------------
        # compose variables then call align_image_stack
        fileout   = origname+left+'+'+right+formlet+stylelet+ext
        fileleft  = origname+left+ext
        fileright = origname+right+ext
        command   = 'align_image_stack -a "'+workdir+fileout+'" -m -i -'+stylecode+' -C "'+mydir+fileright+'" "'+mydir+fileleft+'"'
        
        # create .process file and delete .queue file
        with open(workdir+fileout+'.process', 'w') as fn:
            fn.write('')

        if os.path.isfile(workdir+fileout+'.queue'):
            os.remove(workdir+fileout+'.queue')

        # run alignment program
        result = os.system(command)
        if result != 0:
            print ('Error running align_image_stack '+result)

        #---------------------------------------
        # merge the files, put result in mydir

        # load left and right images
        image_left = Image.open(workdir+fileout+'0001.tif')
        image_right = Image.open(workdir+fileout+'0000.tif')
        image_left.load() ; image_right.load()

        if formlet == 'A':
            # separate the colours
            image_red, junk1, junk2, transparency_mask = image_left.split()
            junk3, image_green, image_blue, junk4 = image_right.split()
            # merge the appropriate colours into 3D image
            image_new = Image.merge('RGBA', (image_red, image_green, image_blue, transparency_mask))

        elif formlet == 'S':
            image_width = int(image_left.size[0]) ; image_height = int(image_left.size[1])
            # create double-width blank new image
            image_new = Image.new('RGB', (image_width * 2, image_height), color=0)
            # paste left image into new image on the left
            #V4.2.1 image_ was missing from image_left
            image_new.paste(image_left, (0, 0, image_width, image_height))
            # paste right image into new image on the right
            image_new.paste(image_right, (image_width, 0, 2 * image_width, image_height))

        else : # Crossover
            image_width = int(image_left.size[0]) ; image_height = int(image_left.size[1])
            # create double-width blank new image
            image_new = Image.new('RGB', (image_width * 2, image_height), color=0)
            # paste right image into new image on the left
            image_new.paste(image_right, (0, 0, image_width, image_height))
            # paste left image into new image on the right
            image_new.paste(image_left, (image_width, 0, 2 * image_width, image_height))

        # save new image, write .view file, remove process file, aligned images
        image_new.save(mydir+'3D'+fileout)

        with open(workdir+fileout+'.view', 'w') as fn:
            fn.write('')

        if os.path.isfile(workdir+fileout+'.process'):
            os.remove(workdir+fileout+'.process')

        if os.path.isfile(workdir+fileout+'0001.tif'):
            os.remove(workdir+fileout+'0001.tif')
        if os.path.isfile(workdir+fileout+'0000.tif'):
            os.remove(workdir+fileout+'0000.tif') 

#---------------------------------------
# finished so delete spawn lock
if os.path.isfile(workdir+spawnlock):
    os.remove(workdir+spawnlock)

exit(0)
