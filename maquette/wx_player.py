# player.py

import wx
import os

# constants for IDs4
ID_AUTOSAVE = wx.NewId()
ID_TOGGLE_TOOL_BAR = wx.NewId()
ID_TOGGLE_STATUS_BAR = wx.NewId()
ID_SPEED = wx.NewId()

ID_TIMELINE = wx.NewId()
ID_ADD_CHAPTER = wx.NewId()
ID_RM_CHAPTER  = wx.NewId()

ID_SET_START = wx.NewId()
ID_SET_END = wx.NewId()

def r(filename):
    """Returns resource folder"""
    script_location = os.path.dirname(__file__)
    one_level_upper = os.path.normpath(os.path.join(script_location, '..'))
    p = ''
    if 'icons' in os.listdir(script_location):
        p = script_location
    elif 'icons' in os.listdir(one_level_upper):
        p = one_level_upper
    else:
        pass # no path found
    
    if not p:
        raise OSError("Could not find resource folder")
    else:
        return os.path.join(p, filename)
    

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        
        self.SetSize((400, 350))
        self.SetMinSize((400, 350))
        
        self.autosave = False
        self.show_statusbar = True
        self.chapters = {}  # dict of (time, name) chapters
        self.SetFocus()
        
        self.start = ""
        self.end = ""
        
        #------------------------------------- building menu and status bar
        self.menubar = MyMenuBar()
        self.SetMenuBar(self.menubar)
        self.statusbar = MyStatusBar(self, wx.ID_ANY)
        self.SetStatusBar(self.statusbar)

        #--------------------------------------------------- adding content
        # building components
        self.toolbar = MyToolBar(self, wx.ID_ANY, style=wx.TB_HORIZONTAL)
        self.mediabar = MediaBar(self, wx.ID_ANY, style=wx.TB_HORIZONTAL)
        self.controlzone = ControlZone(self, wx.ID_ANY)
        self.chapterbar = ChapterBar(self, wx.ID_ANY, style=wx.TB_VERTICAL)
        self.listing = ChapterList(self, wx.ID_ANY, style=wx.LC_REPORT|wx.LC_VRULES)
        
        # positioning them around
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar)
        sizer.Add(self.mediabar)
        sizer.Add(self.controlzone, flag=wx.EXPAND | wx.BOTTOM | wx.TOP)
        
        vb = wx.BoxSizer(wx.HORIZONTAL)
        vb.Add(self.chapterbar, 0, flag=wx.EXPAND)
        vb.Add(self.listing, 1, flag=wx.EXPAND)
        sizer.Add(vb, 1, flag=wx.EXPAND)
        #sizer.Add(self.chapterbar, 0, flag=wx.EXPAND|wx.TOP)
        #sizer.Add(self.listing, 1, flag=wx.EXPAND)
        self.SetSizer(sizer)
        
        #--------------------------------------------- initializing content
        self.toolbar.ToggleTool(ID_AUTOSAVE, self.autosave)
        self.toolbar.ToggleTool(ID_TOGGLE_STATUS_BAR, self.show_statusbar)
        self.toolbar.EnableTool(wx.ID_UNDO, False)
        
        #------------------------------------------------ bindings creation
        # Exit bindings
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_TOOL, self.OnExit, id=wx.ID_EXIT)
        
        # autosave binding
        self.Bind(wx.EVT_MENU, self.ToggleAutoSave, id=ID_AUTOSAVE)
        self.Bind(wx.EVT_TOOL, self.ToggleAutoSave, id=ID_AUTOSAVE)
        
        # shorcut bindings
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
        # display settings
        self.Bind(wx.EVT_MENU, self.ToggleToolBar, id=ID_TOGGLE_TOOL_BAR)
        self.Bind(wx.EVT_MENU, self.ToggleStatusBar, id=ID_TOGGLE_STATUS_BAR)
        
        # add/remove chapters
        self.Bind(wx.EVT_TOOL, self.AddChapter, id=ID_ADD_CHAPTER)
        self.Bind(wx.EVT_TOOL, self.RmChapter, id=ID_RM_CHAPTER)
        
        # start/end selection
        self.Bind(wx.EVT_TOOL, self.SetStart, id=ID_SET_START)
        self.Bind(wx.EVT_TOOL, self.SetEnd, id=ID_SET_END)
        
        # link chapter selection to timeline position
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ChapterSelect, id=self.listing.GetId())
        
        
    def OnSpin(self, ev):
        print "Spin"
    
    def OnExit(self, ev):
        self.Close()
        
    def OnKeyDown(self, ev):
        keycode = ev.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            ret  = wx.MessageBox('Are you sure to quit?', 'Question', wx.YES_NO | wx.CENTRE | wx.NO_DEFAULT, self)
            if ret == wx.YES:
                self.Close()
        ev.Skip()
        
    def ToggleAutoSave(self, ev):
        # toggling autosave status
        self.autosave = not self.autosave
        
        # Now updating linked GUI items
        m = self.menubar.filemenu.autosave
        if m.IsChecked() != self.autosave:
            m.Toggle()
        
        self.toolbar.ToggleTool(ID_AUTOSAVE, self.autosave)
        
    def ToggleToolBar(self, ev):
        if self.menubar.showmenu.show_toolbar.IsChecked():
            self.toolbar.Show()
        else:
            self.toolbar.Hide()
        
    def ToggleStatusBar(self, ev):
        self.show_statusbar = not self.show_statusbar
        
        if self.show_statusbar:
            self.statusbar.Show()
        else:
            self.statusbar.Hide()
        
        m = self.menubar.showmenu.show_statusbar
        if m.IsChecked() != self.show_statusbar:
            m.Toggle()
        
        self.toolbar.ToggleTool(ID_TOGGLE_STATUS_BAR, self.show_statusbar)
    
    def AddChapter(self, ev):
        # retrieve timeline position
        t = self.controlzone.timeline.GetValue()
        
        # add in storage - dict ensures uniqueness
        self.chapters[t] = "some chapter name"
        print self.chapters
        # display in listing
        self.UpdateChapters()
        
    def RmChapter(self, ev):
        # retrieve timeline position
        t = self.controlzone.timeline.GetValue()
        
        # remove from storage - note that precision is possible through
        # direct selection of the chapter in the listing.
        if t in self.chapters:
            del self.chapters[t]
        
            # display in listing
            self.UpdateChapters()
        else:
            return
    
    def ChapterSelect(self, ev):
        # retrieve chapter timeline
        idx = self.listing.GetFocusedItem()
        if idx == -1:
            # failure case, with no selection
            return
        t = int(self.listing.GetItem(idx, 0).GetText())
        # move slider to time
        self.controlzone.timeline.SetValue(t)
    
    def UpdateChapters(self):
        # refreshing chapters listing, in order
        self.listing.DeleteAllItems()
        for i, t in enumerate(sorted(self.chapters)): 
            self.listing.InsertStringItem(i, str(t))
            self.listing.SetStringItem(i, 1, self.chapters[t])
        
    def SetStart(self, ev):
        self.start = self.controlzone.timeline.GetValue()
        self.statusbar.SetStatusText("Start: %s" % self.start, 1)
        
    def SetEnd(self, ev):
        self.end = self.controlzone.timeline.GetValue()
        self.statusbar.SetStatusText("End: %s" % self.end, 2)
    
class MyMenuBar(wx.MenuBar):
    """Custom menu bar"""
    def __init__(self, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)
        
        self.filemenu = FileMenu()
        self.editmenu = EditMenu()
        self.playmenu = PlayMenu()
        self.showmenu = ShowMenu()
        self.helpmenu = HelpMenu()
        
        self.Append(self.filemenu, '&File')
        self.Append(self.editmenu, '&Edit')
        self.Append(self.playmenu, '&Play')
        self.Append(self.showmenu, '&Show')
        self.Append(self.helpmenu, '&Help')

class FileMenu(wx.Menu):
    """Custom File Menu"""
    def __init__(self, *args, **kwargs):
        wx.Menu.__init__(self, *args, **kwargs)
        
        self.new  = wx.MenuItem(self, wx.ID_NEW,  "&New",  "Create new project")
        self.open = wx.MenuItem(self, wx.ID_OPEN, "&Open", "Open Project")
        self.save = wx.MenuItem(self, wx.ID_SAVE, "&Save", "Save Project")
        self.autosave = wx.MenuItem(self, ID_AUTOSAVE, "&AutoSave", "Save Project", kind=wx.ITEM_CHECK)
        self.quit = wx.MenuItem(self, wx.ID_EXIT, "&Quit", "Quit application")
        
        self.AppendItem(self.new)
        self.AppendItem(self.open)
        self.AppendItem(self.save)
        self.AppendItem(self.autosave)
        self.AppendSeparator()
        self.AppendItem(self.quit)
        
class EditMenu(wx.Menu):
    """Custom Edit menu"""
    def __init__(self, *args, **kwargs):
        wx.Menu.__init__(self, *args, **kwargs)
        self.Append(wx.ID_UNDO, "&Undo", "Cancel last action")
        self.Append(wx.ID_REDO, "&Redo", "Redo cancelled action")
        self.AppendSeparator()
        self.Append(wx.ID_PROPERTIES, "&Properties", "Edit project properties")

class PlayMenu(wx.Menu):
    """Custom play menu"""
    def __init__(self, *args, **kwargs):
        wx.Menu.__init__(self, *args, **kwargs)
        self.Append(wx.ID_ANY, "&Play" )
        self.Append(wx.ID_ANY, "P&ause")
        self.Append(wx.ID_ANY, "&Stop")
        self.AppendSeparator()
        self.Append(wx.ID_ANY, "Play &All")
        self.AppendSeparator()
        self.Append(wx.ID_ANY, "&Repeat", kind=wx.ITEM_CHECK)
        
class ShowMenu(wx.Menu):
    """Custom display settings menu"""
    def __init__(self, *args, **kwargs):
        wx.Menu.__init__(self, *args, **kwargs)
        self.show_toolbar = wx.MenuItem(self, ID_TOGGLE_TOOL_BAR, "Show ToolBar", kind=wx.ITEM_CHECK)
        self.show_statusbar = wx.MenuItem(self, ID_TOGGLE_STATUS_BAR, "Show StatusBar", kind=wx.ITEM_CHECK)
        
        self.AppendItem(self.show_toolbar)
        self.AppendItem(self.show_statusbar)

class HelpMenu(wx.Menu):
    """Custom Help Menu"""
    def __init__(self, *args, **kwargs):
        wx.Menu.__init__(self, *args, **kwargs)
        self.Append(wx.ID_HELP,  "&Contents", "Help on RP usage")
        self.AppendSeparator()
        self.Append(wx.ID_ABOUT, "&About", "About Rehersal Player")

class MyStatusBar(wx.StatusBar):
    def __init__(self, *args, **kwargs):
        wx.StatusBar.__init__(self, *args, **kwargs)
        self.SetFieldsCount(3)
        self.SetStatusWidths([-1, 100, 100])
     
class MyToolBar(wx.ToolBar):
    def __init__(self, *args, **kwargs):
        wx.ToolBar.__init__(self, *args, **kwargs)
        
        self.AddSimpleTool(wx.ID_SAVE, wx.Bitmap(r('icons/document-save.png')), "Save", "Save to filesystem")
        self.autosave = self.AddSimpleTool(ID_AUTOSAVE, wx.Bitmap(r('icons/document-save.png')), "AutoSave", "Auto save", True)
        self.AddSeparator()
        self.AddSimpleTool(wx.ID_UNDO, wx.Bitmap(r('icons/edit-undo.png')), "Undo", "Cancel action")
        self.AddSimpleTool(wx.ID_REDO, wx.Bitmap(r('icons/edit-redo.png')), "Undo", "Redo action")
        self.AddSeparator()
        self.AddSimpleTool(wx.ID_EXIT, wx.Bitmap(r('icons/system-log-out.png')), "Exit", "Exit RP")
        self.Realize()

class MediaBar(wx.ToolBar):
    def __init__(self, *args, **kwargs):
        wx.ToolBar.__init__(self, *args, **kwargs)
        
        self.AddSimpleTool(wx.ID_ANY, wx.Bitmap(r('icons/media-playback-start.png')), "Play")
        self.AddSimpleTool(wx.ID_ANY, wx.Bitmap(r('icons/media-playback-pause.png')), "Pause")
        self.AddSimpleTool(wx.ID_ANY, wx.Bitmap(r('icons/media-playback-stop.png')), "Stop")
        self.AddSeparator()
        self.AddSimpleTool(ID_SET_START, wx.Bitmap(r('icons/go-first.png')), "Start")
        self.AddSimpleTool(ID_SET_END, wx.Bitmap(r('icons/go-last.png')), "End")
        self.AddSeparator()
        self.AddSimpleTool(wx.ID_ANY, wx.Bitmap(r('icons/media-playback-repeat.png')), "Repeat", "Repeat selection", True)
        
        
class QuitBar(wx.ToolBar):
    def __init__(self, *args, **kwargs):
        wx.ToolBar.__init__(self, *args, **kwargs)
        
        self.AddSimpleTool(wx.ID_EXIT, wx.Bitmap(r('icons/system-log-out.png')), "Exit", "Exit RP")
        self.Realize()
        
class ChapterBar(wx.ToolBar):
    def __init__(self, *args, **kwargs):
        wx.ToolBar.__init__(self, *args, **kwargs)
        
        self.AddSimpleTool(ID_ADD_CHAPTER, wx.Bitmap(r('icons/list-add.png')), "Add Chapter")
        self.AddSimpleTool(ID_RM_CHAPTER, wx.Bitmap(r('icons/list-remove.png')), "Remove Chapter")
        self.AddSimpleTool(wx.ID_ANY, wx.Bitmap(r('icons/go-previous.png')), "Previous chapter")
        self.AddSimpleTool(wx.ID_ANY, wx.Bitmap(r('icons/go-next.png')), "Next chapter")
        self.Realize()
        
class ViewZone(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, style=wx.LC_REPORT, **kwargs)
        self.SetBackgroundColour(wx.BLACK)
        
class ChapterList(wx.ListCtrl):
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        
        # define columns headers
        self.InsertColumn(0, "Time")
        self.InsertColumn(1, "Chapter Name")
        
        self.SetColumnWidth(0, 50)
        self.SetColumnWidth(1, 250)


class ControlZone(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        # building components
        self.timeline = wx.Slider(self, ID_TIMELINE, 0, 0, 121, style=wx.SL_AUTOTICKS|wx.SL_LABELS|wx.SL_SELRANGE)
        self.timeline.SetTickFreq(10)
        
        # pause =   wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(r('icons/media-playback-pause.png')))
        # play  =   wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(r('icons/media-playback-start.png')))
        # stop  =   wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(r('icons/media-playback-stop.png')))
        # prev  =   wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(r('icons/go-previous.png')))
        # nextB  =  wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap(r('icons/go-next.png')))
        # slider2 = wx.Slider(self, wx.ID_ANY, 0, 0, 100, size=(120, -1))
        # spin    = wx.SpinCtrl(self, ID_SPEED, '0', size=(50, -1), min=0, max=10)
        
        # positioning them around
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.timeline, 1)
        
        # hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        # hbox2.Add(play)
        # hbox2.Add(pause)
        # hbox2.Add(stop, flag=wx.RIGHT, border=5)
        # hbox2.Add(prev, flag=wx.LEFT, border=5)
        # hbox2.Add(nextB)
        # hbox2.Add((150, -1), 1, flag=wx.EXPAND | wx.ALIGN_RIGHT)
        # hbox2.Add(slider2, flag=wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, border=5)
        # hbox2.Add(spin)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox1, 1, wx.EXPAND | wx.BOTTOM, 10)
        # vbox.Add(hbox2, 1, wx.EXPAND)
        self.SetSizer(vbox)

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, wx.ID_ANY, 'Rehearsal Player')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()