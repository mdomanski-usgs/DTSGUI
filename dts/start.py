import wx
import dts
from dts.data import DataFile
import dts.ui.dialog.file_io as IO
import os


class InitOption:
    def __init__(self, action, init_text, file_label):
        self.action = action
        self.init_text = init_text
        self.file_label = file_label


class Initialize:

    choices = [
        InitOption(
            "existing",
            'Open an existing DTS GUI file',
            'Choose a DTS GUI saved file'
        ),
        InitOption(
            "sensornet",
            'Sensornet: import a directory of .dtd or .ddf files',
            "Choose a directory containing .dtd or .ddf files."
        ),
        InitOption("silixa",
                   "Silixa: import a directory of .xml files",
                   "Choose a directory containing .xml files.")]

    def __init__(self, current_datafile=None):
        if current_datafile is None:
            self.initialize = True
        else:
            self.initialize = False

        sel = self.initial_choices("Choose a data set for analysis")

        wildcard = "DTS GUI file (*.dts)|*.dts"
        choice = self.choices[sel]
        # print sel

        if choice.action == 'existing':
            path = IO.choose_file(choice.file_label, wildcard)

            if path:
                self.data = DataFile(path, create=False)
            else:
                raise ValueError("No DTS file selected. Exiting.")
        else:

            folder_path = IO.choose_dir(choice.file_label)

            if not folder_path:
                raise ValueError("Import process cancelled. Exiting.")

            data_set_name = self.prompt_for_data_set_name()
            if data_set_name is None:
                raise ValueError("Import process cancelled. Exiting")

            if self.initialize:
                filename = IO.save_file(
                    "Choose a location to save the dataset.", wildcard)  # , wildcard)
                if not filename:
                    raise ValueError("Import process cancelled. Exiting.")
                if dts.DEBUG:
                    print filename
                self.data = DataFile(filename, create=self.initialize)
                try:
                    self.data.import_channel(
                        data_set_name, folder_path, file_type=choice.action)
                except:
                    self.data.close()
                    os.unlink(filename)
                    raise Exception("Import failed.")
            else:
                self.data = current_datafile
                while data_set_name in self.data.get_channels():
                    with wx.MessageDialog(self.dialog, "Data set name {} already exists".format(data_set_name),
                                          "Data set exists", style=wx.OK | wx.CENTER | wx.ICON_ERROR) as msg_dlg:
                        data_set_name = self.prompt_for_data_set_name()
                        if data_set_name is None:
                            raise ValueError(
                                "Import process cancelled. Exiting.")

                self.data.import_channel(
                    data_set_name, folder_path, file_type=choice.action)

        self.dialog.Destroy()

        # The user exited the dialog without pressing the "OK" button
    def __init_options(self, initialize):
        if initialize:
            choices = self.choices
        else:
            choices = self.choices[1:]
        return [i.init_text for i in choices]

    def prompt_for_data_set_name(self):
        # TODO: Use a more sophisticated method to get the data set name
        # dlg_style = (wx.TextEntryDialogStyle & ~(wx.CANCEL | wx.CLOSE_BOX))
        dlg_style = wx.TextEntryDialogStyle
        with wx.TextEntryDialog(self.dialog, "Enter a data set name:", caption="Data set name", style=dlg_style) \
                as text_entry_dlg:
            text_entry_dlg.CenterOnParent()
            text_entry_dlg.SetValue("Channel1")
            if text_entry_dlg.ShowModal() == wx.ID_OK:
                data_set_name = text_entry_dlg.GetValue()
            else:
                data_set_name = None

        return data_set_name

    def initial_choices(self, text):

        self.dialog = wx.SingleChoiceDialog(
            None, text, 'Choose a data set', self.__init_options(self.initialize))
        if self.dialog.ShowModal() == wx.ID_OK:
            if self.initialize:
                return self.dialog.GetSelection()
            else:
                return self.dialog.GetSelection() + 1
        else:
            raise ValueError("Nothing selected. Exiting.")
