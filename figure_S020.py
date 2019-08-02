from scratch_vars import *

num_samples = 1000

unfiltered_obs = tools.parse_csv(fpSC_Dec)
unfiltered_obs.extend(tools.parse_csv(fpSC_2018))
tools.patch_obs(unfiltered_obs, "geos_coincident_cat.csv", "tcc_geos_cat")

loops = [
    (Dataset(fpGEOS_Dec), Dataset(fpGEOS_Jan), "Dec 2017 - Jan 2018",
     ["GOES-15", "GOES-16", "METEOSAT-8", "METEOSAT-10", "HIMAWARI-8"]),
    (Dataset(fpGEOS_Jun), Dataset(fpGEOS_Jul), "Jun 2018 - Jul 2018",
     ["GOES-15", "GOES-16", "METEOSAT-8", "METEOSAT-11", "HIMAWARI-8"])
]


for loop in loops:
    cdf1, cdf2, date_range, geostationary_satellites = loop

    obs_dt = tools.filter_by_datetime(unfiltered_obs,
                                      tools.get_cdf_datetime(cdf1, 0),
                                      tools.get_cdf_datetime(cdf2, -1))

    for geostationary_satellite in geostationary_satellites:
        # Filter obs to those which have a valid GLOBE tcc, match a particular geostationary, and match either Aqua or
        # Terra.
        obs = [ob for ob in obs_dt if
               (ob.tcc is not None) and
               (ob.which_geo == geostationary_satellite) and
               (ob.tcc_geo is not None) and
               (ob.tcc_aquaterra is not None)]

        cats = {"none": 0, "few": 1, "isolated": 2, "scattered": 3, "broken": 4, "overcast": 5, "obscured": 5}

        pop_obscured = sum(1 for ob in obs if ob.tcc == "obscured")

        #################################################
        # Prepare population tally.
        pop_tally_globe = np.zeros(6)
        pop_tally_geos = np.zeros(6)
        pop_tally_aquaterra = np.zeros(6)
        pop_tally_geostationary = np.zeros(6)
        # Tally.
        for ob in obs:
            pop_tally_globe[cats[ob.tcc]] += 1
            pop_tally_geos[cats[ob["tcc_geos_cat"]]] += 1
            pop_tally_aquaterra[cats[ob.tcc_aquaterra_cat]] += 1
            pop_tally_geostationary[cats[ob.tcc_geo_cat]] += 1
        # Divide by total for proportions.
        pop_obscured /= pop_tally_globe.sum()
        pop_tally_globe /= pop_tally_globe.sum()
        pop_tally_geos /= pop_tally_geos.sum()
        pop_tally_aquaterra /= pop_tally_aquaterra.sum()
        pop_tally_geostationary /= pop_tally_geostationary.sum()

        #################################################
        # Prepare sample tallies.
        sample_tallies_globe = []
        sample_tallies_geos = []
        sample_tallies_aquaterra = []
        sample_tallies_geostationary = []

        for _ in tqdm(range(num_samples), desc="Sampling observations"):
            sample = np.random.choice(obs, int(len(obs) / 20))

            # Prepare a sample tally.
            sample_tally_globe = np.zeros(6)
            sample_tally_geos = np.zeros(6)
            sample_tally_aquaterra = np.zeros(6)
            sample_tally_geostationary = np.zeros(6)
            # Tally.
            for ob in sample:
                sample_tally_globe[cats[ob.tcc]] += 1
                sample_tally_geos[cats[ob["tcc_geos_cat"]]] += 1
                sample_tally_aquaterra[cats[ob.tcc_aquaterra_cat]] += 1
                sample_tally_geostationary[cats[ob.tcc_geo_cat]] += 1
            # Divide by total for proportions.
            sample_tally_globe /= sample_tally_globe.sum()
            sample_tally_geos /= sample_tally_geos.sum()
            sample_tally_aquaterra /= sample_tally_aquaterra.sum()
            sample_tally_geostationary /= sample_tally_geostationary.sum()
            # Add to tally list.
            sample_tallies_globe.append(sample_tally_globe)
            sample_tallies_geos.append(sample_tally_geos)
            sample_tallies_aquaterra.append(sample_tally_aquaterra)
            sample_tallies_geostationary.append(sample_tally_geostationary)

        # Get SEMs.
        sample_globe_sem = np.std(sample_tallies_globe, axis=0, ddof=1) / np.sqrt(num_samples)
        sample_geos_sem = np.std(sample_tallies_geos, axis=0, ddof=1) / np.sqrt(num_samples)
        sample_aquaterra_sem = np.std(sample_tallies_aquaterra, axis=0, ddof=1) / np.sqrt(num_samples)
        sample_geostationary_sem = np.std(sample_tallies_geostationary, axis=0, ddof=1) / np.sqrt(num_samples)


        #################################################
        fig = plt.figure(figsize=(9, 7.2))
        ax = fig.add_subplot(111)

        artists = []

        artists.append(ax.bar(np.arange(6) - 0.225, pop_tally_globe, color=std_colors["GLOBE"], width=0.15))
        artists.append(ax.bar(np.arange(6) - 0.075, pop_tally_geos, color=std_colors["GEOS"], width=0.15))
        artists.append(ax.bar(np.arange(6) + 0.075, pop_tally_aquaterra, color=std_colors["AquaTerra"], width=0.15))
        artists.append(ax.bar(np.arange(6) + 0.225, pop_tally_geostationary, color=std_colors[geostationary_satellite], width=0.15))
        artists.append(ax.bar(4.775, pop_obscured, color="#555555", hatch="//", width=0.15))

        #################################################
        ax.errorbar(np.arange(6) - 0.225, pop_tally_globe, sample_globe_sem, fmt="none", capsize=5, ecolor="black")
        ax.errorbar(np.arange(6) - 0.075, pop_tally_geos, sample_geos_sem, fmt="none", capsize=5, ecolor="black")
        ax.errorbar(np.arange(6) + 0.075, pop_tally_aquaterra, sample_aquaterra_sem, fmt="none", capsize=5, ecolor="black")
        artists.append(ax.errorbar(np.arange(6) + 0.225, pop_tally_geostationary, sample_geostationary_sem, fmt="none", capsize=5, ecolor="black"))

        #################################################
        for a in np.arange(-0.5, 5.6, 1.0):
            ax.axvline(a, color="#aaaaaa")

        #################################################
        ax.set_xlabel("Total cloud cover category")
        ax.set_xticks(np.arange(6))
        ax.set_xticklabels(["none", "few", "isolated", "scattered", "broken", "overcast + obscured"])
        ax.set_ylabel("Proportion of all values from source")
        ax.set_yticklabels(["{:.0%}".format(tick) for tick in ax.get_yticks()])
        ax.legend(artists, ["GLOBE", "GEOS", "Aqua + Terra", geostationary_satellite,
                            "Obscured observations", "Standard error"], loc="upper center")
        ax.grid(axis="y")

        ax.set_title("{} global GLOBE, GEOS, Aqua, Terra, {}\n"
                     "Cloud cover for all observations matched with {} and either Aqua or Terra\n"
                     "({} observations)\n"
                     "Standard errors estimated with {} random no-replacement samples of {} observations each"
                     "".format(date_range, geostationary_satellite, geostationary_satellite, len(obs), num_samples,
                               len(sample)))
        plt.tight_layout()
        plt.savefig("img/S020_{}_global_GLOBEvsGEOSvsAquaTerravs{}_histogram_cloud_cover.png".format(
            date_range.replace(" ", ""), geostationary_satellite))


