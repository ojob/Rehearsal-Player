# player.py

import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(350, 300))
        #panel = wx.Panel(self, -1)
        menubar = wx.MenuBar()
        file = wx.Menu()
        play = wx.Menu()
        view = wx.Menu()
        tools = wx.Menu()
        favorites = wx.Menu()
        help = wx.Menu()

        file.Append(101, '&quit', 'Quit application')

        menubar.Append(file, '&File')
        menubar.Append(play, '&Play')
        menubar.Append(view, '&View')
        menubar.Append(tools, '&Tools')
        menubar.Append(favorites, 'F&avorites')
        menubar.Append(help, '&Help')


        toolbar = wx.ToolBar(self, wx.ID_ANY, style=wx.TB_HORIZONTAL)
        toolbar.AddSimpleTool(1, wx.Image('icons/new.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "New", "Create new project")
        toolbar.AddSimpleTool(2, wx.Image('icons/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "Save", "Save to filesystem")
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(3, wx.Image('icons/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "Save", "Save to filesystem")
        toolbar.Realize()
        toolbar2 = wx.ToolBar(self, wx.ID_ANY, style=wx.TB_HORIZONTAL)
        toolbar2.AddSimpleTool(1, wx.Image('icons/new.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "New", "Create new project")
        toolbar2.AddSimpleTool(2, wx.Image('icons/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "Save", "Save to filesystem")
        toolbar2.AddSeparator()
        toolbar2.AddSimpleTool(3, wx.Image('icons/save.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(), "Save", "Save to filesystem")
        toolbar2.Realize()
        
        pnl1 = wx.Panel(self, -1)
        pnl1.SetBackgroundColour(wx.BLACK)
        pnl2 = wx.Panel(self, -1 )
                
        slider1 = wx.Slider(pnl2, -1, 0, 0, 1000)
        pause = wx.BitmapButton(pnl2, -1, wx.Bitmap('icons/new.png'))
        play  = wx.BitmapButton(pnl2, -1, wx.Bitmap('icons/save.png'))
        next  = wx.BitmapButton(pnl2, -1, wx.Bitmap('icons/new.png'))
        prev  = wx.BitmapButton(pnl2, -1, wx.Bitmap('icons/save.png'))
        volume = wx.BitmapButton(pnl2, -1, wx.Bitmap('icons/new.png'))
        slider2 = wx.Slider(pnl2, -1, 0, 0, 100, size=(120, -1))

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        hbox1.Add(slider1, 1)
        hbox2.Add(pause)
        hbox2.Add(play, flag=wx.RIGHT, border=5)
        hbox2.Add(next, flag=wx.LEFT, border=5)
        hbox2.Add(prev)
        hbox2.Add((150, -1), 1, flag=wx.EXPAND | wx.ALIGN_RIGHT)
        hbox2.Add(volume, flag=wx.ALIGN_RIGHT)
        hbox2.Add(slider2, flag=wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, border=5)

        vbox.Add(hbox1, 1, wx.EXPAND | wx.BOTTOM, 10)
        vbox.Add(hbox2, 1, wx.EXPAND)
        pnl2.SetSizer(vbox)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(toolbar, 0, flag=wx.EXPAND|wx.TOP)
        sizer.Add(toolbar2, 0, flag=wx.EXPAND|wx.TOP)
        sizer.Add(pnl1, 1, flag=wx.EXPAND)
        sizer.Add(pnl2, flag=wx.EXPAND | wx.BOTTOM | wx.TOP)

        self.SetMinSize((350, 300))
        self.SetMenuBar(menubar)
        
        status = wx.StatusBar(self, wx.ID_ANY)
        status.SetFieldsCount(3)
        status.SetStatusWidths([-1, 60, 60])
        self.SetStatusBar(status)
        
        self.SetSizer(sizer)
        self.Centre()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'Player')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()