from scratch_vars import *

# Settings
num_samples = 1000
latitude_bin_width = 1.0  # degrees

# Parse data
obs_all = tools.parse_csv(fpSC_Dec)
obs_all.extend(tools.parse_csv(fpSC_2018))
tools.patch_obs(obs_all, "geos_coincident.csv", "tcc_geos", float)
# obs_all = [ob for ob in obs_all if ob.is_from_observer]  # B403a and B404a

category_to_midpoint = dict(
    none=0.00,
    clear=0.05,
    few=0.05,
    isolated=0.175,
    scattered=0.375,
    broken=0.70,
    overcast=0.95,
    obscured=1.00
)

for loop in [[Dataset(fpGEOS_Dec), Dataset(fpGEOS_Jan), "Dec 2017 - Jan 2018"],
             [Dataset(fpGEOS_Jun), Dataset(fpGEOS_Jul), "Jun 2018 - Jul 2018"]]:
    # Filter out obs that have no TCC.
    obs = [ob for ob in obs_all if ob.tcc is not None]

    cdf1, cdf2, date_range = loop

    # Determine the start and end dates of the CDF.
    cdf_start = tools.get_cdf_datetime(cdf1, 0) - timedelta(minutes=30)
    cdf_end = tools.get_cdf_datetime(cdf2, -1) + timedelta(minutes=30)

    # Filter obs to only those which occur in the CDF's timeframe.
    obs = tools.filter_by_datetime(obs, earliest=cdf_start, latest=cdf_end)

    lats = np.arange(-90., 90.1, latitude_bin_width)

    sample_average_histograms = []

    for _ in tqdm(range(num_samples), desc="Sampling observations"):

        sample = np.random.choice(obs, int(len(obs) / 20), False)

        # Construct lists used for scattering.
        y = [ob.lat for ob in sample]
        geos = np.array([ob["tcc_geos"] for ob in sample])
        globe = np.array([category_to_midpoint[ob.tcc] for ob in sample])
        diff = globe - geos

        sample_counting_histogram, _ = np.histogram(y, lats)
        sample_weighted_histogram, _ = np.histogram(y, lats, weights=diff)
        sample_average_histogram = sample_weighted_histogram / sample_counting_histogram
        sample_average_histograms.append(sample_average_histogram)

    # Calculate population average difference.
    pop_x = [ob.lon for ob in obs]
    pop_y = [ob.lat for ob in obs]
    pop_geos = np.array([ob["tcc_geos"] for ob in obs])
    pop_globe = np.array([category_to_midpoint[ob.tcc] for ob in obs])
    pop_diff = pop_globe - pop_geos
    pop_counting_histogram, _ = np.histogram(pop_y, lats)
    pop_weighted_histogram, _ = np.histogram(pop_y, lats, weights=pop_diff)
    pop_average_histogram = pop_weighted_histogram / pop_counting_histogram

    diff_average_histogram_stdev = np.nanstd(sample_average_histograms, axis=0, ddof=1)
    diff_average_histogram_nonzero_samples = np.sum(~np.isnan(sample_average_histograms), axis=0)
    diff_average_histogram_sem = diff_average_histogram_stdev / np.sqrt(diff_average_histogram_nonzero_samples)

    # Plot mean difference.
    ax = plotters.make_pc_fig(figsize=(15, 9))
    ax.barh(lats[:-1], pop_average_histogram * 100., latitude_bin_width, align="edge",
            xerr=diff_average_histogram_sem * 100,
            color=["red" if val > 0 else "blue" for val in pop_average_histogram])
    ax.set_xticks(np.arange(-100., 101., 25.))
    ax.set_xticklabels(np.arange(-1., 1.01, .25), fontdict={'fontsize': 18})
    ax.set_xlabel("Average discrepancy", fontdict={'fontsize': 18})
    ax.grid(axis="x", c="black")

    ax.set_title("{} / Global / GLOBE Clouds minus GEOS\n"
                 "Average discrepancy in cloud cover in {}-degree latitude bins"
                 "".format(date_range, latitude_bin_width), fontdict={'fontsize': 18})
    plt.tight_layout()
    plt.savefig("img/S021_{}_global_GLOBE-SCvsGEOS_bar_average-discrepancy-vs-latitude.png".format(
        date_range.replace(" ", "")))
