import os
import wx
import wx.media
import wx.lib.buttons as buttons

dir_name=os.path.dirname(os.path.abspath(__file__))
image_dir=os.path.join(dir_name,'data')

def to_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

class Media_Panel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent=parent)

        self.frame=parent
        self.current_volume=50
        self.vol_label=wx.StaticText(self,wx.ID_ANY,str(self.current_volume)+"  ")
        self.cur_label=wx.StaticText(self,wx.ID_ANY,"")
        self.max_label=wx.StaticText(self,wx.ID_ANY,"")
        self.mode="Music"
        self.create_menu()
        self.layout_controls()

        sp=wx.StandardPaths.Get()
        self.current_folder=sp.GetDocumentsDir()

        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.on_timer)
        self.timer.Start(100)

    def layout_controls(self):
        try:
            self.media_player=wx.media.MediaCtrl(self,style=wx.SIMPLE_BORDER)
        except NotImplementedError:
            self.Destroy()
       	    raise
        self.media_player.SetVolume(self.current_volume/float(100))
        self.playback_slider=wx.Slider(self,size=wx.DefaultSize)
        self.Bind(wx.EVT_SLIDER,self.on_seek,self.playback_slider)
        self.volume_control=wx.Slider(self,size=wx.DefaultSize)
        self.volume_control.SetRange(0,100)
        self.volume_control.SetValue(self.current_volume)
        self.volume_control.Bind(wx.EVT_SLIDER,self.on_set_volume)
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0,0),1)
        volsizer=wx.BoxSizer(wx.HORIZONTAL)
        volsizer.Add(wx.StaticText(self,wx.ID_ANY,"Volume: "),0,wx.ALIGN_CENTER_VERTICAL)
        volsizer.Add(self.vol_label,0,wx.ALIGN_CENTER)  # Requires an update on volume change
        volsizer.Add(self.volume_control,1,wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(volsizer,0,wx.EXPAND|wx.ALL)
        sizer.Add(wx.Button(self,-1,'Text'),0,wx.EXPAND|wx.ALL)
        hsizer=wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.playback_slider,1,wx.EXPAND|wx.ALL)
        timesizer=wx.BoxSizer(wx.VERTICAL)
        timesizer.Add(self.cur_label,0)
        timesizer.Add(self.max_label,0)
        hsizer.Add(timesizer,0,wx.EXPAND|wx.ALL)
        sizer.Add(hsizer,0,wx.EXPAND|wx.ALL)

        self.SetSizer(sizer)
        self.Layout()

    def build_audio_bar(self):
        audio_bar_sizer=wx.BoxSizer(wx.HORIZONTAL)
        # Missing everything really
        return audio_bar_sizer

	def build_button(self,btn_dict,sizer):
		icn=btn_dict['icon']
		handler=btn_dict['handler']

		img=wx.Bitmap(os.path.join(image_dir,icn))
		btn=buttons.GenBitmapButton(self,bitmap=img,name=btn_dict['name'])
		btn.SetInitialSize()
		btn.bind(wx.EVT_BUTTON,handler)
		sizer.Add(btn,0,wx.LEFT,3)

    def create_menu(self):
        menubar=wx.MenuBar()
        file_menu=wx.Menu()
        mode_menu=wx.Menu()
        open_file_menu_item=file_menu.Append(wx.ID_OPEN,"&Open","Open a File")
        quit_file_menu_item=file_menu.Append(wx.ID_EXIT,"&Quit","Quit")
        music_mode=mode_menu.AppendRadioItem(wx.NewId(),"&Music","In music player mode.")
        video_mode=mode_menu.AppendRadioItem(wx.NewId(),"&Video","In video player mode.")
        youtube_mode=mode_menu.AppendRadioItem(wx.NewId(),"&Youtube","In Youtube player mode.")
        menubar.Append(file_menu,"&File")
        menubar.Append(mode_menu,"&Mode")
        self.frame.SetMenuBar(menubar)
        self.frame.Bind(wx.EVT_MENU,self.on_browse,open_file_menu_item)
        self.frame.Bind(wx.EVT_MENU,self.on_exit,quit_file_menu_item)
        self.frame.Bind(wx.EVT_MENU,self.to_music,music_mode)
        self.frame.Bind(wx.EVT_MENU,self.to_video,video_mode)
        self.frame.Bind(wx.EVT_MENU,self.to_youtube,youtube_mode)
        # Mode change bindings go here

    def load_music(self,music_file):
        if not self.media_player.Load(music_file):
            wx.MessageBox("Unable to load %s." % music_file,
                "ERROR",
                wx.ICON_ERROR | wx.OK)
        else:
            self.media_player.SetInitialSize()
            self.playback_slider.SetRange(0,self.media_player.Length())
            #self.playPauseBtn.Enable(True) 
            self.max_label.SetLabel(" "+str(to_time((self.media_player.Length()/float(1000))))+" ")
            self.media_player.Play()

    def on_browse(self,event):
        wildcard="MP3 (*.mp3)|*.mp3|"   \
                 "WAV (*.wav)|*.wav|"    \
                 "OGG (*.ogg)|*.ogg"
        dlg=wx.FileDialog(self,message="Choose a file",
            defaultDir=self.current_folder,
            defaultFile='',
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR)
        if dlg.ShowModal()==wx.ID_OK:
            path=dlg.GetPath()
            self.current_folder=os.path.dirname(path)
            self.load_music(path)
        dlg.Destroy()

    def on_seek(self,e):
        self.media_player.Seek(self.playback_slider.GetValue())

    def on_set_volume(self,e):
        self.current_volume=self.volume_control.GetValue()
        self.vol_label.SetLabel(str(self.current_volume)+"  ")
        self.media_player.SetVolume(self.current_volume/float(100))

    def on_exit(self,e):
        self.frame.Close(True)

    def to_music(self,e):
        if self.mode != "Music":
            self.mode = "Music"

    def to_video(self,e):
        if self.mode != "Video":
            self.mode = "Video"

    def to_youtube(self,e):
        if self.mode != "Youtube":
            self.mode = "Youtube"

    def on_timer(self,event):
        offset=self.media_player.Tell()
        self.cur_label.SetLabel(" "+str(to_time((offset/float(1000))))+" ")
        self.playback_slider.SetValue(offset)

class Media_Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,wx.ID_ANY,"__a Music Player",size=(650,500))
        panel=Media_Panel(self)

if __name__=="__main__":
    app=wx.App(False)
    frame=Media_Frame()
    frame.Show()
    app.MainLoop()
