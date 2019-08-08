from figure_common import *


obs = tools.parse_csv(fp_obs_with_satellite_matches_2017_Dec)
obs.extend(tools.parse_csv(fp_obs_with_satellite_matches_2018))
cdf1 = Dataset(fp_GEOS_Dec)
cdf2 = Dataset(fp_GEOS_Jan)
cdf3 = Dataset(fp_GEOS_Feb)
cdf4 = Dataset(fp_GEOS_Jun)
cdf5 = Dataset(fp_GEOS_Jul)
cdf6 = Dataset(fp_GEOS_Aug)

for cdf in [cdf1, cdf2, cdf3, cdf4, cdf5, cdf6]:
    filtered_obs = tools.filter_by_datetime_cdf(obs, cdf, timedelta(minutes=30))
    for ob in tqdm(filtered_obs, desc="Finding GEOS coincidents"):
        ob.tcc_geos = cdf["CLDTOT"][tools.find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)]

with open("geos_coincident.csv", "w") as f:
    for ob in tqdm(obs, "Writing to file"):
        try:
            f.write("{},{}\n".format(ob.id, ob.tcc_geos))
        except AttributeError:
            pass
    f.close()

with open("geos_coincident_cat.csv", "w") as f:
    for ob in tqdm(obs, "Writing to file"):
        try:
            f.write("{},{}\n".format(ob.id, tools.bin_cloud_fraction(ob.tcc_geos)))
        except AttributeError:
            pass
    f.close()
