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
        
        # adding controls
        self.controls = Controls()
        self.setCentralWidget(self.controls)
        
        # window parameters
        self.statusBar().showMessage('Ready')
        self.setWindowIcon(QtGui.QIcon('../icons/media-playback-start.png'))        
        self.setWindowTitle('mini-player')    
        
        # rendering
        self.setGeometry(300, 300, 250, 150)
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
        playAction.triggered.connect(self.controls.media_player.play)
        pauseAction.triggered.connect(self.controls.media_player.pause)
        nextAction.triggered.connect(self.controls.media_player.ff)
        prevAction.triggered.connect(self.controls.media_player.fr)
        stopAction.triggered.connect(self.controls.media_player.stop)
        exitAction.triggered.connect(QtGui.qApp.quit)
        

        
        
    def update_status(self, t):
        self.statusBar().showMessage(str(t))

class Controls(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        # initializing player
        fn = "/home/shared/musique/Maxime Le Forestier - Ne quelque part.mp3"
        self.media_player = Player(fn)
        self.slider = Phonon.SeekSlider(self.media_player , self)
        #ew = self.media_player.ew
       
        
        sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.label = QtGui.QLabel(self)
        self.label.setPixmap(QtGui.QPixmap('../icons/audio-volume-muted.png'))
        
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.slider)
        #hbox.addWidget(ew)
        hbox.addWidget(sld)
        hbox.addWidget(self.label)
        self.setLayout(hbox)
        
        sld.valueChanged[int].connect(self.changeValue)
    
    def changeValue(self, value):
        if value == 0:
            self.label.setPixmap(QtGui.QPixmap('../icons/audio-volume-muted.png'))
        elif value > 0 and value <= 30:
            self.label.setPixmap(QtGui.QPixmap('../icons/audio-volume-low.png'))
        elif value > 30 and value < 80:
            self.label.setPixmap(QtGui.QPixmap('../icons/audio-volume-medium.png'))
        else:
            self.label.setPixmap(QtGui.QPixmap('../icons/audio-volume-high.png'))
    
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
        
        # set speed
        #e.setParameterValue(s, QtCore.QVariant(2.0))
        
        # print current status
        print [float(i.toString()) for i in ( e.parameterValue(s), s.minimumValue(), s.maximumValue())]
        print e.description().description()
        
        
        # insert effect in rendering path
        #self.path.insertEffect(e)
        #self.ew = Phonon.EffectWidget(e)
        
        
    def ff(self):
        """just seek for 20 secs forward"""
        target_t = self.currentTime() + 20000
        total_t = self.totalTime()
        if target_t < total_t and self.isSeekable():
            print "seekable, going to %s" % target_t
            self.seek(target_t)
        else:
            self.stop()
            
    def fr(self):
        """just seek for 20 secs backward"""
        target_t = self.currentTime() - 20000
        if self.isSeekable():
            print "seekable, going to %s" % max(0, target_t)
            self.seek(max(0, target_t))
        else:
            self.stop()
            
    

if __name__ == '__main__':
    main()
