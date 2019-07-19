from scratch_vars import *


obs = tools.parse_csv(fpSC_Dec)
obs.extend(tools.parse_csv(fpSC_2018))
cdf1 = Dataset(fpGEOS_Dec)
cdf2 = Dataset(fpGEOS_Jan)
cdf3 = Dataset(fpGEOS_Feb)
cdf4 = Dataset(fpGEOS_Jun)
cdf5 = Dataset(fpGEOS_Jul)
cdf6 = Dataset(fpGEOS_Aug)

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
