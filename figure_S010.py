from figure_common import *

fp = tools.download_from_api(["sky_conditions"], datetime(2017, 1, 1), datetime(2019, 5, 31))
obs = tools.parse_json(fp)

# Create lists of x and y points for the observations of interest.
x = [ob.lon for ob in obs]
y = [ob.lat for ob in obs]

# Create a 2D histogram.
histo, xedges, yedges = np.histogram2d(x, y, (np.arange(-180.0, 180.1, 1.0), np.arange(-90.0, 90.1, 1.0)))
# In order to use pcolormesh, we need to transpose the array.
histo = histo.T
# Take logarithm of the array.  In this context, values naturally span multiple orders of magnitude.
histo = np.log10(histo)

# Create a figure and axis with cartopy projection.
ax = plotters.make_pc_fig()

# Convert the 1D lists of bin edges to 2D lists.
xx, yy = np.meshgrid(xedges, yedges)

# Plot as colormesh.
pcm = ax.pcolormesh(xx, yy, histo, cmap="winter_r")

# Decide what values should be labeled on the colorbar.
ticks = [1, 2, 3, 5, 10, 20, 30, 50, 100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000, int(np.power(10, np.max(histo)))]

# Create colorbar with specific ticks.  We take the log of the ticks since the data is also logarithmic.
pcmcb = plt.colorbar(pcm, ticks=np.log10(ticks), fraction=0.04)
# Create tick labels to account for the logarithmic scaling.
pcmcb.set_ticklabels(ticks)
pcmcb.ax.tick_params(labelsize=18)

ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n"
             "Distribution of GLOBE observations",
             fontdict={"fontsize": 18})

plt.tight_layout()
plt.savefig("img/S010_Jan2017-May2019_global_GLOBE-SC_heatmap_observation-distribution.png")
