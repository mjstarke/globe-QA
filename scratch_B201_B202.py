# DEPRECATED: This script is superseded by figure_S019.

from scratch_vars import *

obs = tools.parse_csv(fpSC_2018)
cdf_Jan = Dataset(fpGEOS_Jan)
cdf_Jul = Dataset(fpGEOS_Jul)
sample_count = 1000

for cdf in [cdf_Jan, cdf_Jul]:
    filtered_obs = [ob for ob in obs if ob.tcc is not None]
    filtered_obs = tools.filter_by_datetime_cdf(filtered_obs, cdf, timedelta(minutes=30))

    for ob in tqdm(filtered_obs, desc="Gathering coincident GEOS output"):
        ob.tcc_geos = cdf["CLDTOT"][tools.find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)]
        # ob.diff_from_geos = cat_to_num[ob.tcc] - ob.tcc_geos
        ob.tcc_geos_category = tools.bin_cloud_fraction(ob.tcc_geos, True)

    globe_tallies = []
    geos_tallies = []

    globe_categories = ["none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
    geos_categories = ["none", "few", "isolated", "scattered", "broken", "overcast"]

    #################################################
    for _ in tqdm(range(sample_count), desc="Sampling observations"):
        # Randomly sample 5% of all the obs.
        sample = np.random.choice(filtered_obs, int(len(filtered_obs) / 20), False)

        # Tally all the TCCs in each category.
        globe_tally = [sum(1 for ob in sample if ob.tcc == category) for category in globe_categories]
        geos_tally = [sum(1 for ob in sample if ob.tcc_geos_category == category) for category in geos_categories]

        # Press overcast and obscured into one.
        globe_tally[-2] += globe_tally[-1]
        globe_tally = globe_tally[:-1]

        globe_tallies.append(globe_tally)
        geos_tallies.append(geos_tally)

    #################################################
    globe_mean = np.mean(globe_tallies, axis=0)
    geos_mean = np.mean(geos_tallies, axis=0)
    globe_stdev = np.std(globe_tallies, axis=0)
    geos_stdev = np.std(geos_tallies, axis=0)

    #################################################
    fig = plt.figure(figsize=(10, 9))
    ax = fig.add_subplot(111)

    ax.errorbar(np.arange(6) - 0.125, globe_mean, globe_stdev, fmt="none", capsize=5, ecolor="gray")
    artists = [ax.bar(np.arange(6) - 0.125, globe_mean, color="purple", width=0.25)]

    for a in range(6):
        ax.text(a - 0.05, globe_mean[a] + globe_stdev[a], "{:.1f}\n±{:.2f}".format(globe_mean[a], globe_stdev[a]),
                ha="right", va="bottom")

    #################################################
    artists.append(ax.bar(np.arange(6) + 0.125, geos_mean, color="orange", width=0.25))
    artists.append(ax.errorbar(np.arange(6) + 0.125, geos_mean, geos_stdev, fmt="none", capsize=5, ecolor="gray"))

    for a in range(6):
        ax.text(a + 0.05, geos_mean[a] + geos_stdev[a], "{:.1f}\n±{:.2f}".format(geos_mean[a], geos_stdev[a]),
                ha="left", va="bottom")

    #################################################
    ax.set_xlabel("Total cloud cover category")
    ax.set_xticks(np.arange(6))
    ax.set_xticklabels(["none", "few", "isolated", "scattered", "broken", "overcast + obscured"])
    ax.set_ylabel("Count")
    ax.legend(artists, ["GLOBE mean", "GEOS mean", "Standard deviation"])

    plt.tight_layout()
    plt.show()
