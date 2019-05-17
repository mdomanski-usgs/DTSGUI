import abc
import os


class Importer:
    """Importer base class

    Do not instantiate. Only to be subclassed.

    """

    # must be implemented by subclass
    type_map = None

    def __init__(self, folder):

        dirlist = os.listdir(folder)

        # this generates a list of files in the directory which will be imported.
        last_ext = None
        self.files = []
        for item in dirlist:
            ext = os.path.splitext(item)[-1][1:]
            if ext in self.type_map:
                if last_ext is None:
                    last_ext = ext
                if ext == last_ext:
                    self.files.append(os.path.join(folder, item))
                    last_ext = ext
                else:
                    raise Exception(
                        "Mixing of .ddf and .dtd extensions is not allowed")
            self.file_type = last_ext
        self.folder = folder

    @abc.abstractmethod
    def get_interval(self):
        """Not implemented (see subclasses)"""
        raise NotImplementedError

    def get_shape(self):
        n_files = len(self.files)
        n_records = self.load_file(self.files[0])[0].shape[0]
        return n_files, n_records

    @abc.abstractmethod
    def load_file(self, filename):
        """Not implemented (see subclasses)"""
        raise NotImplementedError
