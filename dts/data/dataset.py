import datetime

import numpy as np
import pandas as pd


class ChannelChild(object):
    def get_channel(self):
        return self.parent.get_channel()


class Dataset(ChannelChild):
    """This class provides the general interface for interacting with ``data``, ``data_raw``, and ``subset`` objects."""

    def __init__(self, parent, hdf):
        self.parent = parent
        self.__hdf__ = hdf
        self.array = self.__hdf__
        self.attrs = self.__hdf__.attrs

    def get_title(self):
        return self.parent.get_title()

    def __set_attribute__(self, key, value):
        self.__hdf__.attrs[key] = value

    def __get_attribute__(self, key):
        return self.__hdf__.attrs[key]

    def get_array(self):
        return self.array

    def get_times_list(self):
        return self.__hdf__.attrs['times']

    def get_time(self, array_key):
        return self.__hdf__.attrs['times'][array_key]

    def set_offset(self, offset):
        self.__hdf__.attrs["dst_offset"] = offset

    def set_interval(self, interval):
        self.__hdf__.attrs["dst_interval"] = interval

    def get_offset(self):
        """Gets the offset in space from the beginning of the metermarks. Mostly for display."""
        return self.__hdf__.attrs['dst_offset']

    def get_interval(self):
        """Gets the sample interval (in meters) of the dataset."""
        return self.__hdf__.attrs['dst_interval']

    def get_xmin(self):
        """Gets the offset (in space) from the main array object of the dataset"""
        return 0

    def get_tmin(self):
        return 0

    def get_xrange(self):
        return 0, self.get_array().shape[1]

    def get_trange(self):
        return 0, self.get_array().shape[0]

    def is_subset(self):
        """Returns True if this is the same as raw data and False if it has been trimmed."""
        if not hasattr(self, "subset"):
            return True
        return self.subset

    def get_bounds(self, format="xy"):
        """Gets boundaries of the dataset relative to its parent dataset: for example, a ``Subset`` object would return
        locations relative to the  ``Data`` object, and ``Data`` would return locations with respect to ``data_raw``.
        """
        bounds = {}
        if format == "xy":
            for key in ['x_min', 'x_max', 't_min', 't_max']:
                bounds[key] = self.__get_attribute__(key)
                """except:
                    if "min" in key:
                        bounds[key] = 0
                    else:
                        bounds[key] = -1"""
        elif format == "timespace":
            for prefix, newkey in zip(["x", "t"], ["space", "time"]):
                bounds[newkey] = {}
                for lim in ["min", "max"]:
                    oldkey = prefix+"_"+lim
                    bounds[newkey][lim] = self.__get_attribute__(oldkey)
        return bounds

    def get_dist_range(self):
        """Returns range of cable lengths in real-world coordinates (i.e. the actual meter lengths, corrected for
        interval and offset).
        """
        dmin = self.get_dist(0)
        dmax = self.get_dist(self.data.shape[1])
        return dmin, dmax

    def get_dist(self, array_key):
        """Returns cable length for any given array key in this dataset"""
        interval = self.get_interval()
        offset = self.get_offset()
        return array_key*interval+offset

    def get_dist_array(self, interval=None, offset=None):
        """Returns an array of the distances represented in the Dataset"""
        x_min, x_max = self.get_xrange()
        x_indices = np.arange(x_min, x_max)

        if interval is None:
            interval = self.get_interval()
        if offset is None:
            offset = self.get_offset()

        dist_array = x_indices * interval + offset

        return dist_array

    def get_temp_range(self):
        array = self.get_array()
        return np.nanmin(array[:]), np.nanmax(array[:])

    def to_csv(self, path):
        """

        :param path:
        :return:
        """

        df = self.get_data_frame()

        df.to_csv(path)

    def stats_to_csv(self, path):
        """

        :param path:
        :return:
        """

        df = self.get_data_frame()

        max_df = df.max()
        max_df.name = 'Max'

        min_df = df.min()
        min_df.name = 'Min'

        mean_df = df.mean()
        mean_df.name = 'Mean'

        std_df = df.std()
        std_df.name = 'Std'

        stats_df = pd.concat([max_df, min_df, mean_df, std_df], axis=1).transpose()

        stats_df.to_csv(path)

    def get_distance_interval(self):
        """Gets the corrected distance interval of the subset including dataset interval and offset."""
        bounds = self.get_bounds()
        return [self.get_dist(bounds[i]) for i in ["x_min", "x_max"]]

    def get_data_frame(self):
        """

        :return:
        """

        data = self.get_array()[:]

        # get the row indices
        times_list = self.get_times_list()
        datetimes_list = [datetime.datetime.fromtimestamp(time_stamp) for time_stamp in times_list]
        datetime_index = pd.DatetimeIndex(datetimes_list)

        channel = self.get_channel()
        interpolated_points = channel.geodata.get_interpolated()
        dist_array = self.get_dist_array()

        if interpolated_points:
            column_tuples = [(cable_dist, x, y) for cable_dist, x, y in interpolated_points if cable_dist in dist_array]
            coords_type = channel.geodata.get_coords_type()
            if coords_type == 'latlon':
                names = ('cable', 'lat', 'lon')
            else:
                names = ('cable', 'east', 'north')
            columns = pd.MultiIndex.from_tuples(column_tuples, names=names)
        else:
            columns = dist_array

        df = pd.DataFrame(data=data, index=datetime_index, columns=columns)

        return df


class RawDataset(Dataset):
    """A subclass that tunes some methods of the Dataset class to be more appropriate to raw data."""
    def get_xmin(self):
        """Actually returns the x-axis minimum in *data-centric* coordinates (same as for subset and main dataset
        objects). However, since this reference data has been trimmed, this will return less than zero in this case.
        """
        if self.parent.data.is_subset():
            return -1*self.parent.data.attrs["x_min"]
        else:
            return 0

    def get_tmin(self):
        """Similar to the above; returns the t-axis minimum in *data-centric* coordinates centered on the main dataset
        object (which is a subset of this array). The returned value will be 0 or negative.
        """
        if self.parent.data.is_subset():
            return -1*self.parent.data.attrs["t_min"]
        else:
            return 0

