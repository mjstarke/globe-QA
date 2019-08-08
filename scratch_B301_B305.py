# DEPRECATED: This script is deprecated by figure_S016.

from figure_common import *

obs = tools.parse_csv(fpSC_2018)
cdf = Dataset(fpGEOS_Jan)

print("--- Filtering obs by datetime...")
obs = tools.filter_by_datetime_cdf(obs, cdf, timedelta(minutes=30))

category_to_midpoint = dict(
    none=0.00,
    clear=0.00,
    few=0.05,
    isolated=0.175,
    scattered=0.375,
    broken=0.70,
    overcast=0.95,
    obscured=1.00
)


# Create lists of x and y points for the observations of interest.
x = []
y = []
globe = []
geos = []
geos_binned = []

# Search through the list of observations for what can be plotted.
for ob in tqdm(obs, desc="Binning observations"):
    if ob.lat is not None and ob.lon is not None and ob.tcc is not None:
        x.append(ob.lon)
        y.append(ob.lat)
        globe.append(category_to_midpoint[ob.tcc])
        geos_cloud_fraction = cdf["CLDTOT"][tools.find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)]
        geos.append(geos_cloud_fraction)
        geos_binned.append(category_to_midpoint[tools.bin_cloud_fraction(geos_cloud_fraction)])

reduced_lons = cdf["lon"][::4]
reduced_lats = cdf["lat"][::4]

print("--- Histogramming...")
# Create the first numerator histogram that is the sum of all GLOBE reports in each gridbox.
histo_num_globe, xedges, yedges = np.histogram2d(x, y, [reduced_lons, reduced_lats], weights=globe)
# Create the second numerator histogram that is the sum of all GEOS reports in each gridbox.
histo_num_geos, _, _ = np.histogram2d(x, y, [reduced_lons, reduced_lats], weights=geos)
# Create the second numerator histogram that is the sum of all GEOS reports (binned) in each gridbox.
histo_num_geos_binned, _, _ = np.histogram2d(x, y, [reduced_lons, reduced_lats], weights=geos_binned)
# Create the denominator histrogram that is the unweighted heatmap, effectively.
histo_den, _, _ = np.histogram2d(x, y, [reduced_lons, reduced_lats])

# Convert the 1D lists of bin edges to 2D lists.
xx, yy = np.meshgrid(xedges, yedges)

# Create the weighted histograms.
histo_globe = histo_num_globe / histo_den
histo_geos = histo_num_geos / histo_den
histo_geos_binned = histo_num_geos_binned / histo_den

# In order to use pcolormesh, we need to transpose the arrays.
histo_globe = histo_globe.T
histo_geos = histo_geos.T
histo_geos_binned = histo_geos_binned.T


ax = plotters.make_pc_fig(land_color="#999999", coast_color="#444444")
pcm = ax.pcolormesh(xx, yy, histo_globe, cmap="Blues_r", vmin=0.0, vmax=1.0)
cb = plt.colorbar(pcm, ticks=[0.0, 0.1, 0.25, 0.50, 0.90, 1.0], fraction=0.025)
cb.ax.tick_params(labelsize=18)
plt.tight_layout()


ax = plotters.make_pc_fig(land_color="#999999", coast_color="#444444")
pcm = ax.pcolormesh(xx, yy, histo_geos, cmap="Blues_r", vmin=0.0, vmax=1.0)
cb = plt.colorbar(pcm, ticks=[0.0, 0.1, 0.25, 0.50, 0.90, 1.0], fraction=0.025)
cb.ax.tick_params(labelsize=18)
plt.tight_layout()


ax = plotters.make_pc_fig(land_color="#999999", coast_color="#444444")
pcm = ax.pcolormesh(xx, yy, histo_globe - histo_geos, cmap="bwr", vmin=-1.0, vmax=1.0)
cb = plt.colorbar(pcm, ticks=np.arange(-1.0, 1.1, 0.25), fraction=0.025)
cb.ax.tick_params(labelsize=18)
plt.tight_layout()


ax = plotters.make_pc_fig(land_color="#999999", coast_color="#444444")
pcm = ax.pcolormesh(xx, yy, histo_geos_binned, cmap="Blues_r", vmin=0.0, vmax=1.0)
cb = plt.colorbar(pcm, ticks=[0.0, 0.1, 0.25, 0.50, 0.90, 1.0], fraction=0.025)
cb.ax.tick_params(labelsize=18)
plt.tight_layout()


ax = plotters.make_pc_fig(land_color="#999999", coast_color="#444444")
pcm = ax.pcolormesh(xx, yy, histo_globe - histo_geos_binned, cmap="bwr", vmin=-1.0, vmax=1.0)
cb = plt.colorbar(pcm, ticks=np.arange(-1.0, 1.1, 0.25), fraction=0.025)
cb.ax.tick_params(labelsize=18)
plt.tight_layout()
