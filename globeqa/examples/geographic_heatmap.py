from datetime import date
from globeqa import plotters, tools
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# Download all sky_conditions observations from May.
path = tools.download_from_api(["sky_conditions"], date(2019, 5, 1), date(2019, 5, 31))

# Parse the downloaded file.
obs = tools.parse_json(path)

# Create lists of x and y points for the observations of interest.
x = []
y = []

# Create x and y arrays for the histogram.
print("--- Filtering observations...")
for ob in tqdm(obs):
    x.append(ob.lon)
    y.append(ob.lat)

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
ticks = [1, 2, 3, 5, 10, 20, 30, 50, 100, 200, 300, 500, int(np.power(10, np.max(histo)))]

# Create colorbar with specific ticks.  We take the log of the ticks since the data is also logarithmic.
pcmcb = plt.colorbar(pcm, ticks=np.log10(ticks), fraction=0.025)
# Create tick labels to account for the logarithmic scaling.
pcmcb.set_ticklabels(ticks)

# Set title, use the space, and show.
plt.title("""Geographic distribution of GLOBE SC observations during 2019 May
in (1.00$^{o}$ x 1.00$^{o}$) bins""")

plt.tight_layout()
plt.show()
