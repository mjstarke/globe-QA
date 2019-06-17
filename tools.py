from datetime import datetime, time, timezone, timedelta
from observation import Observation
from pprint import PrettyPrinter
from typing import List, Dict, Optional, Union


def pp(obj):
    PrettyPrinter(indent=4).pprint(obj)


def calc_local_midnight_UTC_offset(lon: float):
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
