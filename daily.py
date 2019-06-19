"""
Downloads, parses, and quality-checks yesterday's observations.
"""

from datetime import date, timedelta
from globeqa import *
from os import chdir

# Change to desired download directory.
chdir("/Users/mjstarke/Documents/GLOBE_Daily/")

# Download yesterday's GLOBE observations.
fp = tools.download_from_api(["sky_conditions", "land_covers", "mosquito_habitat_mapper", "tree_heights"],
                             date.today() - timedelta(1), download_dest="SC_LC_MHM_TH__%S.json")

# Open and parse that file.
observations = tools.parse_json(fp)

# Perform quality checking.
land = tools.prepare_earth_geometry()
tools.do_quality_check(observations, land)

# Summarize flags.
flag_summary = tools.print_flag_summary(observations)