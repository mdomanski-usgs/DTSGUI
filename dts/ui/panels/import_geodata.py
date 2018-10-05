import wx
import dts
from dts.ui.controls import SubsetCtrl, Fieldset
from dts.ui.dialog.import_dsv import *
from dts.ui.panels import NotebookChildPanel as Panel
from dts.ui.panels import ModalPanel
import logging as log
import osr


class ImportWizardPanel(Panel):
    """
    CLASS(SUPERCLASS):
      ImportWizardDialog(wx.Dialog)
    DESCRIPTION:
      A dialog allowing the user to preview and change the options for importing
      a file.
    PROTOTYPE:
      ImportWizardDialog(parent, id, title, file,
                         pos = wx.DefaultPosition, size = wx.DefaultSize,
                         style = wx.DEFAULT_DIALOG_STYLE, name = 'ImportWizardDialog')
    ARGUMENTS:
      - parent: the parent window
      - id: the id of this window
      - title: the title of this dialog
      - file: the file to import
    METHODS:
      - GetImportInfo()
        returns a tuple (delimiters, text qualifiers, has headers)
      - ImportData(errorHandler = skipRow)
        returns (headers, data), headers may be None
        errorHandler is a callback function that instructs the method on what
        to do with irregular rows. The default skipRow function simply discards
        the bad row (see importDSV() above).
    """

    def __init__(self, parent, id, file,
                 pos = wx.DefaultPosition, size=wx.DefaultSize,
                 style = wx.EXPAND|wx.GROW, field_choices=None, meta_fields = None):
        Panel.__init__(self, parent, id, pos, size, style)
        self.window = self.GetTopLevelParent()
        self.SetAutoLayout(True)

        self.file = file
        f = open(file, 'r')
        self.data = f.read()
        f.close()

        self.buttonBox = self.ButtonBox()

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.delimPanel = ImportWizardPanel_Delimiters(self, -1, file, self.data, self.ValidState, field_choices=field_choices, meta_fields=meta_fields, style=wx.EXPAND|wx.GROW)
        self.utmZone = UTMZoneControl(self)
        utm_field = Fieldset(self, "Set UTM Zone (optional)", control=self.utmZone)

        sizer.AddMany([
            (self.delimPanel, 0, wx.EXPAND|wx.ALL, 5),
            (utm_field, 0, wx.LEFT, 15),
            (self.buttonBox, 0, wx.RIGHT | wx.ALIGN_RIGHT | wx.ALIGN_TOP, 15),
            ])

        self.SetSizer(sizer)
        self.Layout()
        sizer.Fit(self.delimPanel)
        self.Fit()
        self.Centre()

        self.buttonBox.Bind(wx.EVT_BUTTON, self.__onAccept, id=wx.ID_OK)
        self.buttonBox.Bind(wx.EVT_BUTTON, self.__onCancel, id=wx.ID_CANCEL)

    def __onAccept(self, event):
        log.debug("Import accepted.")
        data, metadata = self.ImportData()
        try:
            if data is not None:
                fields =  self.delimPanel.GetPreviewFields()

                f = lambda x: data[:,fields[x]].astype('float')
                distance = f('Distance')
                if "Easting" in fields and "Northing" in fields:
                    easting = f("Easting")
                    northing = f("Northing")
                    zone = self.utmZone.GetValue()
                    trans = UTMTransformer(zone)
                    for i,zpd in enumerate(zip(easting, northing)):
                        e, n = zpd
                        lon, lat, alt = trans.to_latlon(e,n)
                        print lat, lon
                        easting[i] = lon
                        northing[i] = lat
                    latitude = northing
                    longitude = easting

                elif "Latitude" in fields and "Longitude" in fields:
                    latitude = f("Latitude")
                    longitude = f("Longitude")
                else:
                    raise ValueError("Must set either Easting and Northing or Latitude and Longitude.")

                #if type is 'eastingnorthing': self.raw.attrs['type'] = 'eastingnorthing'
                #else: self.raw.cattrs['type'] = 'latlon'

                import numpy as N

                data = N.vstack((distance, latitude, longitude))

                self.window.data.ch.geodata.set_coords(data)
                event = dts.ui.evt.GeodataImportedEvent(-1,
                        raw_data = data,
                        channel = self.window.data.ch,
                        geodata = self.window.data.ch.geodata
                    )
                wx.PostEvent(self.GetTopLevelParent(), event)

            log.debug("Import completed.")
            wx.CallAfter(self.Parent.Delete)
            self.Destroy()

        except Exception, error:
            log.exception(error)
            self.Parent.ShowError(str(error))

    def __onCancel(self, event):
        log.debug("Import canceled.")

        wx.CallAfter(self.Parent.Delete)

    def ButtonBox(self):
        panel = wx.Panel(self, -1)
        panel.SetAutoLayout(True)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        self.ok = wx.Button(panel, wx.ID_OK, "OK")
        self.cancel = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        sizer.AddMany([
            (self.ok, 0, wx.ALIGN_TOP | wx.EAST | wx.SOUTH, 10),
            (self.cancel, 0, wx.ALIGN_TOP | wx.WEST | wx.SOUTH, 10),
            ])
        panel.Layout()
        panel.Fit()
        return panel

    def GetImportInfo(self):
        return (self.delimPanel.GetDelimiters(),
                self.delimPanel.GetTextQualifier(),
                self.delimPanel.GetHasHeaders())

    def ImportData(self, errorHandler = skipRow):
        delimiters, qualifier, hasHeaders = self.GetImportInfo()
        self.organized_data = organizeIntoLines(self.data, textQualifier = qualifier)
        """dlg = wx.ProgressDialog("Import DSV File",
                               self.file,
                               100,
                               self,
                               wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)"""
        self.imported_data = importDSV(self.organized_data,
                              delimiter = delimiters,
                              textQualifier = qualifier,
                              updateFunction = None,#dlg.Update,
                              errorHandler = errorHandler)
        if self.imported_data is None: return None
        if hasHeaders:
            headers = copy.copy(self.imported_data[0])
            del self.imported_data[0]
        else:
            headers = None

        import numpy as N
        self.imported_data = N.array(self.imported_data)

        self.metadata = None

        return self.imported_data, self.metadata

    def ValidState(self, isValid):
        self.ok.Enable(isValid)


class ErrorPanel(Panel):
    def __init__(self, parent, error):
        log.error(error)
        Panel.__init__(self, parent, id=-1, style=wx.EXPAND)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ctrl = wx.StaticText(self, label=error)
        sizer.Add(self.ctrl, 1, wx.EXPAND|wx.ALL, 5)
        self.button = wx.Button(self, -1, "Dismiss")
        sizer.Add(self.button, 0, wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL, 5)
        self.SetSizer(sizer)
        self.button.Bind(wx.EVT_BUTTON, self.on_dismiss)
        self.Parent.Layout()
        log.debug("Layout adjusted.")

    def on_dismiss(self, event):
        self.Parent.Hide()


class ImportGeodata(Panel):
    def __init__(self, parent, path):
        Panel.__init__(self, parent, id=-1, style=wx.EXPAND)
        self.window = self.GetTopLevelParent()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.modal_panel = ModalPanel(self)
        self.sizer.Add(self.modal_panel, 0, wx.EXPAND)
        self.import_panel = ImportWizardPanel(
                                self,
                                wx.ID_ANY,
                                path,
                                field_choices=['Distance', 'Latitude', 'Longitude', "Easting", "Northing", "Null Field"]
                                )

        self.sizer.Add(self.import_panel, 1, wx.EXPAND | wx.GROW | wx.ALL)
        self.SetSizer(self.sizer)

    def ShowError(self, error):
        panel = ErrorPanel(self.modal_panel, error)
        self.modal_panel.Show(panel)


def import_geodata(parent=None):

    dlg = wx.FileDialog(parent, "Choose a file with geospatial coordinates", ".", "",
                        "All files (*.*)|*.*|CSV files (*.csv)|*.csv|Text files (*.txt)|*.txt",
                        wx.OPEN)
    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return None, None
    else:
        path = dlg.GetPath()
        dlg.Destroy()
        page = ImportGeodata(parent, path)
        dts.ui.tabset.AddPage(page, "Import Geodata")

class UTMZoneControl(SubsetCtrl):
    def __init__(self, parent):
        SubsetCtrl.__init__(self, parent, value=1, range=(1,60))

class UTMTransformer:
    def __init__(self, zone):
        """Transforms UTM eastings and northings to latitudes and longitudes."""
        self.zone = zone
        self.utm_coordinate_system = osr.SpatialReference()
        self.utm_coordinate_system.SetWellKnownGeogCS("WGS84") # Set geographic coordinate system to handle lat/lon

        self.wgs84_coordinate_system = self.utm_coordinate_system.CloneGeogCS() # Clone ONLY the geographic coordinate system

    def to_latlon(self, easting, northing):
        if northing > 0:
            is_northern = 1
        if northing <= 0:
            is_northern = 0
        self.utm_coordinate_system.SetUTM(self.zone, is_northern)
        self.utm_to_wgs84_transform = osr.CoordinateTransformation(self.utm_coordinate_system, self.wgs84_coordinate_system)
        # returns lon, lat, altitude
        return self.utm_to_wgs84_transform.TransformPoint(easting, northing, 0)


