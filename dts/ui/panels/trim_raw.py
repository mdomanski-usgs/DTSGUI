import wx
from dts.ui.plot import PlotImage
from dts.ui.panels import NotebookChildPanel as Panel
from dts.ui.plot.main.toolbar import MainPlotToolbar
from dts.ui.panels.subset_editor import ExtentsCtrlPanel
from dts.ui.controls import Fieldset, ChannelSelectCtrl
from matplotlib.patches import Rectangle

class TrimRaw(Panel):
	def __init__(self, parent, channel=None):
		Panel.__init__(self, parent, id=-1, style=wx.EXPAND | wx.GROW)
		window = self.GetTopLevelParent()
		if channel == None:
			self.channel = window.status.current_channel
		else:
			self.channel = channel

		self.__update_data()
		self.__doLayout()
	
	def __update_data(self):
		#self.channel = self.ds.get_working_channel()
		self.data = self.channel.data_raw

	def __doLayout(self):
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.plot = PlotImage(self, self.channel.data_raw)
		self.cpanel = TrimRawCtrlPanel(self, self.channel.data)
		sizer.Add(self.cpanel, 0, wx.EXPAND)

		sizer.Add(self.plot, 1, wx.EXPAND | wx.GROW | wx.ALL, 0)

		self.SetSizer(sizer)
	
	def update(self):
		pass
		
class TrimRawCtrlPanel(ExtentsCtrlPanel):
	def __init__(self, parent, data):
		self.parent = parent
		ExtentsCtrlPanel.__init__(self, parent, "Trim Raw Data", subset=data, dataset=parent.channel.data_raw)
		
	def on_accept(self, evt):
		extents = self.get_xy_extents()
		#print extents
		#print "Subset edited."
		self.parent.channel.trim_raw(**extents)
		self.on_cancel(evt)

	def __channelControls(self):
		insizer = wx.BoxSizer(wx.VERTICAL)
		
		self.channel_selector = Fieldset(self, "Select channel for trimming", control=ChannelSelectCtrl(self))
		insizer.Add(self.channel_selector)
	
		self.sizer.Add(insizer, wx.GBPosition(0,0), None, wx.EXPAND|wx.GROW|wx.ALL, 5)
		self.channel_selector["control"].Bind(wx.EVT_LISTBOX, self.on_change_channel)
	
	def on_change_channel(self, evt):
		window = self.GetTopLevelParent()
		sel = self.channel_selector["control"].GetSelection()
		window.data.set_working_channel(num=sel)
		self.__update_data()
		self.plot.data = self.data_raw
	

	



