from globeqa import *
import matplotlib.pyplot as plt
import numpy as np

fpSC = "/Users/mjstarke/Documents/GLOBE_A/sky_conditions_20170101_20190531.json"

# Get obs, quality check, and filter to only those with the ER flag.
obs = tools.parse_json(fpSC)
tools.do_quality_check(obs)
obsER = tools.filter_by_flag(obs, {"ER": True})

# Create a new figure.
fig = plt.figure()
ax = fig.add_subplot(111)

# Get the list of all possible source of the data.
sources = tools.find_all_values(obs, "DataSource").keys()
# Prepare to hold a bar artist for each source.
bars = []

# Keep track of the tops of the bars of the previous histogram.
prev_histogram = None
# Go through each of the sources.
for source in sources:
    # Get the elevations from the observations that come from this source.
    elevations = [ob.elevation for ob in obsER if ob.source == source]
    # Create the histogram and retrieve the left edges of the bins.
    histogram, bin_lefts = np.histogram(elevations, np.arange(-6000., 8000.1, 250.))
    # Create a bar chart.  The last element of the bin_lefts is actually the right edge of the final bin, which we don't
    # want.  Align at edge, otherwise each bar is centered and does not accurately represent its bin.  Set the bottoms
    # of the bars, so they can be stacked, to the top of the previous histogram result.
    bar = ax.bar(bin_lefts[:-1], histogram, width=250., align="edge", bottom=prev_histogram)
    # Append this artist to the list of bars for the legend.
    bars.append(bar)
    # Set previous histogram fro the next loop.  If there was no previous histogram, just use this one; if there was,
    # add it instead.  This is necessary for stacking.
    prev_histogram = histogram if prev_histogram is None else prev_histogram + histogram

# Set titles, grid, and legend.
plt.title("Histogram of ER elevations for all sky_conditions observations from 2017-Jan-01 to 2019-May-31 (250m bin width)")
ax.set_xlabel("Elevation (m)")
ax.set_ylabel("Count")
ax.grid(axis='y')
ax.legend(bars, sources)

plt.show()
