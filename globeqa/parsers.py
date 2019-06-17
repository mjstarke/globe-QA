from contextlib import closing
from datetime import date
import json
from globeqa.observation import Observation
from os.path import isfile
from shutil import copyfileobj
from typing import List, Optional
from urllib.request import urlopen


def parse_csv(fp: str, count: int = 1e30, progress: int = 25000,
              protocol: Optional[str] = "sky_conditions") -> List[Observation]:
    """
    Parse a CSV file containing GLOBE observations.
    :param fp: The path to the CSV file.
    :param count: The maximum number of observations to parse.  Default 1e30.
    :param progress: The interval at which to print progress updates.  Larger values cause less frequent updates. If
    not greater than zero, no progress updates will be printed.  Default 25000.
    :param protocol: The protocol that the CSV file comes from.  Default 'sky_conditions'.
    :return: The observations.
    """

    observations = []
    with open(fp, "r") as f:
        header = f.readline().split(',')
        header = [h.strip() for h in header]
        for line in f:
            s = line.split(',')
            observations.append(Observation(header, s, protocol=protocol))
            if len(observations) >= count:
                break
            if (progress > 0) and (len(observations) % progress == 0):
                print("--  Parsed {} observations...".format(len(observations)))

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
