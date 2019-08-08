"""
Code common to all figure scripts.
"""


import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
from cartopy.feature.nightshade import Nightshade
import cartopy.io.shapereader as shpreader
from contextlib import closing
from datetime import date, datetime, timedelta
import json
from matplotlib.cm import get_cmap
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from operator import itemgetter
from os.path import isfile, join
from globeqa import plotters, tools
from globeqa.observation import Observation
import shapely.geometry as sgeom
from shapely.ops import unary_union
from shapely.prepared import prep
from shutil import copyfileobj
from tqdm import tqdm
from typing import Dict, Iterable, List, Optional, Tuple, Union
from urllib.request import urlopen

# If True, tqdm will be overwritten by a hollow iterator.  This effectively disables tqdm.
_disable_tqdm = False

# If _disable_tqdm is True and _print_desc is True, then the description passed to tqdm will still be printed.
_print_desc = False

if _disable_tqdm:
    class tqdm:
        def __init__(self, iterable, *args, **kwargs):
            self.iterable = iterable
            if _print_desc:
                if len(args) > 0:
                    print(args[0] + "...")
                elif "desc" in kwargs:
                    print(kwargs["desc"] + "...")

        def __iter__(self):
            return iter(self.iterable)

# Satellite matches between GLOBE observations and Aqua, Terra, and geostationary satellites.
# Available upon request:
# TODO
fpSC_2018 = "GLOBE_Cloud_2018.csv"
fpSC_Dec = "GLOBE_cloudDec2017.csv"

# Goddard Earth Observing System (GEOS) total cloud cover output.
# Available upon request:
# Nathan Arnold
# nathan.arnold@nasa.gov
fpGEOS_Dec = "x0037.CLDTOT.201712.nc4"
fpGEOS_Jan = "x0037.CLDTOT.201801.nc4"
fpGEOS_Feb = "x0037.CLDTOT.201802.nc4"
fpGEOS_Jun = "x0037.CLDTOT.201806.nc4"
fpGEOS_Jul = "x0037.CLDTOT.201807.nc4"
fpGEOS_Aug = "x0037.CLDTOT.201808.nc4"

# Set of common colors for consistency between graphs.
std_colors = {
    # Colors for comparisons between DataSources:
    "GLOBE Observer App": "purple",
    "GLOBE Data Entry Web Forms": "#40e0d0",
    "GLOBE Data Entry App": "#0055ee",
    "GLOBE Data Entry Site Definition": "#44ff44",
    "GLOBE Email Data Entry": "#ff4444",
    "GLOBE EMDE SCOOL": "#555555",
    "GLOBE Data Entry Legacy": "#ffff00",

    # Colors for comparisons between GLOBE, GEOS, and satellites:
    "GLOBE": "purple",
    "GEOS": "orange",
    "Aqua": "#6666ff",
    "Terra": "#55ff00",
    "AquaTerra": "#66aa88",
    "GOES-15": "#004400",
    "GOES-16": "#228822",
    "HIMAWARI-8": "#ff69b4",
    "METEOSAT-8": "#771111",
    "METEOSAT-10": "#cc4444",
    "METEOSAT-11": "#cc4444",
}

# Converts a GLOBE cloud cover category to a real number (the midpoint of the category's range).
category_to_midpoint = dict(
    none=0.00,
    clear=0.05,
    few=0.05,
    isolated=0.175,
    scattered=0.375,
    broken=0.70,
    overcast=0.95,
    obscured=0.95
)