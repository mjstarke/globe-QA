import cartopy.crs as ccrs
from globeqa import tools
import matplotlib.pyplot as plt
from tqdm import tqdm

FLAG = "LW"

fpSC = "/Users/mjstarke/Documents/GLOBE_A/sky_conditions_20170101_20190531.json"

obs = tools.parse_json(fpSC)
tools.do_quality_check(obs, tools.prepare_earth_geometry())

print("--- Filtering observations by flag...")
obsFLAGGED = tools.filter_by_flag(obs, {FLAG: True})


# Create lists of x and y points for the observations of interest.
x = []
y = []

# Search through the list of observations for what can be plotted.
print("--- Filtering observations by location validity...")
for ob in tqdm(obsFLAGGED):
    if ob.lat is not None and ob.lon is not None:
        x.append(ob.lon)
        y.append(ob.lat)

# Create a figure and axis with cartopy projection.
plt.figure(figsize=(18, 9))
ax = plt.axes(projection=ccrs.PlateCarree())

# Render coastlines in grey so they don't stand out too much.
ax.coastlines(color="#aaaaaa")

# Scatter.  Insert precise point and larger, transparent circles to indicate density.
ax.scatter(x, y, 20, marker=".", color="blue")
ax.scatter(x, y, 800, marker=".", color="blue", alpha=0.08)

# Set title, use the space, and show.
plt.title(r"Locations of all {}-flagged SC observations from 2017-Jan-01 to 2019-May-31".format(FLAG))
plt.tight_layout()
plt.show()
print("--- Plotting completed.")
