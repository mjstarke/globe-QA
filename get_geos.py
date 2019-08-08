"""
Gets all coincident output from the NetCDF4 files for the observations given.
"""

from figure_common import *

obs = tools.parse_csv(fp_obs_with_satellite_matches_2017_Dec)
obs.extend(tools.parse_csv(fp_obs_with_satellite_matches_2018))
cdfs = [
    Dataset(fp_GEOS_Dec),
    Dataset(fp_GEOS_Jan),
    Dataset(fp_GEOS_Feb),
    Dataset(fp_GEOS_Jun),
    Dataset(fp_GEOS_Jul),
    Dataset(fp_GEOS_Aug)
]

# The CDF variable to use.
cdf_variable = "CLDTOT"

# For each CDF file...
for cdf in cdfs:
    # Filter obs to only those which lie in the CDF's temporal range.
    filtered_obs = tools.filter_by_datetime_cdf(obs, cdf, timedelta(minutes=30))
    # For each of those obs, find the coincident value.
    for ob in tqdm(filtered_obs, desc="Finding GEOS coincidents"):
        ob.coincident = cdf[cdf_variable][tools.find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)]

# Save a file with raw cloud cover values.
with open("geos_coincident.csv", "w") as f:
    for ob in tqdm(obs, "Writing to file"):
        try:
            f.write("{},{}\n".format(ob.id, ob.coincident))
        except AttributeError:
            pass
    f.close()

# Save a file with cloud cover categories.
with open("geos_coincident_cat.csv", "w") as f:
    for ob in tqdm(obs, "Writing to file"):
        try:
            f.write("{},{}\n".format(ob.id, tools.bin_cloud_fraction(ob.coincident)))
        except AttributeError:
            pass
    f.close()
