import cartopy.io.shapereader as shpreader
from contextlib import closing
from datetime import date, datetime, timedelta
import json
from netCDF4 import Dataset
from globeqa.observation import Observation
from os.path import isfile
from shapely.ops import unary_union
from shapely.prepared import prep
from shutil import copyfileobj
from tqdm import tqdm
from typing import List, Dict, Optional, Union, Tuple
from urllib.request import urlopen


def parse_csv(fp: str, count: int = 1e30, protocol: Optional[str] = "sky_conditions") -> List[Observation]:
    """
    Parse a CSV file containing GLOBE observations.
    :param fp: The path to the CSV file.
    :param count: The maximum number of observations to parse.  Default 1e30.
    :param protocol: The protocol that the CSV file comes from.  Default 'sky_conditions'.
    :return: The observations.
    """

    # Prepare to collect observations.
    observations = []
    with open(fp, "r") as f:
        # Set aside the header, split it, and strip each piece.
        header = f.readline().split(',')
        header = [h.strip() for h in header]
        # Determine number of lines for tqdm.
        line_count = sum(1 for i in open(fp, 'rb'))
        print("--  Reading CSV file...")
        # Loop through each line.
        for line in tqdm(f, total=line_count):
            # Split the line and create an Observation for it.
            s = line.split(',')
            observations.append(Observation(header, s, protocol=protocol))
            # If limited by count, check here.
            if len(observations) >= count:
                break

    return observations


def download_from_api(protocols: List[str], start: date, end: Optional[date] = None,
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

    # Create a string that represents the protcol part of the query.
    protocol_string = "".join(["protocols={}&".format(protocol) for protocol in protocols])
    # Create the full download link.
    download_src = "https://api.globe.gov/search/v1/measurement/protocol/measureddate/?{}startdate={}&enddate={" \
                   "}&geojson=TRUE&sample=FALSE "
    download_src = download_src.format(protocol_string, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    # Replace % indicators in the destination string with their respective variable values.
    download_dest = download_dest.replace("%P", "__".join(protocols))
    download_dest = download_dest.replace("%S", start.strftime("%Y%m%d"))
    download_dest = download_dest.replace("%E", end.strftime("%Y%m%d"))

    # Check if file already exists at the destination.  If a file by the target name already exists, skip download.
    if check_existing:
        if isfile(download_dest):
            print("--  Download will not be attempted as the file already exists locally.")
            return download_dest

    # Try to download from the API.
    try:
        print("--  Downloading from API...")
        print("--  {}".format(download_src))
        # Open the target URL, open the local file, and copy.
        with closing(urlopen(download_src)) as r:
            with open(download_dest, 'wb') as f:
                copyfileobj(r, f)
        print("--  Download successful.  Saved to:")
        print("--  {}".format(download_dest))
    # In the event of a failure, print the error.
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
    print("--  Reading JSON from {}...".format(fp))
    with open(fp, "r") as f:
        g = f.read()
        print("--  Interpreting file as JSON...")
        raw = json.loads(g)

    print("--  Parsing JSON as observations...")
    ret = []
    for o in tqdm(range(len(raw["features"]))):
        ob = raw["features"][o]
        ret.append(Observation(feature=ob))
    return ret
    # return [Observation(feature=ob) for ob in raw["features"]]


def print_flag_summary(obs: List[Observation]) -> Dict[str, int]:
    """
    Pretty-prints a summary of all flags for the observations.
    :param obs: The observations to analyze.
    :return: The dictionary of (flag, count) pairs for each flag found at least once.
    """
    flag_counts = dict(total=len(obs))
    print("--  Enumerating flags...")
    for ob in obs:
        for flag in ob.flags:
            try:
                flag_counts[flag] += 1
            except KeyError:
                flag_counts[flag] = 1

    print("--  Flag counts are as follows:")
    for k in sorted(flag_counts.keys()):
        v = flag_counts[k]
        print("{:5}  {:>6}  {:7.2%}".format(k, v, v / len(obs)))

    return flag_counts


def filter_by_flag(obs: List[Observation], specs: Union[bool, Dict[str, bool]] = True) -> List[Observation]:
    """
    Filters a list of observations by whether it has particular flags.
    :param obs: The observations to filter.
    :param specs: The flag specifications that an observation must meet to be included in the return.  This can be a
    dictionary of str-bool pairs, which indicates which flags must be present or absent for an observation to pass.
    For instance, {"DX"=True, "ER"=False} means that the observation must have the DX flag and must not have the ER
    flag.  Alternatively, specs can be True, meaning that at least one flag must be present, or False, meaning that all
    flags must be absent.  Default True.
    :return: The filtered observations.
    """
    if type(specs) == dict:
        ret = []
        for ob in tqdm(obs):
            for k, v in specs.items():
                if ob.has_flag(k) == v:
                    ret.append(ob)
        return ret
    elif type(specs) == bool:
        return [ob for ob in obs if ob.flagged == specs]
    else:
        raise TypeError("Argument 'specs' must be either Dict[str, bool] or bool.")


def get_cdf_datetime(cdf: Dataset, index: int) -> datetime:
    """
    Creates a datetime that represents the time at the given index of cdf["time"].
    :param cdf: The CDF Dataset.
    :param index: The time index to process.
    :return: The actual datetime that corresponds to the given index.
    """
    # Get the begin date and begin time from the CDF.  Put them together and convert to a datetime.
    begin_datetime_string = "{}{:0>6}".format(cdf["time"].begin_date, cdf["time"].begin_time)
    begin_datetime = datetime.strptime(begin_datetime_string, "%Y%m%d%H%M%S")

    # Get the value of time at the given index.  This is minutes since the begin time.  It must be converted to int from
    # maskedarray.
    minutes = int(cdf["time"][index])

    # Add to the beginning datetime to get the given datetime.
    return begin_datetime + timedelta(minutes=minutes)


def find_closest_gridbox(cdf: Dataset, t: datetime, lat: float, lon: float) -> Tuple[int, int, int]:
    """
    Find the indices of the closest gridbox to a given point.

    :param cdf: A NetCDF4 dataset.
    :param t: The datetime of the point.
    :param lat: The signed latitude of the point in degrees.
    :param lon: The signed longitude of the point in degrees.

    :return: The indices for time, latitude, and longitude, respectively, of the gridbox that most closely
    approximates the point.
    """

    # Find first latitude and the step between indices.
    first_lat = cdf["lat"][0]
    lat_step = cdf["lat"][1] - first_lat
    # Find the difference between the point latitude and the first latitude.  Divide this by the step size to
    # determine which index to use.
    lat_diff = lat - first_lat
    lat_index = round(lat_diff / lat_step)

    # As above.
    first_lon = cdf["lon"][0]
    lon_step = cdf["lon"][1] - first_lon
    lon_diff = lon - first_lon
    lon_index = round(lon_diff / lon_step)

    # Compose the string that represents the first datetime, then convert it to a datetime.
    begin_datetime_string = "{}{:0>6}".format(cdf["time"].begin_date, cdf["time"].begin_time)
    begin_datetime = datetime.strptime(begin_datetime_string, "%Y%m%d%H%M%S")
    # Determine the step between indices.
    time_step = cdf["time"][1]
    # Find the difference between the point time and a first time.  Convert this from a datetime to an integer
    # number of minutes.
    time_diff = t - begin_datetime
    time_diff_minutes = time_diff / timedelta(seconds=60)
    # Divide by the step size to determine which index to use.
    time_index = round(time_diff_minutes / time_step)

    return int(time_index), int(lat_index), int(lon_index)


def prepare_earth_geometry(geometry_resolution: str = "50m"):
    """
    Preparations necessary for determining whether a point is over land or water.
    This code may need to download a ZIP containing Earth geometry data the first time it runs.
    Code borrowed from   https://stackoverflow.com/a/48062502
    :param geometry_resolution: The resolution of the NaturalEarth shapereader to use.  Valid values are '10m', '50m'
    or '110m'.
    :return: The PreparedGeometry object that can be used for point-land checking.
    """
    print("--  Preparing Earth geometry...")
    land_shp_fname = shpreader.natural_earth(resolution=geometry_resolution, category='physical', name='land')
    land_geom = unary_union(list(shpreader.Reader(land_shp_fname).geometries()))
    land = prep(land_geom)
    print("--  Earth geometry prepared.")
    return land


def do_quality_check(obs: List[Observation], land=None):
    """
    Perform quality checks on the obsevations.
    :param obs: The observations.
    :param land: The PreparedGeometry for land checking.  If None, land check will not be performed.
    """
    print("--  Performing quality check...")
    for o in tqdm(range(len(obs))):
        ob = obs[o]
        ob.check_for_flags(land)


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

    print("--  Searching observations...")
    for ob in tqdm(obs):
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


def list_all_properties(observations: List[dict]) -> List[str]:
    """
    Generates a sorted list of all properties that occur at least once in the observations.
    :param observations: The observations.
    :return: A sorted list of all properties that occur at least once in the observations.
    """
    all_keys = []
    print("--  Searching observations...")
    for ob in tqdm(observations):
        for key in ob["properties"]:
            if key not in all_keys:
                all_keys.append(key)

    return sorted(all_keys)


# def do_daily(interpret_flags: bool = False) -> None:
#     """
#     Downloads, parses, and quality-checks yesterday's observations.
#     :param interpret_flags: Whether to interpret the quality flags and convert them to English.
#     :return: A list of all observation indices that were flagged by the quality checker.
#     """
#     # Download yesterday's GLOBE observations.
#     fp = download_from_api(["sky_conditions", "land_covers", "mosquito_habitat_mapper", "tree_heights"],
#                            date.today() - timedelta(1), download_dest="SC_LC_MHM_TH__%S.json")
#
#     # Open and parse that file.
#     observations = parse_json(fp)
