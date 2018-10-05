import wx
import dts
#import dts.ui.evt

class DataExplore(dts.ui.panels.NotebookChildPanel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, id=-1, style=wx.EXPAND)
		self.window = self.GetTopLevelParent()
		self.ds = self.window.data
		sizer = wx.BoxSizer(wx.HORIZONTAL)

		self.set_data_tree()
		self.infopanel = wx.Panel(self, -1, style=wx.EXPAND | wx.GROW)
		#self.infopanel.SetBackgroundColour('Yellow')
		
		sizer.Add(self.dtree, 1, wx.EXPAND | wx.GROW | wx.ALL)
		sizer.Add(self.infopanel, 1, wx.EXPAND | wx.GROW | wx.ALL)
		self.SetSizer(sizer)
		

	def set_data_tree(self):
		self.dtree = wx.TreeCtrl(self, -1)
		dset = self.dtree.AddRoot('Dataset: '+ self.ds.name)

		for ch in self.ds.channels:
			channel = self.ds.channels[ch]
			chn = self.dtree.AppendItem(dset, channel.name)
			self.dtree.AppendItem(chn, 'Data')
			self.dtree.AppendItem(chn, 'Geo Data')
			self.dtree.AppendItem(chn, 'Raw Data')
			

	def update(self):
		pass