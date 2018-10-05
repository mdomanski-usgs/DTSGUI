import wx
from dts.ui.dialog.import_dsv import ImportWizardDialog

def import_geodata(parent=None):
	
	dlg = wx.FileDialog(parent, "Choose a file with geospatial coordinates", ".", "",
						"CSV files (*.csv)|*.csv|Text files (*.txt)|*.txt|All files (*.*)|*.*",
						wx.OPEN)
	if dlg.ShowModal() == wx.ID_OK:
		path = dlg.GetPath()
		dlg.Destroy()


		dlg = ImportWizardDialog(parent, -1, 'Import Coordinates for Geospatial Reference', path, field_choices=['Distance', 'Latitude', 'Longitude'])
		if dlg.ShowModal() == wx.ID_OK:
			data, metadata = dlg.ImportData()		

			if dlg.data is not None:
				fields =  dlg.delimPanel.GetPreviewFields()
				
				#if type is 'eastingnorthing': self.raw.attrs['type'] = 'eastingnorthing'
				#else: self.raw.attrs['type'] = 'latlon'
		
				import numpy as N
				
				f = lambda x: dlg.data[:,fields[x]].astype('float')
				
 				data = N.vstack((f('Distance'), f('Latitude'), f('Longitude')))

 				
			dlg.Destroy()
			return data, metadata
		else:
			dlg.Destroy()
			return None, None

	else:
		dlg.Destroy()
		return None, None
	