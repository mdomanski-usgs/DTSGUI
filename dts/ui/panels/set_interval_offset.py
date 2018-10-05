import wx
#from wx.lib.masked.numctrl import NumCtrl
#from wx.lib.agw.floatspin import FloatSpin
from dts.ui.controls import Fieldset
from dts.ui.panels import Panel
import dts
import logging as log

class FloatControl(wx.TextCtrl):
	def __init__(self, parent, value=0):
		value = '{0}'.format(value)
		wx.TextCtrl.__init__(self, parent, value=value)
		self.lastGoodValue = value
		self.Bind(wx.EVT_TEXT_ENTER, self.__onAction)

	def __onAction(self, event):
		raw_value = self.GetValue().strip()
		# numeric check
		if all(x in '0123456789.+-' for x in raw_value):
			n = round(float(raw_value), 4)
			self.ChangeValue("%9.4f" % (n))
			self.lastGoodValue = self.GetValue()
		else:
			self.ChangeValue(self.lastGoodValue)	
		event.Skip()

class OffsetPanel(Panel):
	has_previewed = False
	def __init__(self, parent):
		Panel.__init__(self, parent, style=wx.EXPAND)
		self.window = self.GetTopLevelParent()
		self.__doLayout()
		
	def __doLayout(self):
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		dataset = self.window.data.ch
		offset_ctrl = FloatControl(self, dataset.get_offset())
		self.offset = Fieldset(self, 'Offset (meters)', control=offset_ctrl)
		
		sizer.Add(self.offset, 0, wx.ALL, 5)
		
		interval_ctrl = FloatControl(self, dataset.get_interval())
		self.interval = Fieldset(self, 'Interval (meters)', control=interval_ctrl)
		sizer.Add(self.interval, 0, wx.ALL, 5)
		

		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.buttons = {}
		self.buttons["preview"] = wx.Button(self, -1, 'Preview')
		self.buttons["accept"] = wx.Button(self, -1, "Set")
		self.buttons["cancel"] = wx.Button(self, -1, 'Cancel')
		
		for item in ["preview","accept", "cancel"]:
			button_sizer.Add(self.buttons[item], 0, wx.ALIGN_RIGHT|wx.LEFT, 5)
		
		self.Bind(wx.EVT_BUTTON, self.__onSet, id=self.buttons["accept"].GetId())
		self.Bind(wx.EVT_BUTTON, self.__onPreview, id=self.buttons["preview"].GetId())
		self.Bind(wx.EVT_BUTTON, self.__onCancel, id=self.buttons["cancel"].GetId())
		
		sizer.Add(button_sizer, 0, wx.TOP, 20)

		self.SetSizer(sizer)
		
		self.offset['control'].SetFocus()

		wx.FutureCall(1, self.Layout)

	def reset(self):
		log.info("Resetting offset and interval to currently saved values.")
		self.__setOffset(final=True)

	def Delete(self):
		self.Parent.Close()
	
	def __onCancel(self,event):
		if self.has_previewed:
			self.reset()

		self.Delete()

	def __onPreview(self, event):
		interval = float(self.interval['control'].GetValue())
		offset = float(self.offset['control'].GetValue())
		self.__setOffset(interval, offset, False)
		self.has_previewed = True
		log.info("Setting inteval and offset for preview.")


	def __onSet(self, event):
		log.info("Setting final interval and offset.")
		interval = float(self.interval['control'].GetValue())
		offset = float(self.offset['control'].GetValue())
		self.__setOffset(interval, offset, True)

		self.Delete()
		
	def __setOffset(self, interval=None, offset=None, final=False):
		
		channel = self.window.data.get_current_channel()

		if interval is None:
			interval = channel.get_interval()
		if offset is None:
			offset = channel.get_offset()

		if final:
			channel.set_interval_offset(interval, offset)
		
		interp_lengths = channel.geodata.interpolate(interval, offset)
			
		event = dts.ui.evt.OffsetSetEvent(-1,
					offset=offset,
					interval=interval,
					final = final,
					interpolated = interp_lengths
					)
		wx.PostEvent(self, event)
		
		log.info("Interval: {0}, Offset: {1}".format(interval, offset))

