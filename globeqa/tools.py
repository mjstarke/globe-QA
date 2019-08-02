import cartopy.io.shapereader as shpreader
from contextlib import closing
from datetime import date, datetime, timedelta
import json
from netCDF4 import Dataset
from globeqa.observation import Observation
from operator import itemgetter
from os.path import isfile, join
from shapely.ops import unary_union
from shapely.prepared import prep
from shutil import copyfileobj
from tqdm import tqdm
from typing import List, Dict, Optional, Union, Tuple, Iterable, Callable, Any
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
        line_count = sum(1 for _ in open(fp, 'rb')) - 1
        # Loop through each line.
        for line in tqdm(f, total=line_count, desc="Reading CSV file"):
            # If limited by count, exit.
            if len(observations) >= count:
                break
            # Split the line and create an Observation for it.
            s = line.split(',')
            observations.append(Observation(header, s, protocol=protocol))

    return observations


def download_from_api(protocols: List[str], start: Union[date, datetime], end: Optional[Union[date, datetime]] = None,
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

    # Create a string that represents the protocol part of the query.
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

    ret = []
    for o in tqdm(range(len(raw["features"])), desc="Parsing JSON as observations"):
        ob = raw["features"][o]
        ret.append(Observation(feature=ob))
    return ret

    # Although this works and may be more efficient, I'm not sure how to make it work with tqdm...
    # return [Observation(feature=ob) for ob in raw["features"]]


def get_flag_counts(obs: List[Observation]) -> Dict[str, int]:
    """
    Gets a summary of all flags for the given observations.
    :param obs: The observations to analyze.
    :return: The dictionary of (flag, count) pairs for each flag found at least once.
    """
    flag_counts = dict()
    print("--  Enumerating flags...")
    # tqdm not used here because this is a surprisingly fast process.
    for ob in obs:
        for flag in ob.flags:
            try:
                flag_counts[flag] += 1
            except KeyError:
                flag_counts[flag] = 1

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
    :raises TypeError: If specs is neither a string or a dict of string=bool pairs.
    """
    # If specs is a dict...
    if type(specs) == dict:
        ret = []
        # For each observation...
        for ob in tqdm(obs, desc="Filtering observations by flag"):
            # For each specification k=v, k is the flag and v is whether it must be present or absent.
            for k, v in specs.items():
                # If the flag is present or absent as required, add this ob to the list.
                if ob.has_flag(k) == v:
                    ret.append(ob)
        return ret
    # If specs is a bool, just return those obs which have or do not have flags.
    elif type(specs) == bool:
        return [ob for ob in obs if ob.flagged == specs]
    # If not a dict or bool, raise an error.
    else:
        raise TypeError("Argument 'specs' must be either Dict[str, bool] or bool.")


def filter_by_flag_sets(obs: List[Observation], all_of: Iterable[str] = (), none_of: Iterable[str] = (),
                        any_of: Iterable[str] = ()) -> List[Observation]:
    """
    Filters observations by whether they have or do not have certain combinations of flags.
    :param obs: The observations to assess.
    :param all_of: A list of flags that must all be present for an observation to pass.  Default (), which passes all
    observations.
    :param none_of: A list of flags that must all be absent for an observation to pass.  Default (), which passes all
    observations.
    :param any_of: A list of flags of which one must be present for an observation to pass.  Default (), which passes
    all observations.  Passing only one flag to any_of has the same effect as instead appending that flag to all_of.
    :return: An iterable of obs that have been filtered.
    """
    # Store only those obs which have at least one flag from any_of - that is, the intersection of actual flags and
    # required flags has at least one item.
    # Note that we must skip this check of any_of is empty - otherwise, nothing passes.
    ret = [ob for ob in obs if len(set(ob.flags) & set(any_of)) > 0] if any_of else [ob for ob in obs]

    # Store only those obs which have all of the all_of flags - that is, the actual flags is a (not necessarily proper)
    # superset of the required flags.
    ret = [ob for ob in ret if set(ob.flags) >= set(all_of)]

    # Store only those obs which have none of the none_of flags - that is, the intersection of actual flags and required
    # flags is empty.
    ret = [ob for ob in ret if len(set(ob.flags) & set(none_of)) == 0]

    return ret


def get_cdf_datetime(cdf: Dataset, index: int) -> datetime:
    """
    Creates a datetime that represents the time at the given index of cdf["time"].  This assumes that cdf["time"] is
    minutes since the beginning of the run, which means that begin_date and begin_time are also supplied by ["time"].
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
    Find the indices of the closest gridbox to a given point in spacetime.
    :param cdf: A NetCDF4 dataset.
    :param t: The datetime of the point.
    :param lat: The signed latitude of the point in degrees.
    :param lon: The signed longitude of the point in degrees.
    :return: The indices for time, latitude, and longitude, respectively, of the gridbox that most closely
    approximates the point in the dataset.  There is no guarantee that these indices are valid for the dataset.
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
    time_step = cdf["time"][1] - cdf["time"][0]
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
    or '110m'.  Default '50m'.
    :return: The PreparedGeometry object that can be used for point-land checking.
    :raises ValueError: If geometry_resolution is not '10m', '50m', or '110m'.
    """
    if geometry_resolution not in ["10m", "50m", "110m"]:
        raise ValueError("Argument 'geometry_resolution' must be either '10m', '50m', or '110m'.")

    print("--  Preparing Earth geometry...")
    land_shp_fname = shpreader.natural_earth(resolution=geometry_resolution, category='physical', name='land')
    land_geom = unary_union(list(shpreader.Reader(land_shp_fname).geometries()))
    land = prep(land_geom)
    print("--  Earth geometry prepared.")
    return land


def do_quality_check(obs: List[Observation], land=None):
    """
    Perform quality checks on the observations.
    :param obs: The observations.
    :param land: The PreparedGeometry for land checking.  If None, land check will not be performed.
    """
    for o in tqdm(range(len(obs)), desc="Performing quality check"):
        obs[o].check_for_flags(land)


def find_all_values(obs: List[Observation], attribute: str) -> Dict[str, int]:
    """
    Finds all possible values for a given attribute in the observations.
    :param obs: The observations.
    :param attribute: The attribute to find values for.
    :return: A dictionary of (value, count) pairs, each indicating that the given attribute had the value 'value' count
    times in the observations.  If an observation does not have a particular attribute, it contributes nothing to this
    returned dictionary.
    """
    ret = dict()

    for ob in tqdm(obs, desc="Sifting observations"):
        if attribute in ob:
            val = ob[attribute]
            try:
                ret[val] += 1
            except KeyError:
                ret[val] = 1

    return ret


def find_all_attributes(obs: List[dict]) -> List[str]:
    """
    Generates a sorted list of all attributes that occur at least once in the observations.
    :param obs: The observations.
    :return: A sorted list of all attributes that occur at least once in the observations.
    """
    all_keys = []
    for ob in tqdm(obs, desc="Sifting observations"):
        for key in ob.keys:
            if key not in all_keys:
                all_keys.append(key)

    return sorted(all_keys)


def pretty_print_dictionary(d: dict, print_percent: bool = True, print_total: bool = True,
                            total: Optional[float] = None, sorting: Union[None, str, Iterable] = "ka",
                            min_column_widths: Tuple[int, int, int] = (1, 1, 1),
                            compress_below: Optional[float] = None, column_separator: str = "  ") -> list:
    """
    Pretty-prints the contents of a dictionary.
    :param d: The dictionary to assess.
    :param print_percent: Whether to calculate percentages that each value makes up of the whole.  Fails if any values
    in d are not numeric.  Default True.
    :param print_total: Whether to print a row at the end for the sum of all the values.  Fails if any values in d are
    not numeric.  Default True.
    :param total: The number that will be printed if print_total or used to calculate percentage contributions if
    print_percent.  Default None, which automatically calculates total as the sum of dictionary values.
    :param sorting: If an iterable, specifies the order in which the keys will be printed.  If None, key ordering will
    be arbitrary (d.keys() is used).  If "ka", keys will be sorted ascending; "kd" sorts descending.  "va" will sort the
    keys by their corresponding values ascending; "vd" sorts by values descending.  Default "ka".
    :param min_column_widths: A triple of the minimum widths of the three printed columns (key, value, and percentage,
    respectively).  Default (1, 1, 1).
    :param compress_below: Items in d whose values are less than compress_below will be compressed into a single
    "(other)" entry at the bottom of the table (unless the sum of these items is 0).  Default None, which compresses no
    items.
    :param column_separator: The string which separates the printed columns.  Default '  ' (two spaces).
    :return: None.  The results are printed in three columns: key, value, percentage (if do_percent).  The columns are
    automatically sized according to their contents.  If d contains no keys, nothing is printed.
    :raises TypeError: If sorting is a non-iterable non-string.
    :raises ValueError: If min_column_widths does not have length 3.
    :raises ValueError: If any element of min_column_widths is less than 1.
    :raises ValueError: If sorting is an invalid string.
    :raises ZeroDivisionError: If total is zero (whether set explicitly or calculated automatically).
    :return: The list of keys in the order that they were printed, or an empty list if no keys were printed.  Note that
    the compression and total rows are not considered keys.
    """
    if len(min_column_widths) != 3:
        raise ValueError("Argument 'min_column_widths' must have length 3.")

    for width in min_column_widths:
        if width < 1:
            raise ValueError("All minimum column widths must be at least 1.")

    # If there are no keys in the dictionary, there's nothing to do.
    if len(d.keys()) == 0:
        return []

    # keys remains as this arbitrary list if sorting is None.
    keys = d.keys()

    if type(sorting) is str:
        if sorting == "ka":
            keys = sorted(d.keys())
        elif sorting == "kd":
            keys = sorted(d.keys())[::-1]
        elif sorting in "va":
            keys = [item[0] for item in sorted(d.items(), key=itemgetter(1))]
        elif sorting in "vd":
            keys = [item[0] for item in sorted(d.items(), key=itemgetter(1), reverse=True)]
        else:
            raise ValueError("Argument 'sorting' only accepts 'ka', 'kd', 'va', or 'vd' for strings.")
    elif sorting is not None:
        # If not None, sorting should be an iterable.  Test that here.
        try:
            _ = (e for e in d)
        except TypeError:
            raise TypeError("Argument 'sorting' must be None, 'ka', 'kd', 'va', 'vd', or an iterable.")
        keys = sorting

    # Use explicitly set total if available; otherwise, calculate total.
    if (total is None) and (print_percent or print_total):
        total = sum(d[key] for key in keys)

    # If total is zero, we can't do percentage calculations.
    if print_percent and (total == 0):
        raise ZeroDivisionError("Total is 0; percentage contributions cannot be calculated.")

    # Chop off low values if requested.
    compressed = None
    if compress_below is not None:
        compressed = sum(d[key] for key in keys if d[key] < compress_below)
        keys = [key for key in keys if d[key] >= compress_below]

    # Generate contents of columns.
    column1 = [str(key) for key in keys]
    column2 = [str(d[key]) for key in keys]
    # Third column is blank if percent is not requested.
    column3 = ["{:7.2%}".format(d[key] / total) for key in keys] if print_percent else [""] * len(keys)

    if (compressed is not None) and (compressed > 0):
        column1.extend(["", "(other)"])
        column2.extend(["", str(compressed)])
        column3.extend(["", "{:7.2%}".format(compressed / total) if print_percent else ""])

    # Add two more rows for total if requested.
    if print_total:
        column1.extend(["", "(total)"])
        column2.extend(["", str(total)])
        column3.extend(["", "100.00%" if print_percent else ""])

    # Calculate the width that each column requires.
    column1_width = max(max(len(a) for a in column1), min_column_widths[0])
    column2_width = max(max(len(a) for a in column2), min_column_widths[1])
    column3_width = max(max(len(a) for a in column3), min_column_widths[2])

    # Create the format string with appropriate column width.
    fmt = "{:A}S{:>B}S{:C}".replace("A", str(column1_width)).replace("B", str(column2_width)).replace(
        "C", str(column3_width)).replace("S", column_separator)

    # Print each row.
    for a in range(len(column1)):
        print(fmt.format(column1[a], column2[a], column3[a]))

    return list(keys)


def bin_cloud_fraction(fraction: float, clip: bool = False) -> str:
    """
    Bins a cloud fraction into a GLOBE cloud cover category.
    :param fraction: The cloud fraction, from 0.0 (clear) to 1.0 (overcast).  A ValueError is raised if the fraction
    lies outside this range.
    :param clip: Whether to force fraction into the range 0.0 to 1.0.  ValueError will not be raised in this case.
    Default False.
    :return: A string describing the cloud cover: one of [none, few, isolated, scattered, broken, overcast].
    :raises ValueError: If fraction is not in the range 0.0 to 1.0, unless clip is True.
    """
    if clip:
        fraction = min(max(fraction, 0.0), 1.0)
    elif not (0.0 <= fraction <= 1.0):
        raise ValueError("Argument 'fraction' must be between 0.0 and 1.0 (inclusive).")

    bins = dict(none=0.00,
                few=0.10,
                isolated=0.25,
                scattered=0.50,
                broken=0.90,
                overcast=1.00)

    for k, v in bins.items():
        if fraction <= v:
            return k


def filter_by_datetime(obs: List[Observation], earliest: Optional[datetime] = datetime.min,
                       latest: Optional[datetime] = datetime.max, assume_chronology: bool = False) -> List[Observation]:
    """
    Filters a list of observations to a certain datetime range, assuming chronology of the observations.
    :param obs: The observations.
    :param earliest: The earliest datetime that an observation may have to pass the filter.  Default datetime.min, which
    filters out no observations.
    :param latest: The earliest datetime that an observation may have to NOT pass the filter - that is, observations
    with a datetime equal to latest will NOT be included.  Default datetime.max, which filters out no observations.
    :param assume_chronology: Whether the observations are in ascending chronological order.  If set to True when the
    observations are NOT in strictly chronological order, arbitrary returns will result.  Default False.
    :return: The observations that passed the filter.
    :raises ValueError: If earliest is after latest.
    """
    if earliest is not None and latest is not None and (earliest >= latest):
        raise ValueError("Argument 'earliest' must not be after argument 'latest'.")

    elif earliest is None and latest is None:
        return obs

    if assume_chronology:
        first_acceptable_index = 0
        if earliest is not None:
            for o in tqdm(range(len(obs)), desc="Cutting for early date"):
                if obs[o].measured_dt >= earliest:
                    first_acceptable_index = o
                    break

        last_acceptable_index = None
        if latest is not None:
            for o in tqdm(range(len(obs[first_acceptable_index:])), desc="Cutting for late date"):
                if obs[o].measured_dt >= latest:
                    last_acceptable_index = o
                    break

        return obs[first_acceptable_index:last_acceptable_index]

    else:
        ret = []
        for ob in tqdm(obs, desc="Filtering observations by datetime"):
            if earliest <= ob.measured_dt < latest:
                ret.append(ob)

        return ret


def filter_by_hour(obs: List[Observation], hours: List[int]) -> List[Observation]:
    """
    Filters a list of observations by the hour of measurement.
    :param obs: The observations.
    :param hours: The hours that shall pass the filter.
    :return: The observations that passed the filter.
    """
    return [ob for ob in obs if ob.measured_dt.hour in hours]


def process_one_day(download_folder: str = "", download_file: str = "SC_LC_MHM_TH__%S.json",
                    day: Optional[Union[date, datetime]] = None):
    """
    Downloads, parses, and quality-checks one day's observations.
    :param download_folder: The folder to download the JSON file to.  Default "" (current working directory).
    :param download_file: The name that the JSON file should have.  Certain % codes are replaced; see
    download_from_api().  Default "SC_LC_MHM_TH__%S.json" (%S replaced by the date).
    :param day: The day to process.  Default None, which is treated as yesterday.
    :return: The list of observations.
    :raises ValueError: If the JSON file contains no observations.
    """
    if day is None:
        day = date.today() - timedelta(1)

    # Download yesterday's GLOBE observations.
    fp = download_from_api(["sky_conditions", "land_covers", "mosquito_habitat_mapper", "tree_heights"],
                           day, download_dest=join(download_folder, download_file))

    # Open and parse that file.
    observations = parse_json(fp)

    if len(observations) == 0:
        raise ValueError("The JSON file at '{}' contains no observations.".format(fp))

    # Perform quality checking.
    land = prepare_earth_geometry()
    do_quality_check(observations, land)

    # Summarize flags.
    flag_summary = get_flag_counts(observations)
    pretty_print_dictionary(flag_summary, total=len(observations))

    return observations


def filter_by_datetime_cdf(obs: List[Observation], cdf: Dataset, buffer: timedelta):
    """
    Filters a list of observations, returning only those which lie within the time span of the CDF with the given
    buffer.
    :param obs: A list of observations.
    :param cdf: A NetCDF4 Dataset.
    :param buffer: The amount of time on either side of the Dataset's begin and end time in which observation will still
    pass the filter.  For instance, if buffer is 30 minutes, then observations will pass if they are between
    (CDF begin datetime - 30 minutes) and (CDF end datetime + 30 minutes).
    :return:
    """
    earliest = get_cdf_datetime(cdf, 0) - buffer
    latest = get_cdf_datetime(cdf, -1) + buffer
    return [ob for ob in obs if earliest <= ob.measured_dt < latest]


def patch_obs(obs: List[Observation], fp: str, attribute: str, processor: Callable[[str], Any] = lambda v: v):
    """
    Applies a patch to the observations.  The patch is a CSV file whose first column is either to observation ID or
    number (whichever is present in the obs), and the second column is the value associated with that observation.
    :param obs: The observations to patch.
    :param fp: The path to the patch file.
    :param attribute: The attribute to store the value to for each observation.
    :param processor: The function used to process incoming values; i.e., float or int (as otherwise all values are
    strings).  Default lambda v: v, which performs no processing.
    :return: None.  Observations are modified in-place.  If the following patch file is used:
        299023,foo
        928302,bar
    and attribute is "poo", then the observation with id 299023 will have ["poo"] == "foo" and the observation with id
    928302 will have ["poo"] == "bar".
    """
    patch = dict()
    with open(fp, "r") as f:
        for line in tqdm(f, desc="Reading patch"):
            try:
                ob_id, val = line.split(",")
                patch[ob_id] = processor(val[:-1])
            except ValueError:
                pass
        f.close()

    for ob in tqdm(obs, desc="Applying patch"):
        try:
            ob[attribute] = patch[ob.id]
        except KeyError:
            pass
