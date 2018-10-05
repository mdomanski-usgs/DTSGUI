import wx
import dts
from dts.ui.panels import NotebookChildPanel as Panel
from dts.ui.controls import Fieldset, SubsetCtrl
from dts.ui.plot.etc import timestamp2date
import logging as log

class RangeControl(Panel):
	list = None
	range = None
	labels = {
		"min": "Min",
		"max": "Max"
	}
	def __init__(self, parent, label="Range", extents=None):
		Panel.__init__(self,parent, id=wx.ID_ANY)

		box = wx.StaticBox(self, -1, label)
		self.boxsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
		self.SetSizer(self.boxsizer)

		if extents is None:
			extents = {
				"min": self.range[0],
				"max": self.range[1]
			}

		
		self.min = self.control(self.labels["min"], extents["min"], range=(0, extents["max"]-1))
		self.max = self.control(self.labels["max"], extents["max"], range=(extents["min"]+1, len(self.list)-1))

		for i in [self.min, self.max]:
			i.Bind(dts.ui.evt.EVT_VALUE_UPDATED, self.on_set_value)


	def on_set_value(self, event):
		if event.source == self.min:
			self.max.SetRange(event.value+1, self.max.GetMax())
		if event.source == self.max:
			self.min.SetRange(self.min.GetMin(), event.value-1)
		event.Skip()

	def set_extents(self, extents):
		self.set_min(extents["min"])
		self.set_max(extents["max"])

	def get_extents(self):
		return {"min": self.get_min(), "max": self.get_max()}

	def control(self, label, value=0, range=(0,100)):
		control = SubsetCtrl(self, self.formatter, value, range, size=(150,-1))
		field = Fieldset(self, label, control = control)
		self.boxsizer.Add(field)
		return control

	def set_min(self, value):
		self.min.SetValue(value)

	def set_max(self, value):
		self.max.SetValue(value)

	def get_min(self):
		return self.min.GetValue()

	def get_max(self):
		return self.max.GetValue()

	def formatter(self, value):
		return value

class SpaceRangeControl(RangeControl):
	def __init__(self, parent, title, data=None, **kwargs):
		if data is None:
			window = dts.ui.window
			self.channel = window.status.get_current_channel()
			self.data = self.channel.data.get_array()
		else:
			self.data = data
		self.array = self.data.get_array()
		self.list = range(self.array.shape[1])
		self.range = [0, self.array.shape[1]-1]

		RangeControl.__init__(self, parent, title, **kwargs)
		
	def formatter(self, value):
		dst = value*self.data.attrs['dst_interval']+self.data.attrs['dst_offset']
		return str(dst) + " m"

class TimeRangeControl(RangeControl):
	labels = {
		"min": "Start",
		"max": "End"
	}
	def __init__(self, parent, title, data=None, **kwargs):
		self.date_format = dts.ui.time_format.get_format(False)

		if data is None:
			window = dts.ui.window
			self.channel = window.status.get_current_channel()
			self.data = self.channel.data
		else:
			self.data = data
		self.array = self.data.get_array()
		self.list = self.data.attrs['times']
		self.range = [0, self.array.shape[0]-1]
		RangeControl.__init__(self, parent, title, **kwargs)


	def formatter(self, value):
		return timestamp2date(self.list[value], format=self.date_format)