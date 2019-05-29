import h5py as hdf
import io
from dts.data.channel import Channel
import logging as log


class DataFile:
    """The main class defining the interface for interacting with the HDF5
    data file.

    Parameters
    ----------
    file_path : str
        Path to HDF file
    create : bool, optional
        Open (False) or create (True) HDF file (the default is False).

    """

    def __init__(self, file_path, create=False):
        if create:
            self.__create_file(file_path)
        else:
            self.__open_file(file_path)

        attrs = self.__hdf__.attrs
        if 'name' not in attrs:
            attrs['name'] = 'Default'
        self.name = attrs['name']

    def __del__(self):
        self.close()

    def __create_file(self, filename=None, name='Default'):
        if filename is None:
            from tempfile import mkstemp
            filename = mkstemp()[1]

        # Fails when file exists. Need to implement something to handle overwriting files...,
        # or create some sort of error condition
        try:
            self.__hdf__ = hdf.File(
                filename, 'w', driver='core', backing_store=True)
        except IOError:
            log.error(
                "HDF dataset cannot be created because file already exists.")
        self.loaded = False
        self.__hdf__.attrs['name'] = name
        self.channels = dict()

    def __open_file(self, filename):

        self.__hdf__ = hdf.File(filename)
        self.loaded = False

        self.channels = dict()
        ids = self.get_channels()
        for id in ids:
            self.add_channel(id)
        self.set_working_channel()

    def add_channel(self, id):
        """Adds a new channel to this instance

        Parameters
        ----------
        id : str
            Channel ID

        Returns
        -------
        :class:`dta.data.channel.Channel`

        """
        channel = Channel(self, id)
        self.channels[id] = channel

        self.loaded = True
        self.set_working_channel(id)
        return channel

    def import_channel(self, name, folder, file_type="sensornet"):
        """Imports channel data from sensor files

        Parameters
        ----------
        name : str
            New channel ID
        folder : str
            Path to directory containing sensor data
        file_type : {'sensornet', 'silixa'}, optional
            Type of sensor file to import (the default is 'sensornet').

        Returns
        -------
        :class:`dta.data.channel.Channel`

        See Also
        --------
        :func:`dts.data.io.import_data`

        """
        try:
            channel = io.import_data(self, name, folder, file_type)
        except Exception, err:
            log.error(str(err))
            raise Exception("Import failed.")

        self.channels[name] = channel

        self.loaded = True
        self.set_working_channel(name)
        self.save()
        return channel

    def get_channels(self):
        """Returns a list of the available data channels"""

        return self.__hdf__.keys()

    def set_working_channel(self, id=None, num=None):
        """Sets the working channel of this instance

        Parameters
        ----------
        id : str, optional
            New working channel ID (the default is None, which requires the
            channel to be specified by `num`)
        num : int
            Index of new working channel ID (the default is None). If `id` is
            set, `num` is ignored.

        """
        if id is None:
            if num != None:
                id = self.channels.keys()[num]
            else:
                try:
                    id = self.channels.keys()[0]
                except:
                    raise Exception(
                        "No available data channels found. Please try another file.")
        try:
            self.working_channel = self.channels[id]
        except:
            log.error('Invalid channel name')
            raise AttributeError("The requested channel does not exist.")
            self.working_channel = False
        self.ch = self.working_channel
        return self.working_channel

    def get_working_channel(self):
        """Returns the current working channel"""
        return self.working_channel

    def get_current_channel(self):
        """Returns the current working channel"""
        return self.working_channel

    def is_temporary(self):
        """Returns true if the filename is does not have a .dts extension)"""
        import os
        basename, extension = os.path.splitext(self.__hdf__.filename)
        if extension is not '.dts':
            return True
        else:
            return False

    def change_filename(self, new_file_name):
        """Changes the data file name

        Parmeters
        ---------
        new_file_name : str

        """
        if self.is_temporary():
            import os
            os.unlink(self.__hdf__.filename)
        self.__hdf__.filename = new_file_name
        self.save()

    def save(self):
        """Save the data file."""
        log.info("Saving data file.")
        self.__hdf__.flush()

    def combine_channels(self, reverse=True):
        """Not yet implemented."""
        raise NotImplementedError

    def close(self):
        """Closes the HDF file referenced by this instance"""
        self.__hdf__.close()
