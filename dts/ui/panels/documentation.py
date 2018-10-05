import wx
from dts.ui.controls.web import CPL_WebControl

class DocumentationPanel(CPL_WebControl):
	def __init__(self, parent):
		CPL_WebControl.__init__(self, parent)
		app_path = self.GetTopLevelParent().parent.path