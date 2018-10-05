import numpy as np


class Geodata(object):
    def __init__(self, channel):
        self.parent = channel
        self.ch = channel.__hdf__
        if 'geo_raw' not in list(self.ch):
            self.loaded = False
            self.raw = False
            self.interp = False
        else:
            self.raw = self.ch['geo_raw']
            if 'geo_interp' not in list(self.ch):
                self.interpolate()
            else:
                self.interp = self.ch['geo_interp']
            self.loaded = True

    geo_dtype = np.dtype([('pos', 'f'), ('north', 'f'), ('east', 'f')])

    def get_raw(self):
        return self.raw

    def get_center(self):
        """Averages the latitude and longitudes of control points to find a central point for creating a map."""
        return (self.raw['north'].mean(), self.raw['east'].mean())

    def get_interpolated(self, interval=None, offset=None):
        if interval is None and offset is None:
            return self.interp
        else:
            return self.interpolate(interval=interval, offset=offset)

    def set_coords(self, geodata, type='latlon'):

        if 'geo_raw' in list(self.ch):
            del self.ch['geo_raw']

        geo_raw = np.core.records.fromarrays(geodata, names='pos, north, east')
        self.raw = self.ch.create_dataset('geo_raw', data=geo_raw)
        if type is 'eastingnorthing':
            self.raw.attrs['type'] = 'eastingnorthing'
        else:
            self.raw.attrs['type'] = 'latlon'

        self.interpolate()

        self.loaded = True

    def get_coords_type(self):
        """

        :return:
        """

        return self.raw.attrs['type']

    def interpolate(self, interval=None, offset=None):
        """Interpolating without setting the offset will use the default dataset value"""

        update = False
        if interval is None and offset is None:
            update = True

        data = self.parent.get_array()
        # max_length = data.shape[1]

        if offset is None:
            offset = data.attrs['dst_offset']
            # offset = self.parent.data.get_offset()
        if interval is None:
            interval = data.attrs['dst_interval']
            # interval = self.parent.data.get_interval()
        print "Interpolating..."

        interp_lengths = self.parent.data.get_dist_array(interval, offset)

        c1 = np.interp(interp_lengths, self.raw['pos'], self.raw['north'], left=-200, right=-200)
        c2 = np.interp(interp_lengths, self.raw['pos'], self.raw['east'], left=-200, right=-200)
        data = np.vstack((interp_lengths, c1, c2))
        geo_interp = np.core.records.fromarrays(data, names='pos, north, east')
        if update:
            if 'geo_interp' in list(self.parent.__hdf__):
                del self.parent.__hdf__['geo_interp']
            self.interp = self.parent.__hdf__.create_dataset('geo_interp', data=geo_interp)
        else:
            return geo_interp
