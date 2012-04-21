import sys

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
from PyQt4.QtGui import QApplication, QMainWindow, QDirModel, QColumnView
from PyQt4.QtGui import QFrame
from PyQt4.QtCore import SIGNAL
from PyQt4.phonon import Phonon

class MainWindow(QMainWindow):

    m_model = QDirModel()

    def __init__(self):
        QMainWindow.__init__(self)
        self.m_fileView = QColumnView(self)
        self.m_media = None

        self.setCentralWidget(self.m_fileView)
        self.m_fileView.setModel(self.m_model)
        self.m_fileView.setFrameStyle(QFrame.NoFrame)

        self.connect(self.m_fileView,
                SIGNAL("updatePreviewWidget(const QModelIndex &)"), self.play_file)

    def play_file(self, index):
        self.delayedInit()
        self.m_media.setCurrentSource(
                Phonon.MediaSource(self.m_model.filePath(index)))
        self.m_media.play_file()

    def delayedInit(self):
        if not self.m_media:
                self.m_media = Phonon.MediaObject(self)
                audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
                Phonon.createPath(self.m_media, audioOutput)

def main():
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Phonon Tutorial 2 (Python)")
    mw = MainWindow2()
    mw.show()
    sys.exit(app.exec_())

class MainWindow2(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        # initializing player
        fn = "/home/shared/musique/Maxime Le Forestier - Ne quelque part.mp3"
        self.media_player = Player(fn)
        
        # adding some stuff to window
        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 250, 150)
        self.setWindowIcon(QtGui.QIcon('../icons/media-playback-start.png'))        
        self.setWindowTitle('mini-player')    
        self.show()
        
        
        # creating toolbar
        playAction = QtGui.QAction(QtGui.QIcon('../icons/media-playback-start.png'), 'Play', self)
        pauseAction = QtGui.QAction(QtGui.QIcon('../icons/media-playback-pause.png'), 'Pause', self)
        prevAction = QtGui.QAction(QtGui.QIcon('../icons/go-previous.png'), 'Prev', self)
        nextAction = QtGui.QAction(QtGui.QIcon('../icons/go-next.png'), 'Next', self)
        stopAction = QtGui.QAction(QtGui.QIcon('../icons/media-playback-stop.png'), 'Stop', self)
        exitAction = QtGui.QAction(QtGui.QIcon('../icons/system-log-out.png'), 'Exit', self)
        
        self.toolbar = self.addToolBar('Tools')
        self.toolbar.addAction(playAction)
        self.toolbar.addAction(pauseAction)
        self.toolbar.addAction(prevAction)
        self.toolbar.addAction(nextAction)
        self.toolbar.addAction(stopAction)
        self.toolbar.addAction(exitAction)
        
        # binding signals to player
        playAction.triggered.connect(self.media_player.play)
        pauseAction.triggered.connect(self.media_player.pause)
        nextAction.triggered.connect(self.media_player.ff)
        prevAction.triggered.connect(self.media_player.fr)
        stopAction.triggered.connect(self.media_player.stop)
        exitAction.triggered.connect(QtGui.qApp.quit)
        
        self.media_player.tick.connect(self.update_status)
        
    def update_status(self, t):
        self.statusBar().showMessage(str(t))

class Player(Phonon.MediaObject):
    def __init__(self, fn):
        Phonon.MediaObject.__init__(self)
        audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.path = Phonon.createPath(self, audioOutput)
        self.fn = fn
        self.setCurrentSource(Phonon.MediaSource(fn))
        self.tickInterval = 10
        
        # looking for effects
        effects = [e 
                   for e in Phonon.BackendCapabilities.availableAudioEffects()
                   if str(e.name())=='speed']
        if not effects:
            print "no speed effect found"
        else:
            print "speed effect found:", effects[0].name()
            self._activate(effects[0])
        
    def _activate(self, effect):
        e = Phonon.Effect(effect)
        s = e.parameters()[0]
        e.setParameterValue(s, QtCore.QVariant(2.0))
        print [float(i.toString()) for i in ( e.parameterValue(s), s.minimumValue(), s.maximumValue())]
        self.path.insertEffect(e)
        
    def ff(self):
        """just seek for 10 secs forward"""
        target_t = self.currentTime() + 1000
        total_t = self.totalTime()
        if target_t < total_t and self.isSeekable():
            print "seekable, going to %s" % target_t
            self.seek(target_t)
        else:
            self.stop()
            
    def fr(self):
        """just seek for 1 secs backward"""
        target_t = self.currentTime() - 1000
        if self.isSeekable():
            print "seekable, going to %s" % max(0, target_t)
            self.seek(max(0, target_t))
        else:
            self.stop()
            
    

if __name__ == '__main__':
    main()
