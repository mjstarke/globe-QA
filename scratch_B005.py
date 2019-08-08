# DEPRECATED: This script is superseded by figure_S019.

from figure_common import *

# Read in data.
cdf = Dataset(fp_GEOS_Jan)
obs = tools.parse_csv(fp_obs_with_satellite_matches_2018)

# Categories that GLOBE observations may take on.
categories = ["none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]

# Initialize arrays of zeroes for the counts.  GLOBE is one longer since it can contain obscured.
globe = [0] * 7
geos = [0] * 6

obs = tools.filter_by_datetime(obs, latest=tools.get_cdf_datetime(cdf, -1) + timedelta(minutes=30))

# Go through each ob that is not past the max date.
for ob in tqdm(obs, desc="Binning observations"):
    try:
        # Get the index of the bar to increment for the observation itself.
        GLOBE_index = categories.index(ob.tcc)
        # Get the coincident output of GEOS, bin it into a GLOBE category, then get the bar index.
        GEOS_fraction = cdf["CLDTOT"][tools.find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)]
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
bar1 = ax.bar(np.arange(0.2, 5.3, 1.0), globe[:-1], align="edge", width=0.3, color="purple")
bar2 = ax.bar(np.arange(0.5, 5.6, 1.0), geos, align="edge", width=0.3, color="orange")
# Plot obscured stacked on top of overcast in a different color.
bar3 = ax.bar(5.2, globe[-1], align="edge", width=0.3, bottom=globe[-2], color="#444444")

# Set various properties of the plot.
ax.set_xlabel("GLOBE cloud cover category")
ax.set_xticks(np.arange(0.5, 5.6, 1.0))
ax.set_xticklabels(categories)
ax.set_ylabel("Count")
ax.legend([bar1, bar3, bar2], ("GLOBE", "GLOBE obscured", "GEOS-5"))

plt.show()
