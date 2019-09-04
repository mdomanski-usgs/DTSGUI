# DTSGUI

DTSGUI is a public-domain software tool to import, manage, parse/cull, georeference, analyze and visualize fiber-optic distributed temperature sensor (FO-DTS) data. Visualization can efficiently be accomplished in the form of “heat maps” of temperature (as color) versus distance and time, and in map view plots of georeferenced data on land-surface orthoimagery. The code is written in object-oriented Python to facilitate future extension. Data analysis is implemented using tools from the Python libraries NumPy and SciPy, and the graphical user interface (GUI) is implemented using the Python library wx. DTSGUI imports FO-DTS data in two common formats along with spatial coordinates of the FO-DTS cables, plots data and summary statistics (e.g., standard deviation, mean, minimum, maximum) in space and time, and overlays data spatially on maps retrieved from Google Maps using the Google Maps API.

## Tutorial
See [TUTORIAL.md](docs\TUTORIAL.md) for a quick start tutorial.

## Provisional software disclaimer
This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the U.S. Geological Survey (USGS). No warranty, expressed or implied, is made by the USGS or the U.S. Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the USGS nor the U.S. Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.
