import dts.ui.dialog.file_io as IO
import wx

def new_channel_dialog():
  choices = [ 'Open an existing DTS GUI file', 'Import a Sensornet data directory']
  dialog = wx.SingleChoiceDialog ( None, text, 'Choose a data set', choices )
  