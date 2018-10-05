import h5py
from dts.data.channel import Channel
from dts.data.dataset import RawDataset, Dataset
from sensornet import SensornetImporter
from salixa import SalixaImporter
import logging as log


def import_data(dataset, name, folder, file_type="sensornet"):
    channel = Channel(dataset, name)

    if file_type == "sensornet":
        importer = SensornetImporter(folder)
    elif file_type == "salixa":
        importer = SalixaImporter(folder)
    else:
        raise NotImplementedError("Valid importer not available.")

    shape = importer.get_shape()
    data_raw = channel.__hdf__.create_dataset('data_raw', shape)
    log.debug("Dataset shape is ({0}, {1})".format(*shape))

    # Initially, we set the 'data' attribute to mirror the raw data.
    # This will be changed if the data is trimmed.
    channel.__hdf__['data'] = h5py.SoftLink(channel.__hdf__.name+'/data_raw')

    # Create dataset to hold subsets.
    # ref_dtype = h5py.special_dtype(ref=h5py.Reference)
    # subsets	= __hdf__.create_dataset("subsets", (100,), dtype=ref_dtype)

    data_raw.attrs['subset'] = False
    data_raw.attrs['x_min'] = 0
    data_raw.attrs["x_max"] = shape[1]-1
    data_raw.attrs['t_min'] = 0
    data_raw.attrs["t_max"] = shape[0]-1

    times = [0]*shape[0]
    log.debug("{0} files to be imported".format(len(importer.files)))
    for i, item in enumerate(importer.files):
        temps, time = importer.load_file(item)
        print time
        channel.__hdf__['data_raw'][i] = temps
        times[i] = time

    data_raw.attrs['times'] = times
    log.debug("Successfully imported files.")

    interval = importer.get_interval()

    log.debug("Data interval is {0:.4}".format(interval))

    channel.data_raw = RawDataset(channel, channel.__hdf__['data_raw'])
    channel.data = Dataset(channel, channel.__hdf__['data'])

    channel.set_interval_offset(interval, 0.0)

    log.debug("Done with channel creation.")

    return channel