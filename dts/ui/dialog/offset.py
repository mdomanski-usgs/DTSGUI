import wx


class OffsetDialog(wx.Dialog):

    def __init__(self, parent, id, title="Cable Offset and Interval", offset=0, interval=1):
        super(OffsetDialog, self).__init__(parent, title=title)

        self.offset = float(offset)
        self.interval = float(interval)

        self.SetAutoLayout(True)

        sizer = wx.GridBagSizer(vgap=20, hgap=15)

        type_lbl = wx.StaticText(self, label="Distance Offset:")
        sizer.Add(type_lbl, (1, 1), (1, 1), wx.RIGHT)

        self.offset_ctrl = wx.TextCtrl(self, -1, value='{0}'.format(self.offset), validator=FloatValidator(),
                                       name='Offset')
        sizer.Add(self.offset_ctrl, (1, 2), (1, 1), wx.EXPAND)

        meter0 = wx.StaticText(self, label="meters")
        sizer.Add(meter0, (1, 3), (1, 1), wx.LEFT)

        detail_lbl = wx.StaticText(self, label="Sample Spacing:")
        sizer.Add(detail_lbl, (2, 1), (1, 1), wx.RIGHT)

        self.interval_ctrl = wx.TextCtrl(self, -1, value='{0}'.format(self.interval), validator=FloatValidator(),
                                         name='Interval')
        sizer.Add(self.interval_ctrl, (2, 2), (1, 1), wx.EXPAND)

        meter1 = wx.StaticText(self, label="meters")
        sizer.Add(meter1, (2, 3), (1, 1), wx.LEFT)

        btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(btnsizer, (3, 1), (1, 3), wx.EXPAND | wx.ALL)

        self.SetSizer(sizer)

        self.offset_ctrl.SetFocus()

    def get_offset(self):
        return float(self.offset_ctrl.GetValue())

    def get_interval(self):
        return float(self.interval_ctrl.GetValue())


class FloatValidator(wx.PyValidator):

    def __init__(self):
        wx.PyValidator.__init__(self)

    def Clone(self):
        return FloatValidator()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()

        try:
            float(text)
            return True
        except ValueError:
            text_ctrl_name = textCtrl.GetName()
            wx.MessageBox(text_ctrl_name + " must be numerical.", "Invalid value")
            textCtrl.SetFocus()
            return False

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True