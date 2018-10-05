from dts.ui.plot.main.axes import *

class ColorBar(AxesBase):
	name = 'ColorBar'
	def __init__(self, *args, **kwargs):
		AxesBase.__init__(self, *args, **kwargs)
		self.set_visible(False)
		self.cbar = self.figure.colorbar(
						self.figure.parent.main.image,
						cax=self,
						extend='neither'
					)
		
		self.set_ylabel(u'Temperature (\u00b0C)')
		self.yaxis.set_label_position('left')

 		for tick in self.yaxis.iter_ticks():
 			tick[0].label2On = False
 			tick[0].label1On = True


	def set_visible(self, visible=True):
		spacer = self.gridspec.columns.before
		if visible: spacer.show()
		else: spacer.hide()
		AxesBase.set_visible(self, visible, orientation="columns", index=0)
