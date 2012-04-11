# player.py

import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(350, 300))
        #panel = wx.Panel(self, -1)
        
        #------------------------------------------------ building menu bar
        menubar = MyMenuBar()
        
        #---------------------------------------------- building status bar
        status = wx.StatusBar(self, wx.ID_ANY)
        status.SetFieldsCount(3)
        status.SetStatusWidths([-1, 60, 60])
        self.SetStatusBar(status)

        #----------------------------------------------- building toolbar 1
        toolbar = wx.ToolBar(self, wx.ID_ANY, style=wx.TB_HORIZONTAL)
        toolbar.AddSimpleTool(1, wx.Image('icons/new.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "New", "Create new project")
        toolbar.AddSimpleTool(2, wx.Image('icons/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "Save", "Save to filesystem")
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(3, wx.Image('icons/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "Save", "Save to filesystem")
        toolbar.Realize()
        
        #----------------------------------------------- building toolbar 2
        toolbar2 = wx.ToolBar(self, wx.ID_ANY, style=wx.TB_HORIZONTAL)
        toolbar2.AddSimpleTool(1, wx.Image('icons/new.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "New", "Create new project")
        toolbar2.AddSimpleTool(2, wx.Image('icons/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "Save", "Save to filesystem")
        toolbar2.AddSeparator()
        toolbar2.AddSimpleTool(3, wx.Image('icons/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "Save", "Save to filesystem")
        toolbar2.Realize()
        
        #-------------------------------------------------------- main view
        pnl1 = wx.Panel(self, -1)
        pnl1.SetBackgroundColour(wx.BLACK)
        
        #----------------------------------------------------- control zone
        # building components
        pnl2 = wx.Panel(self, -1 )
                
        slider1 = wx.Slider(pnl2, -1, 0, 0, 1000)
        pause = wx.BitmapButton(pnl2, -1, wx.Bitmap('icons/new.png'))
        play  = wx.BitmapButton(pnl2, -1, wx.Bitmap('icons/save.png'))
        next  = wx.BitmapButton(pnl2, -1, wx.Bitmap('icons/new.png'))
        prev  = wx.BitmapButton(pnl2, -1, wx.Bitmap('icons/save.png'))
        volume = wx.BitmapButton(pnl2, -1, wx.Bitmap('icons/new.png'))
        slider2 = wx.Slider(pnl2, -1, 0, 0, 100, size=(120, -1))

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
        pnl2.SetSizer(vbox)

        #----------------------------------- positioning in top-level frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(toolbar, 0, flag=wx.EXPAND|wx.TOP)
        sizer.Add(toolbar2, 0, flag=wx.EXPAND|wx.TOP)
        sizer.Add(pnl1, 1, flag=wx.EXPAND)
        sizer.Add(pnl2, flag=wx.EXPAND | wx.BOTTOM | wx.TOP)

        #------------------------------------------------ top-level characs
        self.SetMinSize((350, 300))
        self.SetMenuBar(menubar)
        
        self.SetSizer(sizer)
        self.Centre()
    
        #------------------------------------------------ bindings creation
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        
    def OnExit(self, ev):
        self.Close()
        
class MyMenuBar(wx.MenuBar):
    def __init__(self, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)
        
        # top-level menus
        file = wx.Menu()
        play = wx.Menu()
        view = wx.Menu()
        tools = wx.Menu()
        favorites = wx.Menu()
        help = wx.Menu()

        # filling menus
        file.Append(wx.ID_EXIT, '&quit', 'Quit application')
        
        # adding menus to the menu bar
        self.Append(file, '&File')
        self.Append(play, '&Play')
        self.Append(view, '&View')
        self.Append(tools, '&Tools')
        self.Append(favorites, 'F&avorites')
        self.Append(help, '&Help')
        
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'Player')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()