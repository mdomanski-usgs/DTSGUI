import datetime

import dts
from dataset import Dataset, RawDataset
import logging as log


class Channel(object):
    def __init__(self, parent, name):
        self.file = parent.__hdf__
        self.parent = parent
        self.name = name
        if name in parent.__hdf__.keys():
            self.__hdf__ = parent.__hdf__[name]
            self.loaded = True
            self.data_raw = RawDataset(self, self.__hdf__['data_raw'])
            self.data = Dataset(self, self.__hdf__['data'])
        else: # if the channel is not yet created.
            self.__hdf__ = self.parent.__hdf__.create_group(name)
            self.loaded = False

        import geodata
        self.geodata = geodata.Geodata(self)

        # Set up subsets
        from subsets import Subsets
        self.subsets = Subsets(self)

        self.key = self.name

    def get_channel(self):
        return self

    def get_title(self):
        return self.name

    def get_key(self):
        return self.key

    def get_data(self):
        return self.data

    def get_array(self):
        return self.data.get_array()

    def get_subsets(self):
        return self.subsets

    def wrap_data(wrap_point = 0, autotrim=True):
        """Creates a dataset from raw data that is symmetrical around a certain point on the cable (e.g. for a loopback
         or double fiber cable)
         """
        pass

    def merge_channels(self):
        pass

    def revert_to_raw(self):
        import h5py as hdf

        # Generate changeset to apply to subsets later
        changeset = {}
        for name in ["x_min", "x_max", "t_min", "t_max"]:
            changeset[name] = self.data.attrs[name]

        del self.__hdf__['data']

        self.__hdf__.create_dataset('data',(1,1))
        del self.__hdf__["data"]

        self.__hdf__['data'] = hdf.SoftLink(self.__hdf__.name+'/data_raw')

        self.data = Dataset(self, self.__hdf__["data"])

        # After new dataset is created, generate new subsets from changeset.
        log.info("Updating subsets.")
        for name, subset in self.subsets.items():
            extents = subset.get_bounds()
            for key, item in extents.items():
                item = item + changeset[key]
                if item < 0: item = 0
            subset.set_bounds(**extents)

        log.info("Reverted to raw data.")

    def trim_raw(self, x_min=None, x_max=None, t_min=None, t_max=None):
        '''Trims raw data non-destructively; can be reverted later'''
        data_raw = self.__hdf__['data_raw']

        if x_min is None: x_min = 0
        if x_max is None: x_max = data_raw.shape[1]-1
        if t_min is None: t_min = 0
        if t_max is None: t_max = data_raw.shape[0]-1

        # Generate changeset to apply to subsets later
        extents = self.data.get_bounds()
        changeset = {}
        for name in ["x_min", "x_max", "t_min", "t_max"]:
            changeset[name] = locals()[name] - extents[name]

        print changeset

        # After new dataset is created, generate new subsets from changeset.
        log.info("Updating subsets.")
        for name, subset in self.subsets.items():
            extents = subset.get_bounds()
            for key, item in extents.items():
                item = item + changeset[key]
                if item < 0: item = 0
            subset.set_bounds(**extents)

        # Overwrite old data with new.
        del self.__hdf__['data'] #must delete old copy of dataset before creating a new one.
        data = self.__hdf__.create_dataset('data', data=data_raw[t_min:t_max, x_min:x_max])
        data.attrs['subset'] = True
        data.attrs['times'] = data_raw.attrs['times'][t_min:t_max]

        data.attrs["x_min"] = x_min
        data.attrs["x_max"] = x_max
        data.attrs["t_min"] = t_min
        data.attrs["t_max"] = t_max

        self.data = Dataset(self, self.__hdf__["data"])
        self.set_interval_offset(
            interval = self.data_raw.get_interval(),
            offset = self.data_raw.get_offset()+x_min*self.data_raw.get_interval()
        )

    def get_times_list(self):
        return self.data.attrs['times']

    def get_time(self, array_key):
        return self.data.attrs['times'][array_key]

    def get_offset(self):
        return self.data.attrs['dst_offset']

    def get_interval(self):
        return self.data.attrs['dst_interval']

    def get_dist(self, array_key):
        interval = self.get_interval()
        offset = self.get_offset()
        return array_key*interval+offset

    def get_dist_range(self):
        return self.data.get_dist_range()

    def get_time_range(self):
        """Returns the min and max times for the dataset"""
        tlist = self.data.attrs['times']
        return tlist[0], tlist[-1]

    def get_temp_range(self):
        return self.data.get_temp_range()

    def get_temp_minmax(self):
        """DEPRECATED"""
        return self.data.get_temp_range()

    def set_interval_offset(self, interval=None, offset=None):
        '''sets the interval and offset from cable length measurements to natural x-axis indices'''

        data = self.data
        data_raw = self.data_raw

        x_min = data.get_bounds()["x_min"]

        if interval is not None:
            data.set_interval(interval)
            data_raw.set_interval(interval)
            self.__hdf__.attrs['cable_interval'] = interval

        if offset is not None:
            data.set_offset(offset)
            raw_offset = offset-x_min*data.get_interval()
            data_raw.set_offset(raw_offset)
            self.__hdf__.attrs['cable_offset'] = raw_offset

        if self.geodata.loaded:
            self.geodata.interpolate()

    def set_interval_offset_old(self, interval=None, offset=None):
        '''sets the interval and offset from cable length measurements to natural x-axis indices'''
        if offset == None:
            offset = self.__hdf__.attrs['cable_offset']
        else:
            self.__hdf__.attrs['cable_offset'] = offset
            self.__hdf__['data_raw'].attrs['dst_offset'] = offset

        if interval == None:
            interval = self.__hdf__.attrs['cable_interval']
        else:
            self.__hdf__.attrs['cable_interval'] = interval
            self.__hdf__['data_raw'].attrs['dst_interval'] = interval

        data = self.__hdf__['data']
        if data.attrs['subset']:
            x_min = data.attrs['x_min']
            data.attrs['dst_offset'] = offset+x_min*interval
            data.attrs['dst_interval'] = interval

        if self.geodata.loaded:
            self.geodata.interpolate()

