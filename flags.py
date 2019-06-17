import cartopy.io.shapereader as shpreader
from contextlib import closing
from datetime import date, datetime, timedelta
import json
from os.path import isfile
import shapely.geometry as sgeom
from shapely.ops import unary_union
from shapely.prepared import prep
from shutil import copyfileobj
from typing import List, Optional, Union, Tuple, Dict
from urllib.request import urlopen


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
            print("... Download will not be attempted as the file already exists locally.")
            return download_dest

    try:
        print("... Downloading from API...")
        print("... {}".format(download_src))
        with closing(urlopen(download_src)) as r:
            with open(download_dest, 'wb') as f:
                copyfileobj(r, f)
        print("... Download successful.  Saved to:")
        print("... {}".format(download_dest))
    except Exception as e:
        print("(x) Download failed:")
        print(e)

    return download_dest


def parse_JSON(fp: str) -> List[dict]:
    """
    Parses a JSON file and returns its features.

    :param fp: The path to the JSON file.
    :returns: The features of the JSON.
    """
    print("... Parsing JSON from {}...".format(fp))
    with open(fp, "r") as f:
        raw = json.loads(f.read())

    print("... Parse complete.")
    return raw["features"]


# Preparations necessary for determining whether a point is over land or water.
# This code may need to download a ZIP containing Earth geometry data the first time it runs.
# Code borrowed from   https://stackoverflow.com/a/48062502

print("... Preparing Earth geometry...")
land_shp_fname = shpreader.natural_earth(resolution=geometry_resolution, category='physical', name='land')
land_geom = unary_union(list(shpreader.Reader(land_shp_fname).geometries()))
land = prep(land_geom)


def is_land(x: float, y: float) -> bool:
    """
    Determines whether a given coordinate is over land on Earth.

    :param x: The longitude of the point in decimal degrees.  Positive values are east of the Prime Meridian.
    :param y: The latitude of the point in decimal degrees.  Positive values are north of the equator.
    :returns: Whether or not the point is over land given the shapereader geometry.
    """
    return land.contains(sgeom.Point(x, y))


print("... Earth geometry prepared.")


def check_datetime(dts: str, flag_midnight: bool = True, fmt: str = "%Y-%m-%dT%H:%M:%S") -> str:
    """
    Checks the given datetime string for validity.

    :param dts: The datetime string to test.
    :param flag_midnight: Whether to flag for observations at midnight.  Default False.
    :param fmt: The formatting string to test against (reference datetime.strptime()).
    Default "%Y-%m-%dT%H:%M:%S", which would match "2019-02-07T02:05:37".
    :returns: A summary of all flags raised, or a blank string if no flags were raised.
    """
    ret = ""
    try:
        # Parse the datetime string.
        dt = datetime.strptime(dts, fmt)
        # If that datetime is in the future, flag.
        if dt > datetime.now():
            ret += "DF "
        # If the measured datetime is at midnight, this may be a default value arising from lack of entry.
        if flag_midnight and (dt.hour == 0) and (dt.minute == 0):
            ret += "DM "
        # Year should not be before 1995.
        if dt.year < 1995:
            ret += "DO "
    # Flag on ValueError, which is thrown from strptime() if the datetime string is not formatted properly.
    # This is thrown not only for positional formatting errors, but also for impossible datetimes, such as
    # hour 25, minute 61, month 13, or November 31.  Regardless of the reason, the datetime must be malformed.
    except ValueError:
        ret += "DI "

    return ret


def check_skyconditions(ob: dict) -> str:
    """
    Checks a sky_conditions observation for problems.

    :param ob: The observation.

    :return: Any flags that were raised during checking.
    """

    # Constant lists.
    CLOUD_TYPES = ["Cirrus", "Cirrocumulus", "Cumulus", "Altocumulus", "Stratus", "Nimbostratus", "Altostratus",
                   "Stratocumulus", "Cumulonimbus", "Cirrostratus"]
    COVER_LEVELS = ["none", "clear", "isolated", "scattered", "broken", "overcast", "obscured"]
    OBSCURATION_TYPES = ["Fog", "Smoke", "Haze", "VolcanicAsh", "Dust", "Sand", "Spray", "HeavyRain", "HeavySnow",
                         "BlowingSnow"]

    # Set an alias for convenience.
    props = ob["properties"]

    # Keep a concise list of all flags raised.
    flags = ""

    # Check that the coordinates point to land.  Because of the finite resolution of the Earth geometry,
    # this flag may be raised for coastal areas unnecessarily.
    if not is_land(*ob["geometry"]["coordinates"]):
        flags += "NL "

    # Check validity of the measured datetime.
    try:
        flags += check_datetime(props["skyconditionsMeasuredAt"])
    # Flag on KeyError, which indicates that the datetime is missing.
    except KeyError:
        flags += "DX "

    # For each of the CloudCover keys, if present, ensure they have valid values.
    for key in ["skyconditionsCloudCover", "skyconditionsCloudCoverHigh", "skyconditionsCloudCoverMid",
                "skyconditionsCloudCoverLow"]:
        if key in props.keys():
            if props[key] not in COVER_LEVELS:
                flags += "CI "

    # Ensure that the number of contrails being reported is reasonable.
    total_contrails = 0
    for key in ["skyconditionsShortLivedContrails", "skyconditionsSpreadingContrails",
                "skyconditionsNonSpreadingContrails"]:
        if key in props.keys():
            total_contrails += int(float(props[key]))
    if total_contrails >= 20:
        flags += "NE "

    # Determine how many obscurations were specified.  This is needed for two different checks.
    obscurations_specified = 0
    for key_ in OBSCURATION_TYPES:
        if "skyconditions" + key_ in props:
            if props["skyconditions" + key_] == "true":
                obscurations_specified += 1

    # Raise a flag if two obscurations are reported.  Some combinations of two are legitimate, but combinations of more
    # than two are probably not legitimate, for which a different flag will be raised.
    if obscurations_specified == 2:
        flags += "O2 "
    elif obscurations_specified > 2:
        flags += "OM "

    # POSSIBLY DEPRECATED

    #     # If multiple obscurations are reported, it's likely that a flag should be raised.  However, some combinations
    #     # may be legitimate and will not be flagged.  Assume at first that the combination is not legitimate.
    #     obscuration_combination_could_be_legitimate = False

    #     # If the obscurations reported are only heavy rain and fog, or heavy snow and fog, do NOT raise a flag.
    #     if obscurations_specified == 2:
    #         try:
    #             if (props["skyconditionsHeavyRain"] == "true") and (props["skyconditionsFog"] == "true"):
    #                 obscuration_combination_could_be_legitimate = True
    #         except KeyError:
    #             pass
    #         try:
    #             if (props["skyconditionsHeavySnow"] == "true") and (props["skyconditionsFog"] == "true"):
    #                 obscuration_combination_could_be_legitimate = True
    #         except KeyError:
    #             pass

    #     # If multiple obscurations were specified and it does not appear to possibly be a legitimate combination,
    #     # raise a flag.
    #     if (obscurations_specified > 1) and not obscuration_combination_could_be_legitimate:
    #         flags += "OM "

    # Ensure that, if CloudCover is obscured, no cloud types are reported.
    try:
        if props["skyconditionsCloudCover"] == "obscured":
            # Test each cloud type.  Because the CLOUD_TYPES list does not contain full key names, each key
            # must be prefixed with "skyconditions".  If the key is present and true, raise a flag.
            for key_ in CLOUD_TYPES:
                if "skyconditions" + key_ in props:
                    if props["skyconditions" + key_] == "true":
                        flags += "OC "

            # If no obscuration was specified despite obscured cover, raise a flag.
            if obscurations_specified == 0:
                flags += "OX "
    # Flag on KeyError, which indicates that cloud cover was not reported.
    except KeyError:
        flags += "CX "

    # If sky clairty is low but haze was not reported as an obstruction, raise a flag.
    # Also flag if sky clarity is good but haze is reported.
    try:
        if props["skyconditionsSkyClarity"] == "extermely hazy":
            if props["skyconditionsHaze"] == "false":
                flags += "OH "
        else:
            if props["skyconditionsHaze"] == "true":
                flags += "OI "
    except KeyError:
        pass

    return flags


def check_landcovers(ob: dict) -> str:
    """
    Checks a land_covers observation for problems.

    ob: The observation.

    returns: Any flags that were raised during checking.
    """

    # Set an alias for convenience.
    props = ob["properties"]

    # Keep a concise list of all flags raised.
    flags = ""

    # Check that the coordinates point to land.  Because of the finite resolution of the Earth geometry,
    # this flag may be raised for coastal areas unnecessarily.
    if not is_land(*ob["geometry"]["coordinates"]):
        flags += "NL "

    # Check validity of the measured datetime.
    try:
        flags += check_datetime(props["landcoversMeasuredAt"])
    # Flag on KeyError, which indicates that the datetime is missing.
    except KeyError:
        flags += "DX "

    return flags


def check_mosquitohabitatmapper(ob: dict) -> str:
    """
    Checks a mosquito_habitat_mapper observation for problems.

    ob: The observation.

    returns: Any flags that were raised during checking.
    """

    # Set an alias for convenience.
    props = ob["properties"]

    # Keep a concise list of all flags raised.
    flags = ""

    # Check that the coordinates point to land.  Because of the finite resolution of the Earth geometry,
    # this flag may be raised for coastal areas unnecessarily.
    if not is_land(*ob["geometry"]["coordinates"]):
        flags += "NL "

    # Check validity of the measured datetime.
    try:
        flags += check_datetime(props["mosquitohabitatmapperMeasuredAt"])
    # Flag on KeyError, which indicates that the datetime is missing.
    except KeyError:
        flags += "DX "

    # Ensure that the number of larvae being reported, if any, is reasonable.
    if "mosquitohabitatmapperLarvaeCount" in props.keys():
        if int(props["mosquitohabitatmapperLarvaeCount"]) >= 200:
            flags += "LE "

    return flags


def check_treeheights(ob: dict) -> str:
    """
    Checks a tree_heights observation for problems.

    ob: The observation.

    returns: Any flags that were raised during checking.
    """

    # Set an alias for convenience.
    props = ob["properties"]

    # Keep a concise list of all flags raised.
    flags = ""

    # Check that the coordinates point to land.  Because of the finite resolution of the Earth geometry,
    # this flag may be raised for coastal areas unnecessarily.
    if not is_land(*ob["geometry"]["coordinates"]):
        flags += "NL "

    # Check validity of the measured datetime.
    try:
        flags += check_datetime(props["treeheightsMeasuredAt"])
    # Flag on KeyError, which indicates that the datetime is missing.
    except KeyError:
        flags += "DX "

    # Ensure that the height of trees being reported is reasonable.
    try:
        if float(props["treeheightsTreeHeightAvgM"]) >= 200.:
            flags += "HE "
    # Flag on KeyError, which indicates that no tree height was reported.
    except KeyError:
        flags += "HX "

    return flags


def interpret_flags(flags: str, joiner: str = "\n") -> str:
    """
    Converts a string of abbreviated flags to English.

    :param flags: The flags to interpret.
    :param joiner: Each translated flag will be separated by this string.  Default "\n" (newline).
    :returns: The interpreted flags.  Raises a KeyError if a flag is unrecognized.
    """
    meanings = dict(
        CI="Cloud cover has invalid value",
        CX="Cloud cover is missing",
        DF="Datetime of measurement is in the future",
        DI="Datetime of measurement is invalid",
        DM="Datetime of measurement is at midnight",
        DO="Datetime of measurement is too old",
        DX="Datetime of measurement is missing",
        HE="Tree height is excessive",
        HX="Tree height is missing",
        LE="Mosquito larvae count is excessive",
        NE="Contrail count is excessive",
        NL="Location may not be over land",
        PI="Protocol invalid or not yet implemented",
        O2="Two obscurations reported",
        OC="Obscuration reported but cloud types also reported",
        OH="Extreme haze reported in sky clarity but not as an obstruction",
        OI="Haze reported as an obstruction but not as extreme haze in sky clarity",
        OM="More than two obscurations reported",
        OX="Obscuration reported but obscuration type missing",
    )

    # Return the value corresponding to the key for each flag, then join.
    return joiner.join([meanings[i] for i in flags.split()])


# Begin quality check.
def do_quality_check(observations: List[dict], silence_flags: Union[List[str], Tuple[str]] = ("DM",),
                     interpret: bool = False) -> List[int]:
    """
    Performs quality checks on the given observations.

    :param observations: The observations to check.  Should normally be the ["features"] of the raw JSON object.
    :param silence_flags: Flags and combinations of flags that should be silenced (will not be printed).
    Including "*" will silence all flags.  Silencing a flag does not suppress the check.  Silencing a flag or a
    combination of flags will not silence combinations of flags that contain the silenced combination (eg.,
    silencing DM will not silence DM NL).  Default ("DM",).
    :param interpret: bool.  Whether to automatically interpret the flags and convert them to English. Default
    False.

    :returns: List[int].  The indicies of every observation that was flagged.  Any flagged observations will
    also have a ["flags"] attribute if any flags were raised.  If printed, observation numbers are zero-indexed.
    """

    print("... Beginning quality check on {} observations...".format(len(observations)))

    # Keep track of which observations have been flagged.
    flagged = []

    # Iterate through each observation.
    for o in range(len(observations)):
        ob = observations[o]
        protocol = ob["properties"]["protocol"]

        # Determine which protocol this observation falls under and call the appropriate checks.
        if protocol == "sky_conditions":
            ob["flags"] = check_skyconditions(ob)
        elif protocol == "land_covers":
            ob["flags"] = check_landcovers(ob)
        elif protocol == "mosquito_habitat_mapper":
            ob["flags"] = check_mosquitohabitatmapper(ob)
        elif protocol == "tree_heights":
            ob["flags"] = check_treeheights(ob)
        else:
            ob["flags"] = "PI"

        # If any flags were raised for this observation, print them now.
        if "*" not in silence_flags:
            if ("flags" in ob.keys()) and (len(ob["flags"]) > 0):
                if ob["flags"].strip() not in silence_flags:
                    flags = interpret_flags(ob["flags"], ";  ") if interpret else ob["flags"]
                    print("/!\ Observation #{:0>8}: {}".format(o, flags))
                    flagged.append(o)

    print("... Finished quality check.")
    return flagged


# Daily procedure
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


# Sort and print the list of all properties that occur at least once in the observations.

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


# Given a key, find all occurrences in the observations and tally up how frequently each value is.
# Will have spammy results for float values.

def print_all_values(obs: List[dict], key: str) -> None:
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
        if key in ob["properties"]:
            value = ob["properties"][key]
            found_obs.append(ob)
            found_values.append(value)
            if value not in unique_values:
                unique_values.append(value)
                unique_counts.append(1)
            else:
                i = unique_values.index(value)
                unique_counts[i] += 1

    print("{} of {} observations had the key '{}'.".format(len(found_values), len(found_obs), key))
    print("Unique values for the key follow:")
    for i in range(len(unique_values)):
        print("{:6} occurrences:   {}".format(unique_counts[i], unique_values[i]))