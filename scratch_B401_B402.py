from figure_common import *

# Settings
num_samples = 1000
latitude_bin_width = 1.0  # degrees

# Parse data
obs_all = tools.parse_csv(fp_obs_with_satellite_matches_2018)

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

for cdf in [Dataset(fp_GEOS_Jan), Dataset(fp_GEOS_Jul)]:
    # Filter out obs that have no TCC.
    obs = [ob for ob in obs_all if ob.tcc is not None]

    # Determine the start and end dates of the CDF.
    cdf_start = tools.get_cdf_datetime(cdf, 0) - timedelta(minutes=30)
    cdf_end = tools.get_cdf_datetime(cdf, -1) + timedelta(minutes=30)

    # Filter obs to only those which occur in the CDF's timeframe.
    obs = tools.filter_by_datetime(obs, earliest=cdf_start, latest=cdf_end)

    # Get GEOS coincident for each observation.
    for ob in tqdm(obs, desc="Finding GEOS coincident output for all observations"):
        try:
            i = tools.find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)
            ob.tcc_geos = float(cdf["CLDTOT"][i])
        except IndexError:
            pass

    # Filter out any obs that do not have GEOS coincident output.
    obs = [ob for ob in obs if "tcc_geos" in dir(ob)]

    lats = np.arange(-90., 90.1, latitude_bin_width)

    diff_average_histograms = []

    for _ in tqdm(range(num_samples), desc="Sampling observations"):

        sample = np.random.choice(obs, int(len(obs) / 20), False)

        # Construct lists used for scattering.
        y = [ob.lat for ob in sample]
        geos = np.array([ob.tcc_geos for ob in sample])
        globe = np.array([category_to_midpoint[ob.tcc] for ob in sample])
        diff = globe - geos

        globe_weighted_histogram, _ = np.histogram(y, lats, weights=globe)
        geos_weighted_histogram, _ = np.histogram(y, lats, weights=geos)
        diff_weighted_histogram, _ = np.histogram(y, lats, weights=diff)
        counting_histogram, _ = np.histogram(y, lats)

        # globe_average_histogram = globe_weighted_histogram / counting_histogram
        # geos_average_histogram = geos_weighted_histogram / counting_histogram
        diff_average_histogram = diff_weighted_histogram / counting_histogram

        diff_average_histograms.append(diff_average_histogram)

    diff_average_histogram_mean = np.nanmean(diff_average_histograms, axis=0)
    diff_average_histogram_stdev = np.nanstd(diff_average_histograms, axis=0, ddof=1)
    diff_average_histogram_nonzero_samples = np.sum(~np.isnan(diff_average_histograms), axis=0)
    diff_average_histogram_sem = diff_average_histogram_stdev / np.sqrt(diff_average_histogram_nonzero_samples)

    # Plot mean difference.
    ax = plotters.make_pc_fig()
    ax.barh(lats[:-1], diff_average_histogram_mean * 100., latitude_bin_width, align="edge",
            xerr=diff_average_histogram_sem * 100,
            color=["red" if val > 0 else "blue" for val in diff_average_histogram_mean])
    # ax.barh(lats[:-1], diff_average_histogram_sem * 100, latitude_bin_width, align="edge", color="green", left=-180)
    ax.set_xticks(np.arange(-100., 101., 25.))
    ax.set_xticklabels(np.arange(-1., 1.01, .25), fontdict={'fontsize': 18})
    ax.grid(axis="x", c="black")
    plt.tight_layout()
