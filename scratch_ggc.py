import cartopy.crs as ccrs
from cartopy.feature.nightshade import Nightshade
from datetime import datetime, timedelta
from matplotlib.cm import get_cmap
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from globeqa import tools
from globeqa.observation import Observation
from tqdm import tqdm
from typing import List, Optional


def plot_ggc(t: int, obs: List[Observation], cdf: Dataset, save_path: Optional[str]) -> None:
    """
    Plots GEOS data and GLOBE observations on one plot.
    :param t: The time index to use.  The actual time will be pulled from cdf["time"].
    :param obs: The observations to plot.
    :param cdf: The NetCDF dataset to pull cloud data from.
    :param save_path: If a string, the path to which the image will be saved; the figure will not be displayed
    interactively.  If None, the plot is shown interactively.
    :return: None.  The file is saved to save_path.
    """

    # Set figure size and create an axis with a Plate-Carrée projection.
    plt.figure(figsize=(18, 9))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Render coastlines in grey so they don't stand out too much.
    ax.coastlines(color="#aaaaaa")

    # Latitude and longitude are provided as one-dimensional arrays, but they need to be 2D arrays for .contourf().
    # np.meshgrid() will create these arrays.
    xx, yy = np.meshgrid(cdf["lon"], cdf["lat"])

    # Fill-contour the cloud data.  Levels chosen are the cutoff points for GLOBE cloud cover categories.
    print("--- Plotting GEOS fill...")
    cf_sky = ax.contourf(xx, yy, cdf["CLDTT"][t], cmap="Blues_r", levels=[0.0, 0.1, 0.25, 0.5, 0.9, 1.0])

    # Add colorbar.  Ticks are as above.
    plt.colorbar(cf_sky, orientation="vertical", fraction=0.03, ticks=[0.0, 0.1, 0.25, 0.5, 0.9, 1.0])

    # Determine the beginning and end of the window for observations to be plotted.
    window_center = tools.get_cdf_datetime(cdf, t)
    window_start = window_center - timedelta(minutes=90)
    window_end = window_center + timedelta(minutes=90)

    # Create a dictionary to contain points to plot and how to plot them (marker and value for color).

    # Colormap must be retrieved directly.  If we use cmap= and c= with scatter() later, MPL assumes, for whatever
    # reason, that c is actually an RGB/A tuple, despite the presence of cmap and the inappropriate length of c for an
    # RGB/A tuple.  The only foolproof way around this is to grab the cmap directly, call it, and then wrap the result
    # in a list to create a two-dimensional array-like. Known design issue with MPL that probably won't be fixed.

    # For now, we use the cmap to get the color, and wrap it in the call to scatter().
    cmap = get_cmap("Blues_r")

    # Each entry is a specification for how a particular type of observation should be plotted.
    scatter = dict(
        none=dict(x=[], y=[], marker="P", color=cmap(0.00)),
        few=dict(x=[], y=[], marker="P", color=cmap(0.05)),
        isolated=dict(x=[], y=[], marker="P", color=cmap(0.175)),
        scattered=dict(x=[], y=[], marker="P", color=cmap(0.375)),
        broken=dict(x=[], y=[], marker="P", color=cmap(0.70)),
        overcast=dict(x=[], y=[], marker="P", color=cmap(0.95)),
        obscured=dict(x=[], y=[], marker="X", color=cmap(1.00))
    )

    # Find observations to plot.
    print("--- Searching for valid observations...")
    # Look through each observation.
    for ob in tqdm(obs):
        # Verify that the observation is plottable.
        if ob.lat is not None and ob.lon is not None and ob.measured_dt is not None and ob.tcc is not None:
            # Verify that the ob is inside the three-hour window.
            if window_end > ob.measured_dt >= window_start:
                # The first key is the cloud cover category; the second keys are x and y.
                scatter[ob.tcc]["x"].append(ob.lon)
                scatter[ob.tcc]["y"].append(ob.lat)

    # Scatter plot the GLOBE observations using the same colorscale as the filled contour.  An edge must be used
    # or the markers will blend in with the fill.  zorder is set so that the markers render over the coastlines.
    # c is given a single color wrapped in a list to prevent MPL from assuming it's an RGB/A tuple.
    print("--- Plotting valid observations...")
    # Grab each data object for each of the different categories of observations to plot.
    for k, data in scatter.items():
        # Do not plot if there is no data.
        if len(data["x"]) > 0:
            ax.scatter(data["x"], data["y"], 200, c=[data["color"]],  edgecolors="black", zorder=5,
                       marker=data["marker"])

    # Add day/night terminator.  zorder puts this on top of the scatter so that the points will have the same color as
    # the GEOS fill after being shaded.  Noinspection since the type of the first argument to Nightshade is specified
    # incorrectly.
    # noinspection PyTypeChecker
    ax.add_feature(Nightshade(window_center, alpha=0.2), zorder=20)

    # Title the plot.  Include specific timestamp of the GEOS data and the three-hour window surrounding it for the
    # observations.
    plt.title("""GEOS total cloud fraction for {} (shaded)
    GLOBE observations from {} through {} (plus marks; X marks for obscured)""".format(
        datetime.strftime(window_center, "%Y-%m-%d  %H%MZ"),
        datetime.strftime(window_start, "%Y-%m-%d  %H%MZ"),
        datetime.strftime(window_end, "%Y-%m-%d  %H%MZ")))

    print("--- Finalizing plot...")
    plt.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        plt.close()

    print("--- Plotting completed.")