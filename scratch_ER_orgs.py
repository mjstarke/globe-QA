from scratch_vars import *

path = tools.download_from_api(["sky_conditions"], date(2017, 1, 1), date(2019, 7, 11))
obs = tools.parse_json(path)

obs = [ob for ob in obs if ob["DataSource"] != "GLOBE Observer App"]
obs = [ob for ob in obs if ob.elevation < 0.]

orgs = tools.find_all_values(obs, "organizationName")
sites = tools.find_all_values(obs, "siteName")

tools.pretty_print_dictionary(orgs, sorting="vd")
keys = tools.pretty_print_dictionary(sites, sorting="vd")


