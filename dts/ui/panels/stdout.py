import sys
import wx

class LogPanel(wx.Panel):
	def __init__(self, parent=-1):
		wx.Panel.__init__(self, -1)
		self.log = wx.TextCtrl(panel, -1, size=(500,400), style = wx.TE_MULTILINE|wx.TE_READONLY| wx.HSCROLL)
		redir=RedirectText(self.log)
		sys.stdout=redir
		print 'Started logging'