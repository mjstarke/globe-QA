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

# If True, tqdm will not be imported.  Instead, a fake tqdm class to wrap the iterable is created so that the rest of
# the code doesn't have to change.  desc kwargs passed to tqdm will be printed instead.
_disable_tqdm = False

if _disable_tqdm:
    class tqdm:
        def __init__(self, iterable, *args, **kwargs):
            self.iterable = iterable
            if len(args) > 0:
                print(args[0] + "...")
            elif "desc" in kwargs:
                print(kwargs["desc"] + "...")

        def __iter__(self):
            return iter(self.iterable)

fpSC_2018 = "/Users/mjstarke/Documents/GLOBE_B/GLOBE_Cloud_2018.csv"
fpSC_Dec = "/Users/mjstarke/Documents/GLOBE_B/GLOBE_cloudDec2017.csv"
fpSC = "/Users/mjstarke/Documents/GLOBE_A/sky_conditions_20170101_20190531.json"
fpLC = "/Users/mjstarke/Documents/GLOBE_A/land_covers_20181001_20190531.json"
fpMM = "/Users/mjstarke/Documents/GLOBE_A/mosquito_habitat_mapper_20170501_20190531.json"
fpTH = "/Users/mjstarke/Documents/GLOBE_A/tree_heights_20190323_20190531.json"
fpGEOS_Jan_3_hourly = "/Users/mjstarke/Documents/GLOBE_B/G5GMAO.cldtt.201801.nc4"

fpGEOS_Dec = "/Users/mjstarke/Documents/GLOBE_B/x0037.CLDTOT.201712.nc4"
fpGEOS_Jan = "/Users/mjstarke/Documents/GLOBE_B/x0037.CLDTOT.201801.nc4"
fpGEOS_Feb = "/Users/mjstarke/Documents/GLOBE_B/x0037.CLDTOT.201802.nc4"
fpGEOS_Jun = "/Users/mjstarke/Documents/GLOBE_B/x0037.CLDTOT.201806.nc4"
fpGEOS_Jul = "/Users/mjstarke/Documents/GLOBE_B/x0037.CLDTOT.201807.nc4"
fpGEOS_Aug = "/Users/mjstarke/Documents/GLOBE_B/x0037.CLDTOT.201808.nc4"

source_color = {
    "GLOBE Observer App": "purple",
    "GLOBE Data Entry Web Forms": "#40e0d0",
    "GLOBE Data Entry App": "#0055ee",
    "GLOBE Data Entry Site Definition": "#44ff44",
    "GLOBE Email Data Entry": "#ff4444",
    "GLOBE EMDE SCOOL": "#555555",
    "GLOBE Data Entry Legacy": "#ffff00",
}

std_colors = {
    "GLOBE": "purple",
    "GEOS": "orange",
    "Aqua": "#6666ff",
    "Terra": "#55ff00",
    "GOES-15": "#004400",
    "GOES-16": "#228822",
    "HIMAWARI-8": "#ff69b4",
    "METEOSAT-8": "#771111",
    "METEOSAT-10": "#cc4444",
    "METEOSAT-11": "#cc4444",
}

source_names = list(source_color.keys())

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