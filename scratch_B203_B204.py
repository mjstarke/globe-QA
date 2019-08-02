from scratch_vars import *

obs = tools.parse_csv(fpSC_Dec)
obs.extend(tools.parse_csv(fpSC_2018))
obs = [ob for ob in obs if ob.tcc is not None]
tools.patch_obs(obs, "geos_coincident_cat.csv", "tcc_geos_cat")

loops = [
    [Dataset(fpGEOS_Dec), Dataset(fpGEOS_Jan), "Dec 2017 - Jan 2018"],
    [Dataset(fpGEOS_Jun), Dataset(fpGEOS_Jul), "Jun 2018 - Jul 2018"],
]

for loop in loops:

    cdf1, cdf2, date_range = loop

    filtered_obs = tools.filter_by_datetime(
        obs,
        tools.get_cdf_datetime(cdf1, 0) - timedelta(minutes=30),
        tools.get_cdf_datetime(cdf2, -1) + timedelta(minutes=30)
    )

    globe_tallies = []
    geos_tallies = []
    aqua_tallies = []
    terra_tallies = []
    geo_tallies = []

    globe_categories = ["none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
    geos_categories = ["none", "few", "isolated", "scattered", "broken", "overcast"]

    #################################################
    for _ in tqdm(range(sample_count), desc="Sampling observations"):
        # Randomly sample 5% of all the obs.
        sample = np.random.choice(filtered_obs, int(len(filtered_obs) / 20), False)

        # Tally all the TCCs in each category.
        globe_tally = [sum(1 for ob in sample if ob.tcc == category) for category in globe_categories]
        geos_tally = [sum(1 for ob in sample if ob["tcc_geos_cat"] == category) for category in geos_categories]
        aqua_tally = [sum(1 for ob in sample if ob.tcc_aqua_cat == category) for category in geos_categories]
        terra_tally = [sum(1 for ob in sample if ob.tcc_terra_cat == category) for category in geos_categories]
        geo_tally = [sum(1 for ob in sample if ob.tcc_geo_cat == category) for category in geos_categories]

        # Press overcast and obscured into one.
        globe_tally[-2] += globe_tally[-1]
        globe_tally = globe_tally[:-1]

        # Convert to arrays.
        globe_tally = np.array(globe_tally)
        geos_tally = np.array(geos_tally)
        aqua_tally = np.array(aqua_tally)
        terra_tally = np.array(terra_tally)
        geo_tally = np.array(geo_tally)

        # Divide by sum to get percentages.
        globe_tally = globe_tally / globe_tally.sum()
        geos_tally = geos_tally / geos_tally.sum()
        aqua_tally = aqua_tally / aqua_tally.sum()
        terra_tally = terra_tally / terra_tally.sum()
        geo_tally = geo_tally / geo_tally.sum()

        globe_tallies.append(globe_tally)
        geos_tallies.append(geos_tally)
        aqua_tallies.append(aqua_tally)
        terra_tallies.append(terra_tally)
        geo_tallies.append(geo_tally)

    #################################################
    pop_globe_tally = [sum(1 for ob in filtered_obs if ob.tcc == category) for category in globe_categories]
    pop_geos_tally = [sum(1 for ob in filtered_obs if ob["tcc_geos_cat"] == category) for category in geos_categories]
    pop_aqua_tally = [sum(1 for ob in filtered_obs if ob.tcc_aqua_cat == category) for category in geos_categories]
    pop_terra_tally = [sum(1 for ob in filtered_obs if ob.tcc_terra_cat == category) for category in geos_categories]
    pop_geo_tally = [sum(1 for ob in filtered_obs if ob.tcc_geo_cat == category) for category in geos_categories]

    pop_globe_tally[-2] += pop_globe_tally[-1]
    pop_globe_tally = pop_globe_tally[:-1]

    pop_globe_tally = np.array(pop_globe_tally)
    pop_geos_tally = np.array(pop_geos_tally)
    pop_aqua_tally = np.array(pop_aqua_tally)
    pop_terra_tally = np.array(pop_terra_tally)
    pop_geo_tally = np.array(pop_geo_tally)

    pop_globe_tally = pop_globe_tally / pop_globe_tally.sum()
    pop_geos_tally = pop_geos_tally / pop_geos_tally.sum()
    pop_aqua_tally = pop_aqua_tally / pop_aqua_tally.sum()
    pop_terra_tally = pop_terra_tally / pop_terra_tally.sum()
    pop_geo_tally = pop_geo_tally / pop_geo_tally.sum()

    globe_stdev = np.std(globe_tallies, axis=0)
    geos_stdev = np.std(geos_tallies, axis=0)
    aqua_stdev = np.std(aqua_tallies, axis=0)
    terra_stdev = np.std(terra_tallies, axis=0)
    geo_stdev = np.std(geo_tallies, axis=0)

    #################################################
    fig = plt.figure(figsize=(8, 7.2))
    ax = fig.add_subplot(111)

    artists = []

    artists.append(ax.bar(np.arange(6) - 0.3, pop_globe_tally, color="purple", width=0.15))
    artists.append(ax.bar(np.arange(6) - 0.15, pop_geos_tally, color="orange", width=0.15))
    artists.append(ax.bar(np.arange(6) + 0.0, pop_aqua_tally, color="#6666ff", width=0.15))
    artists.append(ax.bar(np.arange(6) + 0.15, pop_terra_tally, color="#55ff00", width=0.15))
    artists.append(ax.bar(np.arange(6) + 0.3, pop_geo_tally, color="grey", width=0.15))

    #################################################
    ax.errorbar(np.arange(6) - 0.3, pop_globe_tally, globe_stdev, fmt="none", capsize=5, ecolor="black")
    ax.errorbar(np.arange(6) - 0.15, pop_geos_tally, geos_stdev, fmt="none", capsize=5, ecolor="black")
    ax.errorbar(np.arange(6) + 0.0, pop_aqua_tally, aqua_stdev, fmt="none", capsize=5, ecolor="black")
    artists.append(ax.errorbar(np.arange(6) + 0.15, pop_terra_tally, terra_stdev, fmt="none", capsize=5, ecolor="black"))
    ax.errorbar(np.arange(6) + 0.3, pop_geo_tally, geo_stdev, fmt="none", capsize=5, ecolor="black")

    #################################################
    for a in np.arange(-0.5, 5.6, 1.0):
        ax.axvline(a, color="#aaaaaa")

#################################################
ax.set_xlabel("Total cloud cover category")
ax.set_xticks(np.arange(6))
ax.set_xticklabels(["none", "few", "isolated", "scattered", "broken", "overcast + obscured"])
ax.set_ylabel("Proportion")
ax.set_yticklabels(["{:.0%}".format(tick) for tick in ax.get_yticks()])
ax.legend(artists, ["GLOBE", "GEOS", "Aqua", "Terra", "Geostationaries", "Standard deviation"], loc="upper center")
ax.grid(axis="y")

    ax.set_title("{} global GLOBE\nDistribution of cloud cover".format(date_range))
    plt.tight_layout()
    plt.savefig("img/S019_{}_global_GLOBE_scattermap_dust_observations.png".format(date_range.replace(" ", "")))
