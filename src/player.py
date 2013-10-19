# -*- coding: utf-8 -*-
# 
#
"""
Rehearsal-player

This player is aimed at rehearsing songs, 

"""
__author__ = 'Joël Bourgault'
__email__ = 'joel.bourgault@gmail.com'

# major version, minor version, generation
__version__ = (0, 0, 1)


#==========================================================================
# Import
#==========================================================================

import bisect
import os
import sys

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
from PyQt4.QtGui import QMainWindow, QApplication
from PyQt4.phonon import Phonon

#==========================================================================
# Defining constants
#==========================================================================
WINDOW_TITLE = "Rehearsal-player"

ICON_WINDOW = '../icons/media-playback-start.png'

ICON_OPEN  = '../icons/document-open.png'
ICON_PLAY  = '../icons/media-playback-start.png'
ICON_PAUSE = '../icons/media-playback-pause.png'
ICON_STOP  = '../icons/media-playback-stop.png'

ICON_PREV  = '../icons/go-previous.png'
ICON_NEXT  = '../icons/go-next.png'

ICON_EXIT  = '../icons/system-log-out.png'

ICON_VOLUME_MUTED = '../icons/audio-volume-muted.png'
ICON_VOLUME_MUTED = '../icons/audio-volume-muted.png'
ICON_VOLUME_LOW = '../icons/audio-volume-low.png'
ICON_VOLUME_MED = '../icons/audio-volume-medium.png'
ICON_VOLUME_HIGH = '../icons/audio-volume-high.png'

BOOKMARKS = [0, 13000, 46000, 100000, 210000, 230000]  # in ms

#==========================================================================
# Defining widgets
#==========================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        self._open_dir = os.path.expanduser("~")
        
        QMainWindow.__init__(self)
        
        # creating player resource
        self.player = Player()
        
        # adding controls
        self.sliders = Sliders(self.player)
        self.setCentralWidget(self.sliders)
        
        # window parameters
        self.statusBar().showMessage('Ready')
        self.setWindowIcon(QtGui.QIcon(ICON_WINDOW))
        self.setWindowTitle(WINDOW_TITLE)    
        
        # rendering
        self.setGeometry(400, 300, 400, 150)
        self.show()
        
        # creating buttons toolbar
        openAction  = QtGui.QAction(QtGui.QIcon(ICON_OPEN), 'Open File', self)
        playAction  = QtGui.QAction(QtGui.QIcon(ICON_PLAY), 'Play', self)
        pauseAction = QtGui.QAction(QtGui.QIcon(ICON_PAUSE), 'Pause', self)
        stopAction  = QtGui.QAction(QtGui.QIcon(ICON_STOP), 'Stop', self)
        prevAction  = QtGui.QAction(QtGui.QIcon(ICON_PREV), 'Prev', self)
        nextAction  = QtGui.QAction(QtGui.QIcon(ICON_NEXT), 'Next', self)
        exitAction  = QtGui.QAction(QtGui.QIcon(ICON_EXIT), 'Exit', self)
        
        showBookmarks = QtGui.QPushButton('Bookmarks', self)
        showBookmarks.setCheckable(True)
        
        
        self.toolbar = self.addToolBar('Tools')
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(playAction)
        self.toolbar.addAction(pauseAction)
        self.toolbar.addAction(stopAction)
        self.toolbar.addAction(prevAction)
        self.toolbar.addAction(nextAction)

        self.toolbar.addAction(exitAction)
        
        # binding signals to player
        openAction.triggered.connect(self.open_file)
        playAction.triggered.connect(self.player.play)
        pauseAction.triggered.connect(self.player.pause)
        stopAction.triggered.connect(self.player.stop)
        prevAction.triggered.connect(self.prev_phase)
        nextAction.triggered.connect(self.next_phase)
        exitAction.triggered.connect(QtGui.qApp.quit)
        
        showBookmarks.clicked[bool].connect(self.setColor)
        
    def open_file(self):
        """Selection of a file to be played"""
        fn = QtGui.QFileDialog.getOpenFileName(self, 
                                               'Open file', 
                                               self._open_dir)
        if fn:
            self._open_dir = os.path.dirname(str(fn))
            self.player.open_file(fn)
            self.update_status("Loaded file: {0}"
                               .format(os.path.split(str(fn))[1]))
        else:
            # selection has been aborted by user --> no effect
            pass
        
    def update_status(self, t):
        self.statusBar().showMessage(str(t))

         
    def prev_phase(self):
        target_t = BOOKMARKS[bisect.bisect_left(BOOKMARKS, 
                                                self.player.time())-1]
        # we're stuck at current bookmark, when we want the previous
        if target_t > 0 and abs(target_t - self.player.time()) < 1000:
            target_t = BOOKMARKS[bisect.bisect_left(BOOKMARKS, 
                                                    target_t)-1]
        self.player.seek_t(target_t)    
                
    def next_phase(self):
        """just seek for 20 secs forward"""
        target_t = BOOKMARKS[bisect.bisect_left(BOOKMARKS, 
                                                self.player.time())]
        self.player.seek_t(target_t)    

class Sliders(QtGui.QWidget):

    def __init__(self, player):
        QtGui.QWidget.__init__(self)
        
        # adding seek slider
        self.seek_slider = Phonon.SeekSlider(player , self)
        self.seek_slider.setTracking(False)
       
        # adding volume slider widget
        self.volume_slider = Phonon.VolumeSlider(self)
        self.volume_slider.setOrientation(2)   
        self.volume_slider.setAudioOutput(player.audioOutput)
        
        # puting the sliders in layout
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.seek_slider)
        hbox.addWidget(self.volume_slider)
        self.setLayout(hbox)
        
        # binding events
        #self.seek_slider.sliderChanged.connect(self.vol_indicator)
        
    def vol_indicator(self, v):
        print "volume:", v
       
       
#==========================================================================
# Defining back-end media player
#==========================================================================

class Player(Phonon.MediaObject):
    def __init__(self):
        Phonon.MediaObject.__init__(self)
        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.path = Phonon.createPath(self, self.audioOutput)
        self.tickInterval = 10
        
    def open_file(self, fn):
        self.fn = fn
        self.setCurrentSource(Phonon.MediaSource(fn))
        self.total_time = self.totalTime()
        if self.total_time < 0:
            # when total time cannot be determined
            self.total_time = 1000000000
        
    def set_speed(self, s):
        # checking that speed effect is available
        effects = [e 
                   for e in Phonon.BackendCapabilities.availableAudioEffects()
                   if str(e.name())=='speed']
        if not effects:
            print "no speed effect found"
        else:
            print "speed effect found:", effects[0].name()
            effect = effects[0]
        
        
        # setting speed
        e = Phonon.Effect(effect)
        s = e.parameters()[0]
        
        # set speed
        # FIXME: no backend seems to be able to use this function
        e.setParameterValue(s, QtCore.QVariant(0.5))
        # insert effect in rendering path
        self.path.insertEffect(e)
        self.ew = Phonon.EffectWidget(e)
        
        # print current status
        print [float(i.toString()) for i in ( e.parameterValue(s), 
                                              s.minimumValue(), 
                                              s.maximumValue())]
        print e.description().description()
        
    def time(self):
        return self.currentTime()
        
    def seek_t(self, target_t):
        if self.isSeekable():
            if target_t < self.total_time:
                print "seekable, going to %s" % target_t
                self.seek(target_t)
            else:
                print ("target time ({0}) is more than total time ({1})"
                       .format(target_t, self.total_time))
        else:
            print "not seekable, ignoring seek command"
        
   

            
#==========================================================================
# Starting the application
#==========================================================================

def main():
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Python rehearsal player")
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
    
#==========================================================================
# Auto-start
#==========================================================================

if __name__ == '__main__':
    
    main()
    
