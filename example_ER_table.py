"""
Finds all observations with the ER flag, and prints a table containing the latitude, longitude, and elevation of sites
whose elevations lie outside the range -300 to 6000, and from which at least 5 observations have been made.

NOTE: If a site name contains right-to-left script (e.g., Arabic characters), that table row may print awkwardly.
"""

from globeqa import *
from figure_common import *

# Minimum number of observations a site must have for it to be considered.
minimum_observations = 5

# Download and parse observations.
fp = tools.download_from_api(["sky_conditions"], datetime(2017, 1, 1), datetime(2019, 5, 31))
obs = tools.parse_json(fp)

# ER flag is checked implicitly by checking the elevation directly - this is far quicker than running the full quality
# checker if only one flag is going to be analyzed.
obs = [ob for ob in obs if not (-300 <= ob.elevation <= 6000)]

# Create a dictionary of site=count pairs for all sites that passed the above filter.
d = tools.find_all_values(obs, "siteName")

# Print the sites.  This produces a table with 3 columns: the site name, the number of observations from that site, and
# the percentage contribution to the total.
sites = tools.pretty_print_dictionary(d, sorting="vd", compress_below=minimum_observations)

# Blank lines to separated the two tables.
print()
print()

# For each site, print its name, latitude, longitude and elevation.
for site in sites:
    obSite = [ob for ob in obs if ob["siteName"] == site]
    if len(obSite) >= minimum_observations:
        print("{:50}  {:9.4f}, {:9.4f}   {:9.2f}".format(obSite[0]["siteName"], obSite[0].lon, obSite[0].lat, obSite[0].elevation))
