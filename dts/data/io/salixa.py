from time import strptime, mktime
import xml.etree.ElementTree as et

import numpy as np

from base import Importer
import logging


class SalixaImporter(Importer):

    type_map = ["xml"]

    xml_namespace = {'default': 'http://www.witsml.org/schemas/1series'}

    def _find_in_log(self, xml_file, xml_element):
        """

        :return:
        """

        # parse the xml and find the log
        tree = et.parse(xml_file)
        root = tree.getroot()
        log = root.find('default:log', self.xml_namespace)

        return log.find('default:' + xml_element, self.xml_namespace)

    def _read_time(self, xml_file):
        """

        :param xml_file:
        :return:
        """

        start_date_time_index = self._find_in_log(xml_file, 'startDateTimeIndex').text

        time_format = "%Y-%m-%dT%H:%M:%S"
        date = strptime(start_date_time_index[:-5], time_format)

        return mktime(date)

    def get_interval(self):
        """

        :return:
        """

        step_increment = self._find_in_log(self.files[0], 'stepIncrement')

        interval = float(step_increment.text)
        logging.info("Interval - {0:.4f}".format(interval))
        return interval

    def load_file(self, filename):
        """

        :param filename:
        :return:
        """

        return self.load_xml(filename)

    def load_xml(self, filename):
        """

        :param filename:
        :return:
        """

        time = self._read_time(filename)

        log_data = self._find_in_log(filename, 'logData')
        mnemonic_list_str = log_data.find('default:mnemonicList', self.xml_namespace).text
        mnemonic_list = mnemonic_list_str.split(',')
        temperature_index = mnemonic_list.index('TMP')

        temperatures = []

        for data in log_data.findall('default:data', self.xml_namespace):
            temp = float(data.text.strip().split(',')[temperature_index])
            temperatures.append(temp)

        temperatures = np.array(temperatures, dtype=np.float32)

        return temperatures, time
