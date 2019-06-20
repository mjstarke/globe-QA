from datetime import datetime
from globeqa import tools
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from tqdm import tqdm

fpSC_2018 = "/Users/mjstarke/Documents/GLOBE_B/GLOBE_Cloud_2018.csv"
fpGEOS_Jan = "/Users/mjstarke/Documents/GLOBE_B/G5GMAO.cldtt.201801.nc4"

# Read in data.
cdf = Dataset(fpGEOS_Jan)
obs = tools.parse_csv(fpSC_2018)

# Categories that GLOBE observations may take on.
categories = ["none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]

# Initialize arrays of zeroes for the counts.  GLOBE is one longer since it can contain obscured.
globe = [0] * 7
geos = [0] * 6
# Final date to consider.  GEOS data doesn't extend beyond this point.
max_date = datetime(2018, 2, 1)
# Keep track of the last ob to consider.
last_ob = 0

# Find the last ob to consider.
print("--- Finding stop point...")
for o in range(len(obs)):
    ob = obs[o]
    if ob.measured_dt >= max_date:
        last_ob = o
        break

print("--- Binning observations...")
# Go through each ob that is not past the max date.
for ob in tqdm(obs[:last_ob]):
    # If the ob is valid...
    if ob.tcc and ob.lat and ob.lon:
        # Find the gridbox in GOES that corresponds to it.
        k, j, i = tools.find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)
        try:
            # Get the index of the bar to increment for the observation itself.
            GLOBE_index = categories.index(ob.tcc)
            # Get the coincident output of GEOS, bin it into a GLOBE category, then get the bar index.
            GEOS_fraction = cdf["CLDTT"][k, j, i]
            GEOS_category = tools.bin_cloud_fraction(GEOS_fraction)
            GEOS_index = categories.index(GEOS_category)
            # Increment both respective bars if that succeeds.
            globe[GLOBE_index] += 1
            geos[GEOS_index] += 1

        # ValueError indicates that the observation had an invalid cloud cover (usually -99).  Skip this ob.
        except ValueError:
            pass
        # IndexError indicates that we have moved beyond the temporal range of the GEOS data. Terminate loop, as all
        # following obs will be even later.
        except IndexError:
            break

# Create a figure.
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)

# Plot bars.
bar1 = ax.bar(np.arange(0.2, 5.3, 1.0), globe[:-1], align="edge", width=0.3, color="red")
bar2 = ax.bar(np.arange(0.5, 5.6, 1.0), geos, align="edge", width=0.3, color="orange")
# Plot obscured stacked on top of overcast in a different color.
bar3 = ax.bar(5.2, globe[-1], align="edge", width=0.3, bottom=globe[-2], color="#444444")

# Set various properties of the plot.
plt.title("Frequency of total cloud cover categories and associated coincident GEOS output")
ax.set_xlabel("GLOBE cloud cover category")
ax.set_xticks(np.arange(0.5, 5.6, 1.0))
ax.set_xticklabels(categories)
ax.set_ylabel("Count")
ax.legend([bar1, bar3, bar2], ("GLOBE", "GLOBE obscured", "GEOS-5"))

plt.show()


# Create another figure.
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111)

# Add overcast to obscured for the GLOBE values, then chop off the obscured point so that we have a len-6 array.
globe[-2] += globe[-1]
globe = globe[:-1]
categories[5] += " + obscured"

# Plot the difference.
bar1 = ax.bar(np.arange(0.5, 5.6, 1.0), np.array(globe) - np.array(geos), width=0.5, color="#00aaaa")

# Set various properties of the plot.
plt.title("Frequency of total cloud cover categories for GLOBE observations minus all associated coincident GOES output")
ax.set_xlabel("GLOBE cloud cover category")
ax.set_xticks(np.arange(0.5, 5.6, 1.0))
ax.set_xticklabels(categories)
ax.set_ylabel("Difference")
ax.grid(axis="y")

plt.show()
