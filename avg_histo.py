"""
Plots a geographic heatmap of the given observations.
"""
import cartopy.crs as ccrs
from cartopy.feature import LAND, OCEAN
from datetime import datetime
from globeqa import tools
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from tqdm import tqdm

fpSC_2018 = "/Users/mjstarke/Documents/GLOBE_B/GLOBE_Cloud_2018.csv"
fpGEOS_Jan = "/Users/mjstarke/Documents/GLOBE_B/G5GMAO.cldtt.201801.nc4"

obs = tools.parse_csv(fpSC_2018, count=11000)
cdf = Dataset(fpGEOS_Jan)

print("--- Filtering obs by datetime...")
obsDT = tools.filter_by_datetime(obs, latest=datetime(2018, 1, 30, 23, 59))

category_to_midpoint = dict(
    none=0.00,
    clear=0.00,
    few=0.05,
    isolated=0.175,
    scattered=0.375,
    broken=0.70,
    overcast=0.95,
    obscured=1.00,
)

# Create lists of x and y points for the observations of interest.
x = []
y = []
globe = []
geos = []
geos_binned = []

# Search through the list of observations for what can be plotted.
for ob in tqdm(obsDT, desc="Collecting observation properties"):
    if ob.lat is not None and ob.lon is not None and ob.tcc is not None:
        x.append(ob.lon)
        y.append(ob.lat)
        globe.append(category_to_midpoint[ob.tcc])
        geos_cloud_fraction = cdf["CLDTT"][tools.find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)]
        geos.append(geos_cloud_fraction)
        geos_binned.append(category_to_midpoint[tools.bin_cloud_fraction(geos_cloud_fraction)])

print("--- Histogramming...")
# Create the first numerator histogram that is the sum of all GLOBE reports in each gridbox.
histo_num_globe, xedges, yedges = np.histogram2d(x, y, [cdf["lon"][::4], cdf["lat"][::4]], weights=globe)
# Create the second numerator histogram that is the sum of all GEOS reports in each gridbox.
histo_num_geos, dummy, dummy = np.histogram2d(x, y, [cdf["lon"][::4], cdf["lat"][::4]], weights=geos)
# Create the second numerator histogram that is the sum of all GEOS reports (binned) in each gridbox.
histo_num_geos_binned, dummy, dummy = np.histogram2d(x, y, [cdf["lon"][::4], cdf["lat"][::4]], weights=geos_binned)
# Create the denominator histrogram that is the unweighted heatmap, effecitvely.
histo_den, dummy, dummy = np.histogram2d(x, y, [cdf["lon"][::4], cdf["lat"][::4]])

# Create the weighted histograms.
histo_globe = histo_num_globe / histo_den
histo_geos = histo_num_geos / histo_den
histo_geos_binned = histo_num_geos_binned / histo_den

# In order to use pcolormesh, we need to transpose the arrays.
histo_globe = histo_globe.T
histo_geos = histo_geos.T
histo_geos_binned = histo_geos_binned.T

print("--- Preparing to plot #1: GLOBE...")
# Create a figure and axis with cartopy projection.
plt.figure(figsize=(18, 9))
ax = plt.axes(projection=ccrs.PlateCarree())

# Render coastlines in grey so they don't stand out too much.
ax.coastlines(color="#aaaaaa")

# Convert the 1D lists of bin edges to 2D lists.
xx, yy = np.meshgrid(xedges, yedges)
# Plot as colormesh.
print("--- Plotting...")
pcm = ax.pcolormesh(xx, yy, histo_globe, cmap="Blues_r")

# Create colorbar with specific ticks for GLOBE TCC category bins.
plt.colorbar(pcm, ticks=[0.0, 0.1, 0.25, 0.50, 0.90, 1.0], fraction=0.025)

print("--- Filling background...")
ax.add_feature(LAND)
ax.add_feature(OCEAN)

# Set title, use the space, and show.
plt.title(r"Average cloud fraction for all GLOBE observations from 2019-Jan-01 0000Z to 2019-Jan-30 2359Z (heatmap)")
plt.tight_layout()
plt.show()
print("--- Plotting completed.")


print("--- Preparing to plot #2: GEOS...")
# Create a figure and axis with cartopy projection.
plt.figure(figsize=(18, 9))
ax = plt.axes(projection=ccrs.PlateCarree())

# Render coastlines in grey so they don't stand out too much.
ax.coastlines(color="#aaaaaa")

# Convert the 1D lists of bin edges to 2D lists.
xx, yy = np.meshgrid(xedges, yedges)
# Plot as colormesh.
print("--- Plotting...")
pcm = ax.pcolormesh(xx, yy, histo_geos, cmap="Blues_r")

# Create colorbar with specific ticks for GLOBE TCC category bins.
plt.colorbar(pcm, ticks=[0.0, 0.1, 0.25, 0.50, 0.90, 1.0], fraction=0.025)

print("--- Filling background...")
ax.add_feature(LAND)
ax.add_feature(OCEAN)

# Set title, use the space, and show.
plt.title(r"Average GEOS cloud fraction for coincident with GLOBE observations from 2019-Jan-01 0000Z to 2019-Jan-30 2359Z (heatmap)")
plt.tight_layout()
plt.show()
print("--- Plotting completed.")


print("--- Preparing to plot #3: diff...")
# Create a figure and axis with cartopy projection.
plt.figure(figsize=(18, 9))
ax = plt.axes(projection=ccrs.PlateCarree())

# Render coastlines in grey so they don't stand out too much.
ax.coastlines(color="#aaaaaa")

# Convert the 1D lists of bin edges to 2D lists.
xx, yy = np.meshgrid(xedges, yedges)
# Plot as colormesh.
print("--- Plotting...")
pcm = ax.pcolormesh(xx, yy, histo_globe - histo_geos, cmap="coolwarm")

# Create colorbar with specific ticks for GLOBE TCC category bins.
plt.colorbar(pcm, ticks=np.arange(-1.0, 1.1, 0.25), fraction=0.025)

print("--- Filling background...")
ax.add_feature(LAND)
ax.add_feature(OCEAN)

# Set title, use the space, and show.
plt.title(r"Difference of histograms (GLOBE - GEOS) from 2019-Jan-01 0000Z to 2019-Jan-30 2359Z (heatmap)")
plt.tight_layout()
plt.show()
print("--- Plotting completed.")


print("--- Preparing to plot #4: GEOS binned...")
# Create a figure and axis with cartopy projection.
plt.figure(figsize=(18, 9))
ax = plt.axes(projection=ccrs.PlateCarree())

# Render coastlines in grey so they don't stand out too much.
ax.coastlines(color="#aaaaaa")

# Convert the 1D lists of bin edges to 2D lists.
xx, yy = np.meshgrid(xedges, yedges)
# Plot as colormesh.
print("--- Plotting...")
pcm = ax.pcolormesh(xx, yy, histo_geos_binned, cmap="Blues_r")

# Create colorbar with specific ticks for GLOBE TCC category bins.
plt.colorbar(pcm, ticks=[0.0, 0.1, 0.25, 0.50, 0.90, 1.0], fraction=0.025)

print("--- Filling background...")
ax.add_feature(LAND)
ax.add_feature(OCEAN)

# Set title, use the space, and show.
plt.title(r"Average GEOS cloud fraction (B&M) coincident with GLOBE observations from 2019-Jan-01 0000Z to 2019-Jan-30 2359Z (heatmap)")
plt.tight_layout()
plt.show()
print("--- Plotting completed.")


print("--- Preparing to plot #5: diff with GEOS binned...")
# Create a figure and axis with cartopy projection.
plt.figure(figsize=(18, 9))
ax = plt.axes(projection=ccrs.PlateCarree())

# Render coastlines in grey so they don't stand out too much.
ax.coastlines(color="#aaaaaa")

# Convert the 1D lists of bin edges to 2D lists.
xx, yy = np.meshgrid(xedges, yedges)
# Plot as colormesh.
print("--- Plotting...")
pcm = ax.pcolormesh(xx, yy, histo_globe - histo_geos_binned, cmap="coolwarm")

# Create colorbar with specific ticks for GLOBE TCC category bins.
plt.colorbar(pcm, ticks=np.arange(-1.0, 1.1, 0.25), fraction=0.025)

print("--- Filling background...")
ax.add_feature(LAND)
ax.add_feature(OCEAN)

# Set title, use the space, and show.
plt.title(r"Difference of histograms (GLOBE - GEOS binned) from 2019-Jan-01 0000Z to 2019-Jan-30 2359Z (heatmap)")
plt.tight_layout()
plt.show()
print("--- Plotting completed.")