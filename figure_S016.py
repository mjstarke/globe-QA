from scratch_vars import *

# Settings
num_samples = 1000
lons = np.arange(-180, 180.01, 1.25)
lats = np.arange(-90., 90.1, 1.00)


# Parse data
obs_all = tools.parse_csv(fpSC_Dec)
obs_all.extend(tools.parse_csv(fpSC_2018))
loops = [
    [Dataset(fpGEOS_Dec), Dataset(fpGEOS_Jan), "Dec 2017 - Jan 2018"],
    [Dataset(fpGEOS_Jun), Dataset(fpGEOS_Jul), "Jun 2018 - Jul 2018"],
]

for loop in loops:
    cdf1, cdf2, date_range = loop

    # Filter out obs that have no TCC.
    obs = [ob for ob in obs_all if ob.tcc is not None]

    # Determine the start and end dates of the CDF.
    cdf_start = tools.get_cdf_datetime(cdf1, 0) - timedelta(minutes=30)
    cdf_end = tools.get_cdf_datetime(cdf2, -1) + timedelta(minutes=30)

    # Filter obs to only those which occur in the CDF's timeframe.
    obs = tools.filter_by_datetime(obs, earliest=cdf_start, latest=cdf_end)

    tools.patch_obs(obs, "geos_coincident.csv", "tcc_geos", float)

    sample_average_heatmaps = []

    for _ in tqdm(range(num_samples), desc="Sampling observations"):

        sample = np.random.choice(obs, int(len(obs) / 20), False)

        # Construct lists used for scattering.
        x = [ob.lon for ob in sample]
        y = [ob.lat for ob in sample]
        geos = np.array([ob["tcc_geos"] for ob in sample])
        globe = np.array([category_to_midpoint[ob.tcc] for ob in sample])
        sample_diff = globe - geos

        # Count observations in each bin.
        sample_counting_heatmap = np.histogram2d(x, y, [lons, lats])[0]
        # Again, but with weights corresponding to the differences between GLOBE and GEOS.
        sample_weighted_heatmap = np.histogram2d(x, y, [lons, lats], weights=sample_diff)[0]
        # Divide to get average difference in each bin.
        sample_average_heatmap = sample_weighted_heatmap / sample_counting_heatmap
        # Append to a list for calculating SEM later.
        sample_average_heatmaps.append(sample_average_heatmap)

    # Convert the 1D lists of bin edges to 2D arrays.
    xx, yy = np.meshgrid(lons, lats)

    # Calculate population average difference.
    x = [ob.lon for ob in obs]
    y = [ob.lat for ob in obs]
    geos = np.array([ob["tcc_geos"] for ob in obs])
    globe = np.array([category_to_midpoint[ob.tcc] for ob in obs])
    pop_diff = globe - geos
    pop_counting_heatmap = np.histogram2d(x, y, [lons, lats])[0]
    pop_weighted_heatmap = np.histogram2d(x, y, [lons, lats], weights=pop_diff)[0]
    pop_average_heatmap = pop_weighted_heatmap / pop_counting_heatmap

    # Calculate SEM.
    average_heatmap_stdev = np.nanstd(sample_average_heatmaps, axis=0, ddof=1)
    average_heatmap_nonzero_samples = np.sum(~np.isnan(sample_average_heatmaps), axis=0)
    average_heatmap_sem = average_heatmap_stdev / np.sqrt(average_heatmap_nonzero_samples)

    # Plot mean difference.
    fig = plt.figure(figsize=(10.5, 9))
    ax = fig.add_axes([0.02, 0.02, 0.82, 0.43], projection=ccrs.PlateCarree())
    ax.coastlines(color="#444444")
    ax.add_feature(NaturalEarthFeature("physical", "land", "110m", facecolor="#999999", zorder=-1))
    ax.add_feature(NaturalEarthFeature("physical", "ocean", "110m", facecolor="#98B6E2", zorder=-1))
    ax.set_xlim(-126, -69)
    ax.set_ylim(23, 51.5)
    ax.pcolormesh(xx, yy, pop_average_heatmap.T, cmap="bwr", vmin=-1.0, vmax=1.0)

    ax = fig.add_axes([0.02, 0.49, 0.82, 0.43], projection=ccrs.PlateCarree())
    ax.coastlines(color="#444444")
    ax.add_feature(NaturalEarthFeature("physical", "land", "110m", facecolor="#999999", zorder=-1))
    ax.add_feature(NaturalEarthFeature("physical", "ocean", "110m", facecolor="#98B6E2", zorder=-1))
    ax.set_xlim(-22, 72)
    ax.set_ylim(15, 62)
    pcm = ax.pcolormesh(xx, yy, pop_average_heatmap.T, cmap="bwr", vmin=-1.0, vmax=1.0)

    ax.set_title(date_range + " regional GLOBE minus GEOS\n"
                 "Average cloud cover discrepancy",
                 fontdict={"fontsize": 18})

    ax = fig.add_axes([0.86, 0.02, 0.12, 0.96])
    for s in ["left", "top", "right", "bottom"]:
        ax.spines[s].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    cb = plt.colorbar(pcm, fraction=1.0, ax=ax)
    cb.ax.tick_params(labelsize=18)

    plt.tight_layout()
    plt.savefig("img/S016_{}_CONUS-Europe-MiddleEast_GLOBE-SCvGEOS_heatmap_average-discrepancy.png".format(
        date_range.replace(" ", "")))


    # Plot SEM difference.
    fig = plt.figure(figsize=(10.5, 9))
    ax = fig.add_axes([0.02, 0.02, 0.82, 0.43], projection=ccrs.PlateCarree())
    ax.coastlines(color="#444444")
    ax.add_feature(NaturalEarthFeature("physical", "land", "110m", facecolor="#999999", zorder=-1))
    ax.add_feature(NaturalEarthFeature("physical", "ocean", "110m", facecolor="#98B6E2", zorder=-1))
    ax.set_xlim(-126, -69)
    ax.set_ylim(23, 51.5)
    ax.pcolormesh(xx, yy, average_heatmap_sem.T, cmap="Greens", vmin=0.0, vmax=0.05)

    ax = fig.add_axes([0.02, 0.49, 0.82, 0.43], projection=ccrs.PlateCarree())
    ax.coastlines(color="#444444")
    ax.add_feature(NaturalEarthFeature("physical", "land", "110m", facecolor="#999999", zorder=-1))
    ax.add_feature(NaturalEarthFeature("physical", "ocean", "110m", facecolor="#98B6E2", zorder=-1))
    ax.set_xlim(-22, 72)
    ax.set_ylim(15, 62)
    pcm = ax.pcolormesh(xx, yy, average_heatmap_sem.T, cmap="Greens", vmin=0.0, vmax=0.05)

    ax.set_title(date_range + " regional GLOBE minus GEOS\n"
                 "Standard error of the average cloud cover discrepancy",
                 fontdict={"fontsize": 18})

    ax = fig.add_axes([0.86, 0.02, 0.12, 0.96])
    for s in ["left", "top", "right", "bottom"]:
        ax.spines[s].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    cb = plt.colorbar(pcm, fraction=1.0, ax=ax)
    cb.ax.tick_params(labelsize=18)

    plt.tight_layout()
    plt.savefig("img/S016_{}_CONUS-Europe-MiddleEast_GLOBE-SCvGEOS_heatmap_stderr-average-discrepancy.png".format(
        date_range.replace(" ", "")))
