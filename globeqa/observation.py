from datetime import datetime
import shapely.geometry as sgeom
from typing import Optional, List, Union, Dict


class CloudCover:
    def __init__(self, val: Optional[Union[float, str]]):

        self._val = val

        if type(val) is str:
            try:
                val = float(val)
            except ValueError:
                pass

        if type(val) is str:
            self._cat = val
            self._num = self.cat_to_mid(val)
            self._mid = self._num
        elif type(val) is float:
            val = min(max(val, 0.0), 1.0)
            self._num = val
            self._cat = self.num_to_cat(val)
            self._mid = self.cat_to_mid(self._cat)
        elif val is None:
            self._num = None
            self._cat = None
            self._mid = None
        else:
            raise TypeError("Argument 'val' must be a string, a float, or None.")

    def __lt__(self, other):
        c = self._compare(other)
        return c < 0. if c is not None else NotImplemented

    def __gt__(self, other):
        c = self._compare(other)
        return c > 0. if c is not None else NotImplemented

    def __le__(self, other):
        c = self._compare(other)
        return c <= 0. if c is not None else NotImplemented

    def __ge__(self, other):
        c = self._compare(other)
        return c >= 0. if c is not None else NotImplemented

    def __eq__(self, other):
        c = self._compare(other)
        return c == 0. if c is not None else NotImplemented

    def __ne__(self, other):
        c = self._compare(other)
        return c != 0. if c is not None else NotImplemented

    def _compare(self, other):
        if self.mid is None:
            return None
        elif type(other) is CloudCover:
            return self.num - other.num
        elif type(other) is str:
            return self.mid - self.cat_to_mid(other)
        elif type(other) is float:
            return self.num - other
        else:
            return None

    @property
    def cat(self) -> Optional[str]:
        """
        :return: The GLOBE category that this cloud cover falls into.
        """
        return self._cat

    @property
    def mid(self) -> Optional[float]:
        """
        :return: The numeric midpoint of the GLOBE category that this cloud cover falls into.
        """
        return self._mid

    @property
    def num(self) -> Optional[float]:
        """
        :return: The numeric value of this cloud cover (fraction).  If initialized with a category string, this will be
        the midpoint of the category (and equal to the mid property).
        """
        return self._num

    @property
    def val(self):
        """
        :return: The value used to initialize this CloudCover.
        """
        return self._val

    def num_to_cat(self, fraction):
        fraction = min(max(fraction, 0.0), 1.0)
        bins = dict(none=0.00, few=0.10, isolated=0.25, scattered=0.50, broken=0.90)
        for k, v in bins.items():
            if fraction <= v:
                return k
        return "overcast"

    def cat_to_mid(self, cat):
        try:
            return dict(none=0.00, clear=0.05, few=0.05, isolated=0.175, scattered=0.375, broken=0.70, overcast=0.95,
                        obscured=0.95)[cat]
        except KeyError:
            raise ValueError("'{}' does not represent a valid cloud cover category.".format(cat))


class Observation:
    def __init__(self, header: Optional[List[str]] = None, row: Optional[List[str]] = None,
                 feature: Optional[dict] = None, protocol: Optional[str] = None):
        """
        An Observation object represents a single GLOBE observation.  Initialization processes either a line from a CSV
        file or a feature from a JSON object.  The properties of the observation can be accessed by key (__getitem__).
        :param header: The header row from a CSV file.
        :param row: The observation row from a CSV file.
        :param feature: The JSON feature representing an observation.
        :param protocol: The protocol that the CSV file is derived from.
        :raises ValueError: if neither feature nor (header + row + protocol) are provided.
        """

        if header is not None and row is not None and protocol is not None:
            self._raw = dict(protocol=protocol)
            self.fromAPI = False

            for c in range(len(header)):
                column = header[c]
                try:
                    self._raw[column] = row[c].strip()
                except KeyError:
                    self._raw[column] = None

        elif feature is not None:
            self.fromAPI = True
            self._raw = feature["properties"]
            self._raw["Observation Latitude"] = feature["geometry"]["coordinates"][1]
            self._raw["Observation Longitude"] = feature["geometry"]["coordinates"][0]

        else:
            raise ValueError("Either 'feature' or all of ('header', 'row', and 'protocol') must be provided.")

        self.flags = []

    def __getitem__(self, item: str):
        """
        Attempts to get the requested key.  If the key verbatim does not exist, it will be prefixed with the protocol
        name and retrieval will be reattempted.  Failing that, a KeyError will be raised.
        """
        try:
            return self._raw[item]
        except KeyError:
            return self._raw[self.key_prefix + item]

    def __contains__(self, item):
        return self.soft_get(item) is not None

    def __setitem__(self, key, value):
        self._raw[key] = value

    def soft_get(self, item: str):
        """
        Attempts to get the requested key.  Unlike __getitem__, if a KeyError is raised, it will caught and ignored,
        and None will be returned instead.
        :param item: They key to look for.
        :return: The value associated with the key (with prefix if needed), or None if the key doesn't exist.
        """
        try:
            return self[item]
        except KeyError:
            return None

    @property
    def key_prefix(self) -> str:
        """
        :return: Gets the prefix that should be appended to any key retrieved, based on the protocol.
        """
        if not self.fromAPI:
            return ""
        else:
            return self["protocol"].replace("_", "")

    @property
    def measured_dt(self) -> Optional[datetime]:
        """
        :return: The measurement datetime of this observation, or none if the date and/or time are recorded incorrectly.
        Raises flag DX if the datetime is missing, and DI if the datetime is invalid or malformed.
        """
        # Find or construct the string representing the datetime.

        # sic: "Measurement" may be misspelled in the file.
        d = self.try_keys(["Measurment Date (UTC)", "Measurement Date (UTC)"])
        t = self.try_keys(["Measurment Time (UTC)", "Measurement Time (UTC)"])
        if d is not None and t is not None:
            dtstring = "{}T{}".format(d, t)
        else:
            try:
                dtstring = self["MeasuredAt"]
            except KeyError:
                self.flag("DX")
                return None

        # Attempt to convert that string to a datetime.
        try:
            return datetime.strptime(dtstring, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            # If that format string fails, try add in microseconds
            try:
                return datetime.strptime(dtstring, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                self.flag("DI")
                return None

    @property
    def lat(self) -> Optional[float]:
        """
        :return: The latitude of this observation, or None if the latitude is invalid.
        """
        return self.get_float("Observation Latitude", "LM", "LI")

    @property
    def lon(self) -> Optional[float]:
        """
        :return: The longitude of this observation, or None if it is missing or invalid.
        """
        return self.get_float("Observation Longitude", "LM", "LI")

    @property
    def elevation(self) -> Optional[float]:
        """
        :return: The elevation of this observation, or None if it is missing or invalid.
        """
        val = self.get_float(["elevation", "Observation Elevation"], "EX", "EI")
        if not (-300. <= val <= 6000.):
            self.flag("ER")
        return val

    def get_float(self, keys: Union[str, List[str]],
                  flag_missing: str = None, flag_invalid: str = None) -> Optional[float]:
        """
        Attempts to get a float from the given keys.  Whichever key works first, with or without the prefix, is used.
        :param keys: A key or list of keys to get.  A single key will be treated as a list of one key.
        :param flag_missing: The flag to raise if the value is missing.  Default None.
        :param flag_invalid: The flag to raise if the value if invalid for a float.  Default None.
        :return: The floated key value, or None if the value is missing or invalid.
        """
        val = self.try_keys(keys if type(keys) is list else [keys])
        try:
            return float(val)
        # TypeError occurs if we try to float None.  val is None if none of the keys returned anything.
        except TypeError:
            self.flag(flag_missing)
            return None
        # ValueError occurs if a key returned something, but the string does not represent a float.
        except ValueError:
            self.flag(flag_invalid)
            return None

    def sum_keys(self, keys: List[str]) -> Optional[float]:
        """
        Gets the sum of the values of the given keys for this observation.
        :param keys: The keys to look for.
        :return: The sum of the keys' values as long as at least one of them was a valid float; otherwise, None.
        """
        total = None
        for key in keys:
            val = self.get_float(key)
            if val is not None:
                total = val if total is None else total + val
        return total

    @property
    def tcc(self) -> Optional[str]:
        """
        :return: Gets the total cloud cover of this observation as a string, or None if it is invalid.  Raises flag CI
        if the cloud cover is an invalid value, or CX if it is missing.
        """
        # Return nothing and raise no flags if the protocol isn't SC.
        if self["protocol"] != "sky_conditions":
            return None

        val = self.try_keys(["Total Cloud Cover", "CloudCover"])
        if val is not None:
            if val in ["none", "clear", "few", "isolated", "scattered", "broken", "overcast", "obscured"]:
                return val
            elif val == "-99":
                self.flag("CM")
                return None
            else:
                self.flag("CI")
                return None
        else:
            self.flag("CX")
            return None

    @property
    def tcc_aqua(self) -> Optional[float]:
        """
        :return: Gets the total cloud cover (sum of each level) as reported by Aqua.  Returns None if Aqua is not
        matched to this observation.
        """
        s = self.sum_keys(["Aqua Low Cloud Cover", "Aqua Mid Cloud Cover", "Aqua High Cloud Cover"])
        return s / 100. if s is not None else None

    @property
    def tcc_terra(self) -> Optional[float]:
        """
        :return: Gets the total cloud cover (sum of each level) as reported by Terra.  Returns None if Terra is not
        matched to this observation.
        """
        s = self.sum_keys(["Terra Low Cloud Cover", "Terra Mid Cloud Cover", "Terra High Cloud Cover"])
        return s / 100. if s is not None else None

    @property
    def tcc_geo(self) -> Optional[float]:
        """
        :return: Gets the total cloud cover (sum of each level) as reported by a geostationary satellite.  Returns None
        if there is no geostationary satellite matched to this observation.
        """
        s = self.sum_keys(["GEO Low Cloud", "GEO Mid Cloud", "GEO High Cloud"])
        return s / 100. if s is not None else None

    @property
    def tcc_aqua_cc(self):
        return CloudCover(self.tcc_aqua)

    @property
    def tcc_terra_cc(self):
        return CloudCover(self.tcc_terra)

    @property
    def tcc_geo_cc(self):
        return CloudCover(self.tcc_geo)

    @property
    def cloud_types(self) -> List[str]:
        """
        :return:  Gets the list of cloud types reported in this observation.
        """
        cloud_types = ["Cirrus", "Cirrocumulus", "Cumulus", "Altocumulus", "Stratus", "Nimbostratus", "Altostratus",
                       "Stratocumulus", "Cumulonimbus", "Cirrostratus"]
        return [key for key in cloud_types if self.soft_get(key) == "true"]

    @property
    def obscurations(self) -> List[str]:
        """
        :return:  Gets the list of obscurations reported in this observation.
        """
        obscurations = ["Fog", "Smoke", "Haze", "VolcanicAsh", "Dust", "Sand", "Spray", "HeavyRain", "HeavySnow",
                        "BlowingSnow"]
        return [key for key in obscurations if self.soft_get(key) == "true"]

    def try_keys(self, keys: List[str]):
        """
        Gets the value of the first key in the list that resolves to a valid key.
        :param keys: The keys to check for.  Note that protocol name will be added automatically if needed.
        :return: The value of the key if a match is found; None otherwise.
        """
        for key in keys:
            try:
                return self[key]
            except KeyError:
                pass
        return None

    def has_flag(self, flag: str) -> bool:
        """
        :param flag: The flag to check for.
        :return: Whether the flag is raised on this observation.
        """
        return flag in self.flags

    @property
    def flagged(self) -> bool:
        """
        :return: Whether any flags have been raised for this observation.
        """
        return len(self.flags) > 0

    def flag(self, flag: Optional[str], set_raised: bool = True) -> bool:
        """
        Raises a flag for this observation if it has not already been raised.
        :param flag: The code for the flag to raise.  If None, no flag is added.
        :param set_raised: Whether to raise or lower this flag.  Default True (raise).
        :return: Whether the flag was actually raised/lowered (i.e., it wasn't already raised/lowered).
        """

        # If flag is None, do nothing.
        if flag is None:
            return False
        # If we are trying to raise a flag...
        if set_raised:
            # If the flag is not already raised, raise it.
            if flag not in self.flags:
                self.flags.append(flag)
                return True
            # Otherwise, do nothing.
            return False
        # If we are trying to lower a flag...
        else:
            # If the flag is raised, lower it.
            if flag is self.flags:
                self.flags.remove(flag)
                return True
            # Otherwise, do nothing.
            return False

    def check_for_flags(self, land=None):
        """
        Calls all properties and methods that could raise flags.
        :param land: The PreparedGeometry for checking whether the location is over land. If None, determination of
        whether a location is a water will be ignored.
        """
        _ = self.elevation
        self._check_for_flags_datetime()
        self._check_for_flags_location(land)
        self._check_for_flags_obscurations()
        self._check_for_flags_ranges()

    def _check_for_flags_datetime(self):
        """
        Checks this observation for datetime flags: DF, DI, DM, DO, and DZ.
        """
        # Retrieving the datetime could raise DI or DM flags.
        dt = self.measured_dt
        if dt is not None:
            if dt > datetime.now():
                self.flag("DF")
            if dt.year < 1995:
                self.flag("DO")
            if dt.hour == 0 and dt.minute == 0:
                self.flag("DZ")

    def _check_for_flags_location(self, land=None):
        """
        Checks this observation for flags associated with the location: LI, LW, and LZ.  Additionally check if spray was
        reported over land (flag OP).
        :param land: The PreparedGeometry for determining whether the point is over land.  If None, whether the location
        is not over water will not be checked (flags LW and OP will not be raised).
        """
        if self.lat is not None and self.lon is not None:
            if land is not None:
                # If the point is not on land, flag LW.
                if not land.contains(sgeom.Point(self.lon, self.lat)):
                    self.flag("LW")
                # If the point is on land but sea spray was reported, flag OP.
                elif self.soft_get("Spray") == "true":
                    self.flag("OP")

            if self.lat == 0. and self.lon == 0.:
                self.flag("LZ")
        # If lat or lon is invalid, flag LI.
        else:
            self.flag("LI")

    def _check_for_flags_obscurations(self):
        """
        Checks this observation for flags associated with obscuration: HC, HO, OC, OD, OO, OR, and OX.  Because .tcc
        will also be accessed, flags CI, CM and CX could also be raised.  Flag OP is raised in _check_for_flags_location
        because it requires the land check.
        """
        if self["protocol"] == "sky_conditions":
            obscuration_types = ["Fog", "Smoke", "Haze", "VolcanicAsh", "Dust", "Sand", "Spray", "HeavyRain",
                                 "HeavySnow", "BlowingSnow"]

            num_obscurations = 0
            for key in obscuration_types:
                if self.soft_get(key) == "true":
                    num_obscurations += 1

            if num_obscurations == 2:
                self.flag("OD")
            elif num_obscurations > 2:
                self.flag("OR")

            # If num_obscurations and tcc disagree, raise a flag.
            if (num_obscurations > 0) and (self.tcc != "obscured"):
                self.flag("OO")
            elif (num_obscurations == 0) and (self.tcc == "obscured"):
                self.flag("OX")

            # If they do agree that there is obscuration, but cloud types are still being reported, raise a flag.
            elif ((num_obscurations > 0) or (self.tcc == "obscured")) and (len(self.cloud_types) > 0):
                self.flag("OC")

            # If haze as obscuration and sky clarity disagree, raise a flag.
            haze = self.soft_get("Haze")
            sky_clarity = self.soft_get("SkyClarity")
            if (haze == "true") and (sky_clarity != "extremely hazy"):
                self.flag("HO")
            elif (haze != "true") and (sky_clarity == "extremely hazy"):
                self.flag("HC")

    def _check_for_flags_ranges(self):
        """
        Checks this observation for flags associated with miscellaneous ranges: MI, MR, NI, NR, TI, TM, TR, and TX.
        """
        if self["protocol"] == "tree_heights":
            self.check_key_in_range("TreeHeightAvgM", 0., 99., "T", -99.)

        # Check mosquito larvae count.
        if self["protocol"] == "mosquito_habitat_mapper":
            val = self.soft_get("LarvaeCount")
            if val is not None:
                try:
                    val = float(val)
                    if not (0 <= val <= 199):
                        self.flag("MR")
                except ValueError:
                    if val not in ["1-25", "26-50", "51-100", "more than 100"]:
                        self.flag("MI")

        # Check total contrail count.
        contrails = 0
        for key in ["ShortLivedContrails", "SpreadingContrails", "NonSpreadingContrails"]:
            try:
                val = self[key]
                if (val is not None) and (val.strip() != ""):
                    contrails += float(val)
            # If the key doesn't exist, that's fine.  Ignore it.
            except KeyError:
                pass
            # If the value isn't an integer, something's not right.
            except ValueError:
                self.flag("NI")

        if contrails >= 20:
            self.flag("NR")

    def check_key_in_range(self, key: str, low: float, high: float, x: str, missing: Optional[float] = None):
        """
        Checks that the given key is in the given range.
        :param key: The key (or partial key) to check.
        :param low: The lowest value the key should have.
        :param high: The highest value the key should have.
        :param x: The first character of the flag code.
        :param missing: The value that indicates missing data (not a missing key).  If this value is found, then the
        range check wil not be performed.
        :return: None.  This observation's flags will be updated if necessary, with xR for values of range, xM for
        properly-reported missing values. mX for missing keys, and mI for invalid keys that could not be converted to
        floats.
        """
        val = self.soft_get(key)
        if val is None:
            self.flag(x + "X")
        else:
            try:
                val = float(val)
                if (missing is not None) and (val == missing):
                    self.flag(x + "M")
                elif not (low <= val <= high):
                    self.flag(x + "R")
            except ValueError:
                self.flag(x + "I")

    _flag_definitions = dict(
            CI="Cloud cover is invalid (not a proper category)",
            CM="Cloud cover is coded as missing",
            CX="Cloud cover attribute is missing",
            DF="Datetime of measurement is in the future",
            DI="Datetime of measurement is invalid (string malformed, or not a real datetime)",
            DO="Datetime of measurement is before 1995",
            DX="Datetime of measurement attribute is missing",
            DZ="Datetime of measurement is at midnight UTC",
            EI="Elevation is invalid (not a number)",
            EM="Elevation is coded as missing",
            ER="Elevation is outside of expected range (-300m to 6000m)",
            EX="Elevation attribute is missing",
            HC="Extreme haze reported in sky clarity but not as an obstruction",
            HO="Haze reported as an obstruction but not as extreme haze in sky clarity",
            LI="Location is not a valid lat-lon pair",
            LW="Location may be over water",
            LZ="Location is at 0 N, 0 E",
            MI="Mosquito larvae count is invalid (not a number or app range)",
            MR="Mosquito larvae count outside of expected range (0 - 199)",
            NI="Contrail count is invalid (not a number)",
            NR="Contrail count outside of expected range (0 - 19)",
            OC="Obscuration reported but cloud types also reported",
            OD="Two obscurations reported",
            OO="Obscuration types selected but cover not obscured",
            OP="Spray reported possibly over land",
            OR="More than two obscurations reported",
            OX="Obscured cover reported but obscuration type missing",
            TI="Tree height is invalid (not a number)",
            TM="Tree height is coded as missing",
            TR="Tree height outside of expected range (0m - 199m)",
            TX="Tree height attribute is missing",

            # The following flags are defined, but not yet implemented:
            PI="Protocol invalid or not yet implemented",
        )

    @property
    def flag_definitions(self):
        """
        :return: A dictionary of (str, str) pairs where each key is the identifier for a flag that is described by its
        value.
        """
        return self._flag_definitions

    @property
    def flags_english(self) -> List[str]:
        """
        :return: All flags for this observation converted to human-readable terms.
        """
        # Return the value corresponding to the key for each flag.
        return [self.flag_definitions[i] for i in self.flags]

    @property
    def keys(self) -> List[str]:
        """
        :return: Gets all the keys associated with this observation.
        """
        return self._raw.keys()

    @property
    def source(self) -> str:
        """
        :return: Gets the source of this observation.
        """
        try:
            return self["DataSource"]
        except KeyError:
            return (("GLOBE-trained " if self["Is GLOBE Trained"] == "1" else "") +
                    ("citizen science" if self["is Citizen Science"] == "1" else "")).strip()

    @property
    def photo_urls(self) -> Dict[str, str]:
        """
        :return: Gets a dictionary of direction=url pairs for each direction that has a photo for this observation.
        Direction keys are be South, West, North, East, Upward, and Downward.  A key will be absent if no photo in that
        direction exists.  The value of a given key is not guaranteed to be a valid url; in particular, the value may be
        "rejected" if a photo was submitted but was rejected from the GLOBE database.
        """
        ret = {}
        for direction in ["South", "West", "North", "East", "Upward", "Downward"]:
            try:
                ret[direction] = self["{}PhotoUrl".format(direction)]
            except KeyError:
                pass
        return ret

    @property
    def is_from_observer(self):
        """
        :return: Returns whether or not this observation comes from the GLOBE Observer app.
        """
        return self.source in ["GLOBE Observer App", "citizen science", "GLOBE-trained citizen science"]

    @property
    def id(self):
        """
        :return: Gets the observation's ID or number, whichever is available first.
        """
        return self.try_keys(["ObservationId", "Observation Number"])
