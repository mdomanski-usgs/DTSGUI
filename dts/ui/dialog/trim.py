"""
**Deprecated file**

This functionality is now contained in :py:mod:`dts.ui.panels.trim_raw`.
"""
import wx

class TrimDialog(wx.Dialog):
	def __init__(self, parent, id, title, channel):
		wx.Dialog.__init__(self, parent, id, title)
		self.do_layout()

	def do_layout(self):
		
		panel = wx.Panel(self, -1)
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox_inner = wx.BoxSizer(wx.VERTICAL)
		
		b1 = wx.StaticBox(panel, -1, 'Distance range')
		sizer = wx.StaticBoxSizer(b1, wx.VERTICAL)
		
		c = dict()
		t = dict() # dict to make accesing axis text objects easier
		
		box = wx.GridBagSizer()
		box.Add(wx.StaticText(panel, -1, 'Min:'), (0,0),(1,1))
		c['x_min'] =  wx.SpinCtrl(panel, -1, '0', min=0, max=10)
		box.Add(c['x_min'],(0,1),(1,2))
		t['x_min'] = wx.StaticText(panel, -1, 'Min:')
		box.Add(t['x_min'], (0,3),(1,2))
		
		box.Add(wx.StaticText(panel, -1, 'Max:'), (1,0),(1,1))
		c['x_max'] =  wx.SpinCtrl(panel, -1, '0', min=0, max=10)
		box.Add(c['x_max'],(1,1),(1,2))
		
		
		sizer.Add(box, 0, wx.EXPAND)
		vbox_inner.Add(sizer)
		
		b2 = wx.StaticBox(panel, -1, 'Time range', style=wx.EXPAND)		
		sizer = wx.StaticBoxSizer(b2, wx.VERTICAL)
		
		box = wx.GridBagSizer()
		box.Add(wx.StaticText(panel, -1, 'Min:'), (0,0),(1,1))
		c['t_min'] =  wx.SpinCtrl(panel, -1, '0', min=0, max=10)
		box.Add(c['t_min'],(0,1),(1,2))
		
		box.Add(wx.StaticText(panel, -1, 'Max:'), (1,0),(1,1))
		c['t_max'] =  wx.SpinCtrl(panel, -1, '0', min=0, max=10)
		box.Add(c['t_max'],(1,1),(1,2))
		
		sizer.Add(box, 0, wx.EXPAND)
		vbox_inner.Add(sizer)	
		
		
		vbox_inner.AddSpacer(10)
		
		btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
 		vbox_inner.Add(btnsizer,wx.EXPAND)
 		
 		vbox_inner.AddSpacer(10)


		panel.SetSizer(vbox_inner, wx.EXPAND)
		
		vbox.Add(panel)
		self.SetSizer(vbox, wx.EXPAND)

 	def _onOk(self, event):
 		
 		self.values = dict()
 		for key, control in self.controls.items():
 			self.trim = True # a kludge in place of proper event handling
 			self.values[key] = control.GetValue() # Gets the value of each control and sets the appropriate value.
 		self.Close()
		
 	def _onCancel(self, event):
 		self.Close()
#  		
# class TrimDialog(wx.Dialog):
# 	def __init__(self, parent, id, title, offset=0, interval=1):
# 		wx.Dialog.__init__(self, parent, id, title, size=(280, 250))
# 		self.do_layout()
# 
# 	def do_layout(self):
# 		
# 		
# 		panel = wx.Panel(self, -1)
# 		vbox = wx.BoxSizer(wx.VERTICAL)
# 		
# 		
# 		x_Box = wx.StaticBox(panel, -1, "Distance Range")
# 		x_StaticSizer = wx.StaticBoxSizer(x_Box, wx.VERTICAL | wx.EXPAND)
# 		x_Box.SetSizer(x_BoxSizer)
# 		x_BoxSizer = wx.BoxSizer(wx.VERTICAL)
# 		
# 		def control(parent, label, value, min=0, max=100):			
# 			box = wx.BoxSizer(wx.HORIZONTAL)
# 			box.Add(wx.StaticText(box, -1, label))
# 			ctrl =  wx.SpinCtrl(box, -1, value, min=min, max=max)
# 			box.Add(ctrl)
# 			parent.Add(box)
# 		
# 		
# 		c = dict()
# 		c['x_min'] = control(x_Box, 'Min:', 0)
# 		c['x_max'] = control(x_Box, 'Max:', 100)
# 
# 		btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
# 		vbox.Add(btnsizer,-1, wx.EXPAND|wx.ALL)
# 
#  		self.SetSizer(vbox)
#  		
#  	def _onOk(self, event):
#  		
#  		self.values = dict()
#  		for key, control in self.controls.items():
#  			self.trim = True # a kludge in place of proper event handling
#  			self.values[key] = control.GetValue() # Gets the value of each control and sets the appropriate value.
#  		self.Close()
# 		
#  	def _onCancel(self, event):
#  		self.Close()