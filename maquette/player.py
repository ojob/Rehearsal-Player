# player.py

import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(350, 300))
        
        self.SetMinSize((350, 300))
        
        #------------------------------------- building menu and status bar
        menubar = MyMenuBar()
        self.SetMenuBar(menubar)
        statusbar = MyStatusBar(self, wx.ID_ANY)
        self.SetStatusBar(statusbar)

        #--------------------------------------------------- adding content
        # building components
        toolbar = MyToolBar(self, wx.ID_ANY, style=wx.TB_HORIZONTAL)
        viewzone = ViewZone(self, wx.ID_ANY)
        controlzone = ControlZone(self, wx.ID_ANY)

        # positioning them around
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(toolbar, 0, flag=wx.EXPAND|wx.TOP)
        sizer.Add(viewzone, 1, flag=wx.EXPAND)
        sizer.Add(controlzone, flag=wx.EXPAND | wx.BOTTOM | wx.TOP)
        self.SetSizer(sizer)
        
        #------------------------------------------------ bindings creation
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_TOOL, self.OnExit, id=wx.ID_EXIT)
        
    def OnExit(self, ev):
        self.Close()
        
class MyMenuBar(wx.MenuBar):
    """Custom menu bar"""
    def __init__(self, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)
        
        self.Append(FileMenu(), '&File')
        self.Append(EditMenu(), '&Edit')
        self.Append(HelpMenu(), '&Help')

class FileMenu(wx.Menu):
    """Custom File Menu"""
    def __init__(self, *args, **kwargs):
        wx.Menu.__init__(self, *args, **kwargs)
        
        open = wx.MenuItem(self, wx.ID_OPEN, "&Open", "Open project")
        open.SetBitmap(wx.Bitmap('icons/new.png'))
        self.AppendItem(open)
        
        save = wx.MenuItem(self, wx.ID_OPEN, "&Save", "Save project")
        save.SetBitmap(wx.Bitmap('icons/save.png'))
        self.AppendItem(save)
        
        self.AppendSeparator()
        self.Append(wx.ID_EXIT, "&Quit", "Quit application")
        
class EditMenu(wx.Menu):
    """Custom Edit menu"""
    def __init__(self, *args, **kwargs):
        wx.Menu.__init__(self, *args, **kwargs)
        self.Append(wx.ID_UNDO, "&Undo", "Cancel last action")
        self.Append(wx.ID_REDO, "&Redo", "Redo cancelled action")
        self.AppendSeparator()
        self.Append(wx.ID_PROPERTIES, "&Properties", "Edit project properties")
        
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
        self.SetStatusWidths([-1, 60, 60])
     
class MyToolBar(wx.ToolBar):
    def __init__(self, *args, **kwargs):
        wx.ToolBar.__init__(self, *args, **kwargs)
        self.AddSimpleTool(wx.ID_NEW, wx.Image('icons/new.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "New", "Create new project")
        self.AddSimpleTool(wx.ID_SAVE, wx.Image('icons/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "Save", "Save to filesystem")
        self.AddSeparator()
        self.AddSimpleTool(wx.ID_EXIT, wx.Image('icons/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "Exit", "Exit RP")
        self.Realize()

class ViewZone(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.SetBackgroundColour(wx.BLACK)
        
class ControlZone(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        # building components
        slider1 = wx.Slider(self, -1, 0, 0, 1000)
        pause = wx.BitmapButton(self, -1, wx.Bitmap('icons/new.png'))
        play  = wx.BitmapButton(self, -1, wx.Bitmap('icons/save.png'))
        next  = wx.BitmapButton(self, -1, wx.Bitmap('icons/new.png'))
        prev  = wx.BitmapButton(self, -1, wx.Bitmap('icons/save.png'))
        volume = wx.BitmapButton(self, -1, wx.Bitmap('icons/new.png'))
        slider2 = wx.Slider(self, -1, 0, 0, 100, size=(120, -1))

        # positioning them around
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(slider1, 1)
        
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(pause)
        hbox2.Add(play, flag=wx.RIGHT, border=5)
        hbox2.Add(next, flag=wx.LEFT, border=5)
        hbox2.Add(prev)
        hbox2.Add((150, -1), 1, flag=wx.EXPAND | wx.ALIGN_RIGHT)
        hbox2.Add(volume, flag=wx.ALIGN_RIGHT)
        hbox2.Add(slider2, flag=wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, border=5)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox1, 1, wx.EXPAND | wx.BOTTOM, 10)
        vbox.Add(hbox2, 1, wx.EXPAND)
        self.SetSizer(vbox)
        
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, wx.ID_ANY, 'Rehearsal Player')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()