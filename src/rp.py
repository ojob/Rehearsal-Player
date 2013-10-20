# -*- coding: utf-8 -*-
# 
#
"""
Rehearsal-_player

This _player is aimed at rehearsing songs, 

"""
__author__ = 'Joël Bourgault'
__email__ = 'joel.bourgault@gmail.com'

# major version, minor version, generation
__version__ = (0, 0, 1)


#==========================================================================
# Import
#==========================================================================

#-------------------------------------------------- import built-in modules
import os
import sys

#----------------------------------------------------- import PyQt4 modules
import PyQt4.QtGui as QtGui
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QMainWindow, QApplication
from PyQt4.phonon import Phonon

#-------------------------------------- import other modules of the project
import rp_ui

#==========================================================================
# Defining constants
#==========================================================================
WINDOW_TITLE = "Rehearsal - player"

ICON_WINDOW = '../icons/media-playback-start.png'

ICON_OPEN  = '../icons/document-open.png'
ICON_PLAY  = '../icons/media-playback-start.png'
ICON_PAUSE = '../icons/media-playback-pause.png'
ICON_STOP  = '../icons/media-playback-stop.png'

ICON_PREV  = '../icons/go-previous.png'
ICON_NEXT  = '../icons/go-next.png'

ICON_EXIT  = '../icons/system-log-out.png'

#==========================================================================
# Classes
#==========================================================================
class Bookmarks(dict):
    """class for storing bookmarks"""
    def __init__(self, *args, **kwargs):
        super(Bookmarks, self).__init__()
        self.load_bookmarks("")
        
    def load_bookmarks(self, fn):
        # TODO: extract the following from the given file
        for t, (n, d) in {     
                     0: ('start', ''),
                 22000: ('fin intro', ''),
                 46000: ('début seconde partie', 'ça commence à aller plus vite'),
                 60000: ('swing_out', ''), 
                 77000: ('tour garçons', '') ,
                100000: ('mise en diagonale', '') ,
                127000: ('filles pieds en l\'air', ''),
                  }.items():
            self.add(t, n, d)
        
    def add(self, t, name="", descr=""):
        """t in ms"""
        self[t] = (name, descr)
        
    def remove(self, t):
        del self[t]
        
    def prev(self, t):
        """return first bookmark before given timely_update"""
        try:
            return max(k for k in self.keys() if k < t - 1000)
            # -1000, so that if we're close to a bookmark, we jump to the 
            # previous one
        except ValueError:
            # exception raised if list is empty, returning minimum value
            return 0
        
    def next(self, t):
        ""
        try:
            return min(k for k in self.keys() if k > t)
        except ValueError:
            # exception raised if no bookmark left, returning nothing
            return None
        
#==========================================================================
# Defining widgets
#==========================================================================

class RehearsalPlayer(QMainWindow):
    def __init__(self):
        super(RehearsalPlayer, self).__init__()
        
        # creating internal variables
        self._open_dir = os.path.expanduser("~")
        
        # creating user interface
        self._ui = rp_ui.Ui_MainWindow()
        self._ui.setupUi(self)
        
        # creating _player resource
        self._player = Player()
        
        # connecting _ui and _player
        self.connect_ui()
        
        # displaying the result
        self.show()
        
    def connect_ui(self):
        self._ui.button_open_file.clicked.connect(self.open_file)
        self._ui.button_play.clicked.connect(self._player.play)
        self._ui.button_pause.clicked.connect(self._player.pause)
        self._ui.button_stop.clicked.connect(self._player.stop)
        self._ui.button_bookmark_prev.clicked.connect(self.prev_bookmark)
        self._ui.button_bookmark_next.clicked.connect(self.next_bookmark)
        
        self._ui.seek_slider.setMediaObject(self._player)
        self._ui.volume_slider.setAudioOutput(self._player.audioOutput)

        self._ui.speed_activated.stateChanged.connect(self.set_speed)
        self._ui.speed_spinbox.valueChanged.connect(self.set_speed)
        
        self._player.tick.connect(self.timely_update)
        
    def open_file(self):
        """Selection of a file to be played"""
        fn = QtGui.QFileDialog.getOpenFileName(self, 
                                               'Open file', 
                                               self._open_dir)
        if fn:
            self._open_dir = os.path.dirname(str(fn))
            self._player.open_file(fn)
            self.update_status("Loaded file: {0}"
                               .format(os.path.split(str(fn))[1]))
            self.bookmarks = Bookmarks()  
            # TODO: get bookmarks from file metadata
        else:
            # selection has been aborted by user --> no effect
            pass
        
    def update_status(self, text):
        self.statusBar().showMessage(str(text))
    
    def timely_update(self):
        
        # updating time display
        time_total = self._player.total_time
        time_elapsed = self._player.timely_update() / 1000
        time_left = time_total - time_elapsed if time_total>=0 else -1
        self._ui.time_total.setText(t_to_s(time_total))
        self._ui.time_elapsed.setText(t_to_s(time_elapsed))
        self._ui.time_left.setText(t_to_s(time_left))
         
        # updating volume display
        self._ui.volume_value.setText("{0:.0%}".format(self._player.audioOutput.volume()))
         
    def prev_bookmark(self):
        bookmark = self.bookmarks.prev(self._player.timely_update())
        self._player.seek_t(bookmark)    
                
    def next_bookmark(self):
        """just seek for 20 secs forward"""
        bookmark = self.bookmarks.next(self._player.timely_update())
        if bookmark is not None:
            self._player.seek_t(bookmark)
        else:
            # no next bookmark
            self.update_status("No next bookmark")    

    def set_speed(self, event):
        speed_effect_activate = self._ui.speed_activated.checkState()
        if speed_effect_activate==2:
            # activate effect
            speed_effect_value = float(self._ui.speed_spinbox.value())
            self._player.set_speed(speed_effect_value)
        else:
            # deactivate effect
            self._player.set_speed(1)

    def closeEvent(self, event):
        # TODO: add a condition for saving with changes not already written to file
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Exit?", 
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, 
            QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            QtGui.qApp.quit()
        else:
            if not isinstance(event, bool):
                event.ignore()       

       
#==========================================================================
# Defining back-end media _player
#==========================================================================

class Player(Phonon.MediaObject):
    def __init__(self):
        Phonon.MediaObject.__init__(self)
        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.path = Phonon.createPath(self, self.audioOutput)
        
        # checking that speed effect is available
        effects = [e 
                   for e in Phonon.BackendCapabilities.availableAudioEffects()
                   if str(e.name())=='speed']
        print "speed effect found:", effects[0].name()
        self.speed_effect = Phonon.Effect(effects[0])
        self.speed_effect_param = self.speed_effect.parameters()[0]
    
    def open_file(self, fn):
        self.fn = fn
        self.setCurrentSource(Phonon.MediaSource(fn))
        self.total_time = self.totalTime()
        self.tickInterval = 1000
        
    def set_speed(self, s):
        if s!=1:
            # activating speed effect
            self.path.insertEffect(self.speed_effect)
            self.speed_effect.setParameterValue(self.speed_effect_param,
                                                QVariant(s))
        
        else:
            # deactivating speed effect
            self.path.removeEffect(self.speed_effect)
            self.speed_effect.setParameterValue(self.speed_effect_param,
                                                QVariant(0))
        
    def timely_update(self):
        return self.currentTime()
        
    def seek_t(self, target_t):
        if self.isSeekable():
            if target_t < self.total_time or self.total_time < 0:
                print "seekable, going to %s" % target_t
                self.seek(target_t)
            else:
                print ("target timely_update ({0}) is more than total timely_update ({1})"
                       .format(target_t, self.total_time))
        else:
            print "not seekable, ignoring seek command"
        
   
#==========================================================================
# Utility functions
#==========================================================================
def t_to_s(t):
    if t >= 0:
        m = t / 60
        s = t - m * 60
    else:
        m = s = '--'
    return '{0}:{1:0>2}'.format(m, s)
            
        
#==========================================================================
# Starting the application
#==========================================================================

def main():
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Python rehearsal _player")
    mw = RehearsalPlayer()
    sys.exit(app.exec_())
    
#==========================================================================
# Auto-start
#==========================================================================

if __name__ == '__main__':
    
    main()
    
