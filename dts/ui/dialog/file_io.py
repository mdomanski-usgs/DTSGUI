"""Module containing shortcuts for common file and directory choice operations."""

import wx
import os


def choose_dir(title):
    dlg = wx.DirDialog(None, title, style=wx.DD_DEFAULT_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    else:
        path = False
    dlg.Destroy()
    return path


def choose_file(title, wildcard="*.*"):
    dlg = wx.FileDialog(None, message=title, defaultDir=os.getcwd(), defaultFile="", style=wx.OPEN | wx.CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    else:
        path = False
    dlg.Destroy()
    return path


def save_file(title, wildcard="*.*"):
    dlg = wx.FileDialog(None, message=title, defaultDir=os.getcwd(), defaultFile="", wildcard=wildcard,
                        style=wx.SAVE | wx.CHANGE_DIR | wx.OVERWRITE_PROMPT)
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    else:
        path = False
    dlg.Destroy()
    return path
