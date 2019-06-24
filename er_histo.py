from globeqa import *
import numpy as np
from scratch_vars import *


# Get obs, quality check, and filter to only those with the ER flag.
obs = tools.parse_json(fpSC)
tools.do_quality_check(obs)
obsER = tools.filter_by_flag(obs, {"ER": True})

sources = tools.find_all_values(obsER, "DataSource").keys()

histograms = []
bar_lefts = None
for source in sources:
    # Get the elevations from the observations that come from this source.
    elevations = [ob.elevation for ob in obsER if ob.source == source]
    # Create the histogram and retrieve the left edges of the bins.
    histogram, bin_lefts = np.histogram(elevations, np.arange(-6000., 8000.1, 250.))
    histograms.append(histogram)
    bar_lefts = bin_lefts[:-1] if bar_lefts is None else bar_lefts

ax = plotters.stacked_bars(bar_lefts, histograms, sources, [source_color[source] for source in sources], width=250,
                           align="edge")
