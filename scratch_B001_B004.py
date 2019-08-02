# DEPRECATED: This script is superseded by figure_S016.

from scratch_vars import *

# Settings
csv_path = '/Users/mjstarke/Documents/GLOBE_B/GLOBE_Cloud_2018.csv'
cdf_path = '/Users/mjstarke/Documents/GLOBE_B/x0037.CLDTOT.201807.nc4'
num_samples = 1000

# Parse data
obs = tools.parse_csv(csv_path)
cdf = Dataset(cdf_path)

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

# Filter out obs that have no TCC.
obs = [ob for ob in obs if ob.tcc is not None]

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

diff_average_heatmaps = []

for _ in tqdm(range(num_samples), desc="Sampling observations"):

    sample = np.random.choice(obs, int(len(obs) / 20), False)

    # Construct lists used for scattering.
    x = [ob.lon for ob in sample]
    y = [ob.lat for ob in sample]
    geos = np.array([ob.tcc_geos for ob in sample])
    globe = np.array([category_to_midpoint[ob.tcc] for ob in sample])
    diff = globe - geos

    lons = np.arange(-180, 180.01, 1.25)
    lats = np.arange(-90., 90.1, 1.00)

    globe_weighted_heatmap, xedges, yedges = np.histogram2d(x, y, [lons, lats], weights=globe)
    geos_weighted_heatmap, _, _ = np.histogram2d(x, y, [lons, lats], weights=geos)
    diff_weighted_heatmap, _, _ = np.histogram2d(x, y, [lons, lats], weights=diff)
    counting_heatmap, _, _ = np.histogram2d(x, y, [lons, lats])

    globe_average_heatmap = globe_weighted_heatmap / counting_heatmap
    geos_average_heatmap = geos_weighted_heatmap / counting_heatmap
    diff_average_heatmap = diff_weighted_heatmap / counting_heatmap

    diff_average_heatmaps.append(diff_average_heatmap)

# Convert the 1D lists of bin edges to 2D lists.
xx, yy = np.meshgrid(xedges, yedges)

diff_average_heatmap_mean = np.nanmean(diff_average_heatmaps, axis=0)
diff_average_heatmap_stdev = np.nanstd(diff_average_heatmaps, axis=0)
diff_average_heatmap_nonzero_samples = np.sum(~np.isnan(diff_average_heatmaps), axis=0)
diff_average_heatmap_sem = diff_average_heatmap_stdev / np.sqrt(diff_average_heatmap_nonzero_samples)


# Plot mean difference.
fig = plt.figure(figsize=(10.5, 9))
ax = fig.add_axes([0.02, 0.02, 0.82, 0.46], projection=ccrs.PlateCarree())
ax.coastlines(color="#444444")
ax.add_feature(NaturalEarthFeature("physical", "land", "110m", facecolor="#999999", zorder=-1))
ax.add_feature(NaturalEarthFeature("physical", "ocean", "110m", facecolor="#98B6E2", zorder=-1))
ax.set_xlim(-126, -69)
ax.set_ylim(23, 51.5)
ax.pcolormesh(xx, yy, diff_average_heatmap_mean.T, cmap="bwr", vmin=-1.0, vmax=1.0)

ax = fig.add_axes([0.02, 0.52, 0.82, 0.46], projection=ccrs.PlateCarree())
ax.coastlines(color="#444444")
ax.add_feature(NaturalEarthFeature("physical", "land", "110m", facecolor="#999999", zorder=-1))
ax.add_feature(NaturalEarthFeature("physical", "ocean", "110m", facecolor="#98B6E2", zorder=-1))
ax.set_xlim(-22, 72)
ax.set_ylim(15, 62)
pcm = ax.pcolormesh(xx, yy, diff_average_heatmap_mean.T, cmap="bwr", vmin=-1.0, vmax=1.0)

ax = fig.add_axes([0.86, 0.02, 0.12, 0.96])
for s in ["left", "top", "right", "bottom"]:
    ax.spines[s].set_visible(False)
ax.set_xticks([])
ax.set_yticks([])
cb = plt.colorbar(pcm, fraction=1.0, ax=ax)
cb.ax.tick_params(labelsize=18)
plt.show()


# Plot SEM difference.
fig = plt.figure(figsize=(10.5, 9))
ax = fig.add_axes([0.02, 0.02, 0.82, 0.46], projection=ccrs.PlateCarree())
ax.coastlines(color="#444444")
ax.add_feature(NaturalEarthFeature("physical", "land", "110m", facecolor="#999999", zorder=-1))
ax.add_feature(NaturalEarthFeature("physical", "ocean", "110m", facecolor="#98B6E2", zorder=-1))
ax.set_xlim(-126, -69)
ax.set_ylim(23, 51.5)
ax.pcolormesh(xx, yy, diff_average_heatmap_sem.T, cmap="Greens", vmin=0.0, vmax=0.03)

ax = fig.add_axes([0.02, 0.52, 0.82, 0.46], projection=ccrs.PlateCarree())
ax.coastlines(color="#444444")
ax.add_feature(NaturalEarthFeature("physical", "land", "110m", facecolor="#999999", zorder=-1))
ax.add_feature(NaturalEarthFeature("physical", "ocean", "110m", facecolor="#98B6E2", zorder=-1))
ax.set_xlim(-22, 72)
ax.set_ylim(15, 62)
pcm = ax.pcolormesh(xx, yy, diff_average_heatmap_sem.T, cmap="Greens", vmin=0.0, vmax=0.03)

ax = fig.add_axes([0.86, 0.02, 0.12, 0.96])
for s in ["left", "top", "right", "bottom"]:
    ax.spines[s].set_visible(False)
ax.set_xticks([])
ax.set_yticks([])
cb = plt.colorbar(pcm, fraction=1.0, ax=ax)
cb.ax.tick_params(labelsize=18)
plt.show()

