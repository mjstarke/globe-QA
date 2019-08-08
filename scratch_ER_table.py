from globeqa import *
from figure_common import *

obs = tools.parse_json(fpSC)
tools.do_quality_check(obs)
obsER = tools.filter_by_flag(obs, {"ER": True})

d = tools.find_all_values(obsER, "siteName")

tools.pretty_print_dictionary(d, sorting="vd", compress_below=5)

for site in d.keys():
    obSite = [ob for ob in obsER if ob["siteName"] == site]
    print("{:9.4f}, {:9.4f}   {:9.2f}".format(obSite[0].lon, obSite[0].lat, obSite[0].elevation))