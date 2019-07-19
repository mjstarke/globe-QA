from cartopy.feature.nightshade import Nightshade
from datetime import date, datetime, timedelta
from matplotlib.cm import get_cmap
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from globeqa import plotters, tools
from tqdm import tqdm


for t in tqdm(range(50), desc="Plotting GGCs"):
    path = tools.download_from_api(["sky_conditions"], date(2017, 12, 1), date(2017, 12, 31))
    obs = tools.parse_json(path)
    cdf = Dataset("/Users/mjstarke/Documents/GLOBE_B/x0037.CLDTOT.201712.nc4")

    # Set figure size and create an axis with a Plate-Carrée projection.
    ax = plotters.make_pc_fig()

    # Latitude and longitude are provided as one-dimensional arrays, but they need to be 2D arrays for .contourf().
    # np.meshgrid() will create these arrays.
    xx, yy = np.meshgrid(cdf["lon"], cdf["lat"])

    # Fill-contour the cloud data.  Levels chosen are the cutoff points for GLOBE cloud cover categories.
    print("--- Plotting GEOS fill...")
    cf_sky = ax.contourf(xx, yy, cdf["CLDTOT"][t], cmap="Blues_r", levels=[0.0, 0.1, 0.25, 0.5, 0.9, 1.0])

    # Add colorbar.  Ticks are as above.
    plt.colorbar(cf_sky, orientation="vertical", fraction=0.03, ticks=[0.0, 0.1, 0.25, 0.5, 0.9, 1.0])

    # Determine the beginning and end of the window for observations to be plotted.
    window_center = tools.get_cdf_datetime(cdf, t)
    window_start = window_center - timedelta(minutes=30)
    window_end = window_center + timedelta(minutes=30)

    # Create a dictionary to contain points to plot and how to plot them (marker and value for color).

    # Colormap must be retrieved directly.  If we use cmap= and c= with scatter() later, MPL assumes, for whatever
    # reason, that c is actually an RGB/A tuple, despite the presence of cmap and the inappropriate length of c for an
    # RGB/A tuple.  The only foolproof way around this is to grab the cmap directly, call it, and then wrap the result
    # in a list to create a two-dimensional array-like. Known design issue with MPL that probably won't be fixed.

    # For now, we use the cmap to get the color, and wrap it in the call to scatter().
    cmap = get_cmap("Blues_r")

    # Each entry is a specification for how a particular type of observation should be plotted.
    scatter = {
        None: dict(x=[], y=[], marker="X", color="brown"),
        "none": dict(x=[], y=[], marker="X", color=cmap(0.00)),
        "clear": dict(x=[], y=[], marker="P", color=cmap(0.00)),
        "few": dict(x=[], y=[], marker="P", color=cmap(0.05)),
        "isolated": dict(x=[], y=[], marker="P", color=cmap(0.175)),
        "scattered": dict(x=[], y=[], marker="P", color=cmap(0.375)),
        "broken": dict(x=[], y=[], marker="P", color=cmap(0.70)),
        "overcast": dict(x=[], y=[], marker="P", color=cmap(0.95)),
        "obscured": dict(x=[], y=[], marker="X", color=cmap(1.00))
    }

    # Filter observations to only those which lie in the one-hour window surrounding the output time.
    obs = tools.filter_by_datetime(obs, window_start, window_end, assume_chronology=False)

    # Look through each observation.
    for ob in tqdm(obs, desc="Collecting observations"):
        # The first key is the cloud cover category; the second keys are x and y.
        scatter[ob.tcc]["x"].append(ob.lon)
        scatter[ob.tcc]["y"].append(ob.lat)

    artists = []
    keys = [None, "none", "clear", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
    labels = ["null", "none", "clear", "few", "isolated", "scattered", "broken", "overcast", "obscured"]

    # Scatter plot the GLOBE observations using the same colorscale as the filled contour.  An edge must be used
    # or the markers will blend in with the fill.  zorder is set so that the markers render over the coastlines.
    # c is given a single color wrapped in a list to prevent MPL from assuming it's an RGB/A tuple.
    # Grab each data object for each of the different categories of observations to plot.
    for k, data in tqdm(scatter.items(), desc="Scattering observations"):
        # Do not plot if there is no data.
        if True:  # len(data["x"]) > 0:
            artist = ax.scatter(data["x"], data["y"], 200, c=[data["color"]], edgecolors="black", zorder=5, marker=data["marker"])
            artists.append(artist)
            labels.append(k)

    # Add day/night terminator.  zorder puts this on top of the scatter so that the points will have the same color as
    # the GEOS fill after being shaded.  Noinspection since the type of the first argument to Nightshade is specified
    # incorrectly.
    # noinspection PyTypeChecker
    ax.add_feature(Nightshade(window_center, alpha=0.2), zorder=20)

    # Title the plot.  Include specific timestamp of the GEOS data and the one-hour window surrounding it for the
    # observations.
    plt.title("""GEOS x0037 total cloud fraction for {} (shaded)
    GLOBE observations from {} through {} symbols)""".format(
        datetime.strftime(window_center, "%Y-%m-%d  %H%MZ"),
        datetime.strftime(window_start, "%Y-%m-%d  %H%MZ"),
        datetime.strftime(window_end, "%Y-%m-%d  %H%MZ")))

    ax.legend(artists, labels, loc="lower left")

    plt.tight_layout()
    plt.savefig("/Users/mjstarke/Documents/GLOBE_B/images_ggc_x0037/{:0>4.0f}.png".format(t))
    plt.close()
