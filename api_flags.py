import cartopy.io.shapereader as shpreader
from contextlib import closing
from datetime import date, datetime, timedelta
import json
from os.path import isfile
import pprint
import shapely.geometry as sgeom
from shapely.ops import unary_union
from shapely.prepared import prep
from shutil import copyfileobj
from typing import List, Optional, Union, Tuple, Dict
from urllib.request import urlopen
from observation import Observation


# Settings

# The Earth geometry resolution to use, specified as a ratio in millions.
# Valid values are '10m', '50m', and '110m'.  Default is 50m.
# See NaturalEarthData.com for details.
geometry_resolution = ["10m", "50m", "110m"][1]


def download_from_API(protocols: List[str], start: date, end: Optional[date] = None,
                      download_dest: str = "%P_%S_%E.json", check_existing: bool = True) -> str:
    """
    Downloads from the GLOBE API.
    :param protocols: The protocols to download.
    :param start: The beginning of the range to download.
    :param end: The end of the range to download.  If None, will be set equal to the start date,
    capturing one day of output.  Default None.
    :param download_dest: Where to save the downloaded file.  %P will be replaced with protocol name(s),
    %S with the start date, and %E with the end date.  Default "%P_%S_%E.json".
    :param check_existing: Whether to check if the file exists locally (at download_dest) before
    downloading.  download_dest will be interpreted according to the rules listed above before checking.
    Default True.
    :returns: The path to the downloaded file, including the file name.
    """
    if end is None:
        end = start

    protocol_string = "".join(["protocols={}&".format(protocol) for protocol in protocols])
    download_src = "https://api.globe.gov/search/v1/measurement/protocol/measureddate/?{}startdate={}&enddate={" \
                   "}&geojson=TRUE&sample=FALSE "
    download_src = download_src.format(protocol_string, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    download_dest = download_dest.replace("%P", "__".join(protocols))
    download_dest = download_dest.replace("%S", start.strftime("%Y%m%d"))
    download_dest = download_dest.replace("%E", end.strftime("%Y%m%d"))

    if check_existing:
        if isfile(download_dest):
            print("--- Download will not be attempted as the file already exists locally.")
            return download_dest

    try:
        print("--- Downloading from API...")
        print("--- {}".format(download_src))
        with closing(urlopen(download_src)) as r:
            with open(download_dest, 'wb') as f:
                copyfileobj(r, f)
        print("--- Download successful.  Saved to:")
        print("--- {}".format(download_dest))
    except Exception as e:
        print("(x) Download failed:")
        print(e)

    return download_dest


def parse_json(fp: str) -> List[Observation]:
    """
    Parses a JSON file and returns its features converted to observations.
    :param fp: The path to the JSON file.
    :returns: The features of the JSON.
    """
    print("--- Reading JSON from {}...".format(fp))
    with open(fp, "r") as f:
        raw = json.loads(f.read())

    print("--- Parsing JSON as observations...")
    return [Observation(feature=ob) for ob in raw["features"]]


def prepare_earth_geometry():
    # Preparations necessary for determining whether a point is over land or water.
    # This code may need to download a ZIP containing Earth geometry data the first time it runs.
    # Code borrowed from   https://stackoverflow.com/a/48062502
    print("--- Preparing Earth geometry...")
    land_shp_fname = shpreader.natural_earth(resolution=geometry_resolution, category='physical', name='land')
    land_geom = unary_union(list(shpreader.Reader(land_shp_fname).geometries()))
    land = prep(land_geom)
    print("--- Earth geometry prepared.")
    return land


def do_quality_check(obs: List[Observation], land, progress_interval: int = 10000):
    print("--- Performing quality check...")
    for o in range(len(obs)):
        ob = obs[o]
        ob.check_for_flags(land)
        if o % progress_interval == 0:
            print("--- {:7.2%}   Checked {} observations...".format(o / len(obs), o))


# /Users/mjstarke/Documents/GLOBE Task A/sky_conditions_20170101_20190531.json
def test(fp: str, maximum: int = None, ret: bool = False):
    obs = parse_json(fp)
    if maximum is not None:
        obs = obs[:maximum]
    land = prepare_earth_geometry()
    do_quality_check(obs, land)
    flag_counts = dict(total=len(obs))
    print("--- Enumerating flags...")
    for ob in obs:
        for flag in ob.flags:
            try:
                flag_counts[flag] += 1
            except KeyError:
                flag_counts[flag] = 1

    print("--- Flag counts are as follows:")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(flag_counts)
    return obs if ret else None


def print_all_values(obs: List[Observation], key: str) -> None:
    """
    Prints all values that are paired with a given key at least once in the observations.
    :param obs: The observations.
    :param key: The key to evaluate.
    :return: None.  Prints results directly.
    """
    found_values = []
    found_obs = []
    unique_values = []
    unique_counts = []

    for ob in obs:
        if key in ob:
            value = ob[key]
            found_obs.append(ob)
            found_values.append(value)
            if value not in unique_values:
                unique_values.append(value)
                unique_counts.append(1)
            else:
                i = unique_values.index(value)
                unique_counts[i] += 1

    print("{} of {} observations had the key '{}'.".format(len(found_values), len(obs), key))
    print("Unique values for the key follow:")
    for i in range(len(unique_values)):
        print("{:6} occurrences:   {}".format(unique_counts[i], unique_values[i]))
