import cartopy.io.shapereader as shpreader
from datetime import datetime, time, timezone, timedelta
from netCDF4 import Dataset
from globeqa.observation import Observation
from pprint import PrettyPrinter
from shapely.ops import unary_union
from shapely.prepared import prep
from typing import List, Dict, Optional, Union, Tuple


def pp(obj):
    PrettyPrinter(indent=4).pprint(obj)


def calc_local_midnight_utc_offset(lon: float):
    return timedelta(hours=lon / 15.)


def print_flag_summary(obs: List[Observation]) -> None:
    """
    Pretty-prints a summary of all flags for the observations.
    :param obs: The observations to analyze.
    """
    flag_counts = dict(total=len(obs))
    print("--- Enumerating flags...")
    for ob in obs:
        for flag in ob.flags:
            try:
                flag_counts[flag] += 1
            except KeyError:
                flag_counts[flag] = 1

    print("--- Flag counts are as follows:")
    for k in sorted(flag_counts.keys()):
        v = flag_counts[k]
        print("{:5}  {:>6}  {:7.2%}".format(k, v, v / len(obs)))


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
        for ob in obs:
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
    Find the indicies of the closest gridbox to a given point.

    :param cdf: A NetCDF4 dataset.
    :param t: The datetime of the point.
    :param lat: The signed latitude of the point in degrees.
    :param lon: The signed longitude of the point in degrees.

    :return: The indices for time, latitude, and longitude, respectively, of the gridbox that most closely
    approximates the point.
    """

    # Find first latitude and the step between indicies.
    first_lat = cdf["lat"][0]
    lat_step = cdf["lat"][1] - first_lat
    # Find the difference between the point latitude and the first latitude.  Divide this by the step size to
    # determine which index to use.
    lat_diff = lat - first_lat
    lat_index = round(lat_diff / lat_step)
    lat_size = cdf["lat"].shape[0]

    # As above.
    first_lon = cdf["lon"][0]
    lon_step = cdf["lon"][1] - first_lon
    lon_diff = lon - first_lon
    lon_index = round(lon_diff / lon_step)
    lon_size = cdf["lon"].shape[0]

    # Compose the string that represents the first datetime, then convert it to a datetime.
    begin_datetime_string = "{}{:0>6}".format(cdf["time"].begin_date, cdf["time"].begin_time)
    begin_datetime = datetime.strptime(begin_datetime_string, "%Y%m%d%H%M%S")
    # Deterime the step between indicies.
    time_step = cdf["time"][1]
    # Find the difference between the point time and a first time.  Conver this from a datetime to an integer
    # number of minutes.
    time_diff = t - begin_datetime
    time_diff_minutes = time_diff / timedelta(seconds=60)
    # Divide by the step size to determine which index to use.
    time_index = round(time_diff_minutes / time_step)
    time_size = cdf["time"].shape[0]

    return int(time_index), int(lat_index), int(lon_index)


def prepare_earth_geometry(geometry_resolution: str):
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


def list_all_properties(observations: List[dict]) -> List[str]:
    """
    Generates a sorted list of all properties that occur at least once in the observations.
    :param observations: The observations.
    :return: A sorted list of all properties that occur at least once in the observations.
    """
    all_keys = []
    for ob in observations:
        for key in ob["properties"]:
            if key not in all_keys:
                all_keys.append(key)

    return sorted(all_keys)


def count_flags(obs: List[dict]) -> Dict[str, int]:
    """
    Finds and counts flags in the observations.
    :param obs: The observations.
    :return: A dictionary of (flag, count) pairs.
    """
    flag_counts = dict()

    for ob in obs:
        flags = ob["flags"].split()
        for flag in flags:
            try:
                flag_counts[flag] += 1
            except KeyError:
                flag_counts[flag] = 1

    return flag_counts


def do_daily(interpret_flags: bool = False) ->  List[int]:
    """
    Downloads, parses, and quality-checks yesterday's observations.
    :param interpret_flags: Whether to interpret the quality flags and convert them to English.
    :return: A list of all observation indices that were flagged by the quality checker.
    """
    # Download yesterday's GLOBE observations.
    fp = download_from_API(["sky_conditions", "land_covers", "mosquito_habitat_mapper", "tree_heights"],
                           date.today() - timedelta(1), download_dest="SC_LC_MHM_TH__%S.json")

    # Open and parse that file.
    observations = parse_JSON(fp)

    # Perform quality check.
    flagged_ob_indices = do_quality_check(observations, ["*"], interpret=interpret_flags)
    return flagged_ob_indices