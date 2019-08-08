# DEPRECATED: This script produces figures with no statistical significance, as it attempts to compare the domains of
# different geostationaries.

from figure_common import *

obs = tools.parse_csv(fp_obs_with_satellite_matches_2017_Dec)
obs.extend(tools.parse_csv(fp_obs_with_satellite_matches_2018))
cdf1, cdf2 = Dataset(fp_GEOS_Dec), Dataset(fp_GEOS_Jan)  # B211
# cdf1, cdf2 = Dataset(fpGEOS_Jun), Dataset(fpGEOS_Jul)  # B212
sample_count = 1000

filtered_obs = [ob for ob in obs if ob.tcc is not None]
filtered_obs = tools.filter_by_datetime(
    filtered_obs,
    tools.get_cdf_datetime(cdf1, 0) - timedelta(minutes=30),
    tools.get_cdf_datetime(cdf2, -1) + timedelta(minutes=30)
)

goes15_tallies = []
goes16_tallies = []
himawari_tallies = []
meteosat8_tallies = []
meteosat10_11_tallies = []

tcc_categories = ["none", "few", "isolated", "scattered", "broken", "overcast"]

#################################################
for _ in tqdm(range(sample_count), desc="Sampling observations"):
    # Randomly sample 5% of all the obs.
    sample = np.random.choice(filtered_obs, int(len(filtered_obs) / 20), False)

    # Tally all the TCCs in each category.
    goes15_tally = [sum(1 for ob in sample if ob.which_geo == "GOES-15" and ob.tcc_geo_cat == category) for category in tcc_categories]
    goes16_tally = [sum(1 for ob in sample if ob.which_geo == "GOES-16" and ob.tcc_geo_cat == category) for category in tcc_categories]
    himawari_tally = [sum(1 for ob in sample if ob.which_geo == "HIMAWARI-8" and ob.tcc_geo_cat == category) for category in tcc_categories]
    meteosat8_tally = [sum(1 for ob in sample if ob.which_geo == "METEOSAT-8" and ob.tcc_geo_cat == category) for category in tcc_categories]
    meteosat10_11_tally = [sum(1 for ob in sample if ob.which_geo == "METEOSAT-11" and ob.tcc_geo_cat == category) for category in tcc_categories]

    # Convert to arrays.
    goes15_tally = np.array(goes15_tally)
    goes16_tally = np.array(goes16_tally)
    himawari_tally = np.array(himawari_tally)
    meteosat8_tally = np.array(meteosat8_tally)
    meteosat10_11_tally = np.array(meteosat10_11_tally)

    # Divide by sum to get percentages.
    goes15_tally = goes15_tally / goes15_tally.sum()
    goes16_tally = goes16_tally / goes16_tally.sum()
    himawari_tally = himawari_tally / himawari_tally.sum()
    meteosat8_tally = meteosat8_tally / meteosat8_tally.sum()
    meteosat10_11_tally = meteosat10_11_tally / meteosat10_11_tally.sum()

    goes15_tallies.append(goes15_tally)
    goes16_tallies.append(goes16_tally)
    himawari_tallies.append(himawari_tally)
    meteosat8_tallies.append(meteosat8_tally)
    meteosat10_11_tallies.append(meteosat10_11_tally)

#################################################
pop_goes15_tally = [sum(1 for ob in filtered_obs if ob.which_geo == "GOES-15" and ob.tcc_geo_cat == category) for category in tcc_categories]
pop_goes16_tally = [sum(1 for ob in filtered_obs if ob.which_geo == "GOES-16" and ob.tcc_geo_cat == category) for category in tcc_categories]
pop_himawari_tally = [sum(1 for ob in filtered_obs if ob.which_geo == "HIMAWARI-8" and ob.tcc_geo_cat == category) for category in tcc_categories]
pop_meteosat8_tally = [sum(1 for ob in filtered_obs if ob.which_geo == "METEOSAT-8" and ob.tcc_geo_cat == category) for category in tcc_categories]
pop_meteosat10_11_tally = [sum(1 for ob in filtered_obs if ob.which_geo == "METEOSAT-11" and ob.tcc_geo_cat == category) for category in tcc_categories]

pop_goes15_tally = np.array(pop_goes15_tally)
pop_goes16_tally = np.array(pop_goes16_tally)
pop_himawari_tally = np.array(pop_himawari_tally)
pop_meteosat8_tally = np.array(pop_meteosat8_tally)
pop_meteosat10_11_tally = np.array(pop_meteosat10_11_tally)

pop_goes15_tally = pop_goes15_tally / pop_goes15_tally.sum()
pop_goes16_tally = pop_goes16_tally / pop_goes16_tally.sum()
pop_himawari_tally = pop_himawari_tally / pop_himawari_tally.sum()
pop_meteosat8_tally = pop_meteosat8_tally / pop_meteosat8_tally.sum()
pop_meteosat10_11_tally = pop_meteosat10_11_tally / pop_meteosat10_11_tally.sum()

goes15_sem = np.std(goes15_tallies, axis=0, ddof=1) / np.sqrt(sample_count)
goes16_sem = np.std(goes16_tallies, axis=0, ddof=1) / np.sqrt(sample_count)
himawari_sem = np.std(himawari_tallies, axis=0, ddof=1) / np.sqrt(sample_count)
meteosat8_sem = np.std(meteosat8_tallies, axis=0, ddof=1) / np.sqrt(sample_count)
meteosat10_11_sem = np.std(meteosat10_11_tallies, axis=0, ddof=1) / np.sqrt(sample_count)

#################################################
fig = plt.figure(figsize=(8, 7.2))
ax = fig.add_subplot(111)

artists = [ax.bar(np.arange(6) - 0.3, pop_goes15_tally, color="#004400", width=0.15),
           ax.bar(np.arange(6) - 0.15, pop_goes16_tally, color="#228822", width=0.15),
           ax.bar(np.arange(6) + 0.0, pop_himawari_tally, color="#ff69b4", width=0.15),
           ax.bar(np.arange(6) + 0.15, pop_meteosat8_tally, color="#771111", width=0.15),
           ax.bar(np.arange(6) + 0.3, pop_meteosat10_11_tally, color="#cc4444", width=0.15),
           ax.errorbar(np.arange(6) + 0.15, pop_meteosat8_tally, meteosat8_sem, fmt="none", capsize=5, ecolor="black")]

#################################################
ax.errorbar(np.arange(6) - 0.3, pop_goes15_tally, goes15_sem, fmt="none", capsize=5, ecolor="black")
ax.errorbar(np.arange(6) - 0.15, pop_goes16_tally, goes16_sem, fmt="none", capsize=5, ecolor="black")
ax.errorbar(np.arange(6) + 0.0, pop_himawari_tally, himawari_sem, fmt="none", capsize=5, ecolor="black")
ax.errorbar(np.arange(6) + 0.3, pop_meteosat10_11_tally, meteosat10_11_sem, fmt="none", capsize=5, ecolor="black")

#################################################
for a in np.arange(-0.5, 5.6, 1.0):
    ax.axvline(a, color="#aaaaaa")

#################################################
ax.set_xlabel("Total cloud cover category")
ax.set_xticks(np.arange(6))
ax.set_xticklabels(["none", "few", "isolated", "scattered", "broken", "overcast + obscured"])
ax.set_ylabel("Proportion")
ax.set_yticklabels(["{:.0%}".format(tick) for tick in ax.get_yticks()])
ax.legend(artists, ["GOES-15", "GOES-16", "HIMAWARI-8", "METEOSAT-8", "METEOSAT-11", "Standard error"], loc="upper center")
ax.grid(axis="y")

plt.tight_layout()
plt.show()
