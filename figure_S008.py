from scratch_vars import *


# Get obs and filter to only those outside of the reasonable elevation range.
obs = tools.parse_json(fpSC)
obs = [ob for ob in obs if not (-300 <= ob.elevation <= 6000)]

sources = ["GLOBE Observer App", "GLOBE Data Entry App", "GLOBE Data Entry Web Forms"]

histograms = []
bar_lefts = None
for source in sources:
    # Get the elevations from the observations that come from this source.
    elevations = [ob.elevation for ob in obs if ob.source == source]
    # Create the histogram and retrieve the left edges of the bins.
    histogram, bin_lefts = np.histogram(elevations, np.arange(-6000., 8000.1, 250.))
    histograms.append(histogram)
    bar_lefts = bin_lefts[:-1] if bar_lefts is None else bar_lefts

ax = plotters.plot_stacked_bars(bar_lefts, histograms, sources, [std_colors[source] for source in sources], width=250,
                                align="edge")
ax.set_xlabel("Elevation (meters)")
ax.set_ylabel("Count")
ax.grid(axis="both")

ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n"
             "Elevation of observations lying outside the range -300m to 6000m")

plt.tight_layout()
plt.savefig("img/S008_Jan2017-May2019_global_GLOBE-SC_histogram_elevation.png")
