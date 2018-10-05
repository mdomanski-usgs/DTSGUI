import numpy as np

import logging as log
from dataset import Dataset


class Subsets(dict):
    def __init__(self, parent):
        self.parent = parent
        self.__hdf__ = self.parent.__hdf__.require_group("subsets")
        for i in self.__hdf__.keys():
            self[i] = Subset(self, key = i)

    def create_new(self, title):
        new_subset = Subset(self, title=title)
        return new_subset

    def get_channel(self):
        return self.parent.get_channel()


class Subset(Dataset):
    """This class represents an active subset."""
    def __init__(self, parent, title=None, key=None):
        self.parent = parent
        if key is None:
            if title is None:
                raise Exception("Please specify either key or title")
            else:
                self.key = self.slugify(title)
        else:
            if title is not None:
                raise Exception("Both key and title set. Ignoring title and looking for subset '{0}'".format(key))
                title = None
            self.key = key

        import h5py
        ref_dtype = h5py.special_dtype(ref=h5py.RegionReference)
        self.__hdf__ = parent.__hdf__.require_dataset(self.key, (1,), dtype=ref_dtype, exact=True)
        self.array = self.__hdf__
        self.attrs = self.__hdf__.attrs
        parent[self.key] = self

        if title is not None:
            self.set_title(title, False)

    def get_key(self):
        return self.key

    def set_key(self, new_title):
        oldkey = self.key
        newkey = self.slugify(new_title)
        #self.parent.id.move(self.key, newkey)
        self.__hdf__.parent.id.move(self.key, newkey)
        self.parent[newkey] = self
        del(self.parent[oldkey])
        self.key = newkey

    def get_array(self):
        return self.get_data()

    def get_data(self):
        data = self.get_channel().get_array()
        B = self.get_bounds()
        return data[B['t_min']:B['t_max'],B['x_min']:B['x_max']]

    def set_title(self, title, reset_key = True):
        self.title = title
        self.__set_attribute__('title', title)
        if reset_key: self.set_key(title)

    def get_title(self):
        return self.__get_attribute__('title')

    def get_description(self):
        return self.__get_attribute__('description')

    def set_description(self, description):
        self.description = description
        self.__set_attribute__('description', description)

    def get_xrange(self):
        return (self.__get_attribute__("x_min"), self.__get_attribute__("x_max"))

    def get_trange(self):
        return (self.__get_attribute__("t_min"), self.__get_attribute__("t_max"))

    def get_offset(self):
        return self.get_channel().get_offset()+self.__get_attribute__('x_min')*self.get_interval()

    def get_interval(self):
        return self.get_channel().get_interval()

    def set_bounds(self, x_min=None, x_max=None, t_min=None, t_max=None):
        data = self.get_channel().data

        self.__hdf__[0] = data.__hdf__.regionref[t_min:t_max, x_min:x_max]

        args = [x_min, x_max, t_min, t_max]
        names = ['x_min', 'x_max', 't_min', 't_max']
        for key, item in zip(names, args):
            print key+": "+str(item)
            self.__set_attribute__(key, item)

    def get_dist(self, array_key):
        return self.get_channel().get_dist(array_key)

    def get_dist_array(self):
        data = self.get_channel().data
        super_dist_array = data.get_dist_array()
        x_min, x_max = self.get_xrange()
        return super_dist_array[x_min:x_max]

    def get_xmin(self):
        return self.attrs["x_min"]

    def get_tmin(self):
        return self.attrs["t_min"]

    def get_times_list(self):
        B = self.get_bounds()
        times = self.get_channel().get_times_list()
        return times[B['t_min']:B['t_max']]

    def get_time_range(self):
        rng = self.get_times_list()
        return rng[0], rng[-1]

    def get_time(self, array_key):
        return self.get_channel().get_time(array_key)

    def update(self, title=None, description=None, bounds=None):
        """Requires any of a title, description, and a dictionary of subset bounds."""
        if title != None: key = self.set_title(title)
        if description != None: self.set_description(description)
        if bounds != None: self.set_bounds(**bounds)

    def get_temp_minmax(self):
        data = self.get_data()
        return np.nanmin(data), np.nanmax(data)

    def slugify(self, inString):

        """This function creates a nicely underscored version of the original dataset title, making sure there are not
        already duplicates."""
        import re
        aslug = re.sub('[^\w\s-]', '', inString).strip().lower()
        aslug = re.sub('\s+', '_', aslug)

        a = 2
        while aslug in self.parent.keys():
            aslug += "_{}".format(a)
            a += 1

        return aslug

    def __del__(self):
        del(self.__hdf__)
        object.__del__(self)
        log.info("Deleted")


def create_bounds_dict(x_min=None, x_max=None, t_min=None, t_max=None):
    """Utility function to help create a properly formatted bounds dictionary object"""
    return {'x_min': x_min, 'x_max': x_max, 't_min': t_min, 't_max': t_max}