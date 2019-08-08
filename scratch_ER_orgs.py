"""
Finds all observations that have a negative elevation and do not come from GLOBE Observer, then prints two tables: one
containing the names of organizations that make those observations, and one contianing the sites from which those
observations are made.
"""

from figure_common import *

path = tools.download_from_api(["sky_conditions"], date(2017, 1, 1), date(2019, 7, 11))
obs = tools.parse_json(path)

obs = [ob for ob in obs if ob["DataSource"] != "GLOBE Observer App"]
obs = [ob for ob in obs if ob.elevation < 0.]

orgs = tools.find_all_values(obs, "organizationName")
sites = tools.find_all_values(obs, "siteName")

tools.pretty_print_dictionary(orgs, sorting="vd")
keys = tools.pretty_print_dictionary(sites, sorting="vd")


