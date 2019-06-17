from datetime import datetime
import shapely.geometry as sgeom
from typing import Optional, List, Any, Union


class Observation:
    def __init__(self, header: Optional[List[str]] = None, row: Optional[List[str]] = None,
                 feature: Optional[dict] = None, protocol: Optional[str] = None):

        if header is not None and row is not None:
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
            raise ValueError("Either 'feature' or both 'header' and 'row' must be provided.")

        self.flags = []

    def __getitem__(self, item: str):
        """
        Attempts to get the requested key.  If the key verbatim does not exist, it will be prefixed with the protocol
        name and retreival will be reattempted.  Failing that, a KeyError will be raised.
        """
        try:
            return self._raw[item]
        except KeyError:
            return self._raw[self.key_prefix + item]

    def __contains__(self, item):
        return self.soft_get(item) is not None

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
        Raises flag DX is the datetime is missing, and DI if the datetime is invalid or malformed.
        """
        # Find or construct the string representing the datetime.
        try:
            # sic: "Measurement" is misspelled in the file.
            dtstring = "{}T{}".format(self["Measurment Date (UTC)"], self["Measurment Time (UTC)"])
        except KeyError:
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

    def try_float(self, key: str) -> Optional[float]:
        """
        Attempts to float the given key from the raw observation data.
        :param key: The key to float.
        :return: The floated key, or None if the key could not be floated.
        """
        try:
            return float(self._raw[key])
        except ValueError:
            return None

    @property
    def lat(self) -> Optional[float]:
        """
        :return: The latitude of this observation, or None if the latitude is invalid.
        """
        return self.try_float("Observation Latitude")

    @property
    def lon(self) -> Optional[float]:
        """
        :return: The longitude of this observation, or None if it is missing or invalid.
        """
        return self.try_float("Observation Longitude")

    @property
    def elevation(self) -> Optional[float]:
        """
        :return: The elvation of this observation, or None if it is missing or invalid.
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
    def cloud_types(self) -> List[str]:
        """
        :return:  Gets the list of cloud types reported in this observation.
        """
        CLOUD_TYPES = ["Cirrus", "Cirrocumulus", "Cumulus", "Altocumulus", "Stratus", "Nimbostratus", "Altostratus",
                       "Stratocumulus", "Cumulonimbus", "Cirrostratus"]
        ret = []
        for key in CLOUD_TYPES:
            if self.soft_get(key) == "true":
                ret.append(key)
        return ret

    @property
    def obscurations(self) -> List[str]:
        """
        :return:  Gets the list of obscurations reported in this observation.
        """
        OBSCURATIONS = ["Fog", "Smoke", "Haze", "VolcanicAsh", "Dust", "Sand", "Spray", "HeavyRain", "HeavySnow",
                        "BlowingSnow"]
        ret = []
        for key in OBSCURATIONS:
            if self.soft_get(key) == "true":
                ret.append(key)
        return ret

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

    def flag(self, flag: Optional[str]) -> bool:
        """
        Raises a flag for this observation.
        :param flag: The code for the flag to raise.  If None, no flag is added.
        :return: Whether the flag was actually added.  Duplicate flags will not be added.
        """
        if (flag not in self.flags) and (flag is not None):
            self.flags.append(flag)
            return True
        else:
            return False

    def check_for_flags(self, land):
        """
        Calls all properties and methods that could raise flags.
        :param land: The PreparedGeometry for checking whether the location is over land.
        """
        a = self.tcc
        a = self.measured_dt
        a = self.elevation
        self._check_for_flags_datetime()
        self._check_for_flags_location(land)
        self._check_for_flags_obscurations()
        self._check_for_flags_ranges()

    def _check_for_flags_datetime(self):
        if self.measured_dt is not None:
            if self.measured_dt > datetime.now():
                self.flag("DF")
            if self.measured_dt.year < 1995:
                self.flag("DO")
            if self.measured_dt.hour == 0 and self.measured_dt.minute == 0:
                self.flag("DZ")

    def _check_for_flags_location(self, land):
        if self.lat is not None and self.lon is not None:
            if not land.contains(sgeom.Point(self.lon, self.lat)):
                self.flag("LW")
            if self.lat == 0. and self.lon == 0.:
                self.flag("LZ")
        else:
            self.flag("LI")

    def _check_for_flags_obscurations(self):
        if self["protocol"] == "sky_conditions":
            OBSCURATION_TYPES = ["Fog", "Smoke", "Haze", "VolcanicAsh", "Dust", "Sand", "Spray", "HeavyRain",
                                 "HeavySnow", "BlowingSnow"]
            num_obscurations = 0
            for key in OBSCURATION_TYPES:
                if self.soft_get(key) == "true":
                    num_obscurations += 1

            if num_obscurations == 2:
                self.flag("OT")
            elif num_obscurations > 2:
                self.flag("OM")

            if (num_obscurations > 0) and (self.tcc != "obscured"):
                self.flag("OO")
            elif (num_obscurations == 0) and (self.tcc == "obscured"):
                self.flag("OX")

            if ((num_obscurations > 0) or (self.tcc == "obscured")) and (len(self.cloud_types) > 0):
                self.flag("OC")

            try:
                if self.soft_get("Haze") == "true":
                    if self["SkyClarity"] != "extremely hazy":
                        self.flag("HO")
                else:
                    if self["SkyClarity"] == "extremely hazy":
                        self.flag("HC")
            except KeyError:
                pass  # self.flag("HX") TODO decide whether this flag is necessary - is SkyClarity optional?

    def _check_for_flags_ranges(self):

        if self["protocol"] == "tree_heights":
            self.check_key_in_range("TreeHeightAvgM", 0., 99., "T", -99.)

        # Check mosquito larvae count.
        if self["protocol"] == "mosquito_habitat_mapper":
            val = self.soft_get("LarvaeCount")
            if val is None:
                pass  # self.flag("MX") TODO is this optional too?
            else:
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

    flag_definitions = dict(
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
            HX="Sky clarity is missing",
            LI="Location is not a valid lat-lon pair",
            LW="Location may be over water",
            LZ="Location is at 0 N, 0 E",
            MI="Mosquito larvae count is invalid (not a number or app range)",
            MR="Mosquito larvae count (specific) outside of normal range (0 - 199)",
            MX="Mosquito larvae count attribute is missing",
            NI="Contrail count is invalid (not a number)",
            NR="Contrail count outside of normal range (0 - 19)",
            OC="Obscuration reported but cloud types also reported",
            OM="More than two obscurations reported",
            OO="Obscuration types selected but cover not obscured",
            OT="Two obscurations reported",
            OX="Obscured cover reported but obscuration type missing",
            TI="Tree height is invalid (not a number)",
            TM="Tree height is coded as missing",
            TR="Tree height outside of normal range (0m - 199m)",
            TX="Tree height attribute is missing",

            # The following flags are defined, but not yet implemented:
            PI="Protocol invalid or not yet implemented",
        )

    @property
    def flags_english(self) -> List[str]:
        """
        :returns: All flags for this observation converted to human-readable terms.
        """
        # Return the value corresponding to the key for each flag.
        return [self.flag_definitions[i] for i in self.flags]

    # def check_key(self, key, must_exist: bool = False, valid: Optional[list] = None,
    #               min: Optional[Any] = None, max: Optional[Any] = None):
    #     try:
    #         if valid is not None:
    #             return self[key] in valid
    #         else:
    #             if (min is not None) and (self[key] < min):
    #                 return False
    #             if (max is not None) and (self[key] > max):
    #                 return False
    #     except KeyError:
    #         return not must_exist
    #
    #     return True
