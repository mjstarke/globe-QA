import cartopy.crs as ccrs
from cartopy.feature.nightshade import Nightshade
from cartopy.feature import LAND, OCEAN
from datetime import datetime, timedelta
from matplotlib.cm import get_cmap
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from globeqa.observation import Observation
from globeqa.tools import find_closest_gridbox, get_cdf_datetime
from tqdm import tqdm
from typing import List, Optional, Tuple


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
    window_center = get_cdf_datetime(cdf, t)
    window_start = window_center - timedelta(minutes=90)
    window_end = window_center + timedelta(minutes=90)

    # Create a dictionary to contain points to plot and how to plot them (marker and value for color).

    # Colormap must be retreived directly.  If we use cmap= and c= with scatter() later, MPL assumes, for whatever
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


def plot_geo_hm(obs: List[Observation], cdf: Dataset, save_path: Optional[str]):
    """
    Plots a geographic heatmap of the given observations.
    :param obs: The observations to plot.
    :param cdf: The NetCDF dataset that contains the lat/lons.
    :param save_path: If a string, the path to which the image will be saved; the figure will not be displayed
    interactively.  If None, the plot is shown interactively.
    """

    # Create lists of x and y points for the observations of interest.
    x = []
    y = []

    # Search through the list of observations for what can be plotted.
    print("--- Filtering observations...")
    for ob in tqdm(obs):
        if ob.lat is not None and ob.lon is not None:
            x.append(ob.lon)
            y.append(ob.lat)

    # Create a 2D histogram.  Bin edges shouldn't be every lon and lat, as that would make bins too small (hence ::4).
    histo, xedges, yedges = np.histogram2d(x, y, [cdf["lon"][::4], cdf["lat"][::4]])
    # In order to use pcolormesh, we need to transpose the array.
    histo = histo.T
    # Take logarithm of the array.  Values naturally span multiple orders of magnitude.
    histo = np.log10(histo)

    # Create a figure and axis with cartopy projection.
    plt.figure(figsize=(18, 9))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Render coastlines in grey so they don't stand out too much.
    ax.coastlines(color="#aaaaaa")

    # Convert the 1D lists of bin edges to 2D lists.
    xx, yy = np.meshgrid(xedges, yedges)
    # Plot as colormesh.
    pcm = ax.pcolormesh(xx, yy, histo, cmap="plasma_r")

    # Decide what values should be labeled on the colorbar.
    highest = np.max(histo)
    if highest > 500:
        ticks = [1, 10, 100, 1000, 10000, 100000, 1000000]
    elif highest > 50:
        ticks = [1, 10, 50, 100, 500]
    else:
        ticks = [1, 3, 5, 10, 25, 50]

    # Create colorbar with specific ticks.  We take the log of the ticks since the data is also logarithmic.
    pcmcb = plt.colorbar(pcm, ticks=np.log10(ticks), fraction=0.025)
    # Create tick labels to account for the logarithmic scaling.
    pcmcb.set_ticklabels(ticks)

    # Set title, use the space, and show.
    plt.title(r"Geographic distribution of GLOBE cloud observations in 2018, in (1.25$^{o}$ x 1.00$^{o}$) bins (logarithmic fill)")

    print("--- Finalizing plot...")
    plt.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        plt.close()

    print("--- Plotting completed.")


def plot_cat_hm(obs, cdf, save_path: Optional[str] = None, progress=1000):
    histo = np.zeros((7, 6))

    obs_categories = ["obscured", "overcast", "broken", "scattered", "isolated", "few", "none"]
    geos_thresholds = [0.01, 0.10, 0.25, 0.50, 0.90, 1.00]
    geos_categories = ["clear", "few", "isolated", "scattered", "broken", "overcast"]

    print("--- Histogramming observations...")
    for o in tqdm(range(len(obs))):
        ob = obs[o]
        if ob.tcc is not None and ob.lat is not None and ob.lon is not None and ob.measured_dt is not None:
            # Get the index of the observation's tcc.
            x = obs_categories.index(ob.tcc)

            # Get the GEOS tcc at the observation.
            try:
                geos_tcc = cdf["CLDTT"][find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)]
                for t in range(len(geos_thresholds)):
                    if geos_tcc <= geos_thresholds[t]:
                        y = t
                        break
            except IndexError:
                break

            # Update the histogram.
            histo[x, y] += 1

        if o % progress == 0:
            print("--  Histogrammed {} observations...".format(o))

    print("--- Readying plot...")
    # Set up a figure and axis.
    fig, ax = plt.subplots()
    ax.imshow(histo, cmap="summer_r")

    # Specifically show all ticks.
    ax.set_xticks(np.arange(len(geos_categories)))
    ax.set_yticks(np.arange(len(obs_categories)))

    # Label each ticks with the appropriate categories.
    ax.set_xticklabels(geos_categories)
    ax.set_yticklabels(obs_categories)

    # Label the axes.
    ax.set_xlabel("GEOS equivalent TCC category")
    ax.set_ylabel("GLOBE observation TCC category")

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(obs_categories)):
        for j in range(len(geos_categories)):
            ax.text(j, i, int(histo[i, j]), ha="center", va="center", color="k")

    ax.set_title("GEOS vs. GLOBE total cloud cover (TCC) at GLOBE observation sites for 2018")
    fig.tight_layout()

    print("--- Finalizing plot...")
    plt.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        plt.close()

    print("--- Plotting completed.")


def plot_tcc_scatter(obs, cdf, save_path: Optional[str] = None, progress=1000):
    x = []
    y = []
    obs_categories = ["none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
    obs_values = [0.00, 0.05, 0.175, 0.375, 0.70, 0.95, 1.00]

    print("--- Processing observations for scatterplot...")
    for o in tqdm(range(len(obs))):
        ob = obs[o]
        if ob.tcc is not None and ob.lat is not None and ob.lon is not None and ob.measured_dt is not None:
            # Get the index of the observation's tcc.
            x.append(obs_values[obs_categories.index(ob.tcc)])

            # Get the GEOS tcc at the observation.
            try:
                y.append(cdf["CLDTT"][find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)])
            except IndexError:
                x = x[:-1]
                break

        if o % progress == 0:
            print("--  Processed {} observations...".format(o))

    fig = plt.figure(figsize=(13.5, 9))
    ax = fig.add_subplot(111)

    ax.scatter(x, y, marker="+")

    ax.set_xticks(obs_values)
    ax.set_xticklabels(obs_categories)
    ax.set_yticks(obs_values)

    print("--- Finalizing plot...")
    plt.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        plt.close()

    print("--- Plotting completed.")


def fig_pc(figsize: Tuple[float, float] = (18, 9), coast_color: str = "#aaaaaa", color_bg: bool = True):
    """
    Creates a cartopy figure using the PlateCarree projection.
    :param figsize: The size of the figure for matplotlib (usually in inches).  Default (18, 9).
    :param coast_color: The color of the coastlines.  Default '#aaaaaa' (light grey).
    :param color_bg: Whether to color the background (blue for ocean, orange for land).  Default True.
    :return: The axis for the figure.
    """
    # Create a figure and axis with cartopy projection.
    plt.figure(figsize=figsize)
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Render coastlines in grey so they don't stand out too much.
    ax.coastlines(color=coast_color)

    if color_bg:
        ax.add_feature(LAND)
        ax.add_feature(OCEAN)

    return ax


def annotated_heatmap(data: np.ndarray, x_ticks: List[str], y_ticks: List[str], save_path: Optional[str] = None,
                      text_formatter: str = "{:.0f}", text_color: str = "white", high_text_color: str = "black",
                      text_color_threshold: float = np.inf, **kwargs):
    """
    Creates a simple annotated heatmap.
    :param data: A two-dimensional array of data for which to create a heatmap.  It will be automatically transposed for
    imshow().
    :param x_ticks: The list of tick labels along the x axis.  Must have length data.shape[0].
    :param y_ticks: The list of tick labels along the y axis.  Must have length data.shape[1].
    :param save_path: If None, the plot will be shown interactively.  If a file path, the plot will instead be saved to
    that location.  Defualt None.
    :param text_formatter: The format string for the annotations.  Default '{:.0f}', which produces integers.
    :param text_color: The color for the cell labels.  Default 'white'.
    :param high_text_color: The color for the cell labels if the corresponding value is greater than
    text_color_threshold. Default 'black'.
    :param text_color_threshold: The threshold at which to switch from text_color to high_text_color.  Default np.inf
    (which means that text_color is used everywhere).
    :param kwargs: kwargs are passed to imshow().
    :return: The axis of the drawn plot.
    :raises: ValueError if data is not 2-dimensional, or if lengths of x_ticks and y_ticks do not match data.shape.
    """
    if len(data.shape) != 2:
        raise ValueError("'data' must be two-dimensional.")
    if (len(x_ticks), len(y_ticks)) != data.shape:
        raise ValueError("(len(x_ticks), len(y_ticks)) must equal data.shape.")

    data = data.T

    print("--  Readying plot...")
    # Set up a figure and axis.
    fig, ax = plt.subplots()
    ax.imshow(data, **kwargs)

    # Specifically show all ticks.
    ax.set_xticks(np.arange(len(x_ticks)))
    ax.set_yticks(np.arange(len(y_ticks)))

    # Label each ticks with the appropriate categories.
    ax.set_xticklabels(x_ticks)
    ax.set_yticklabels(y_ticks)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(y_ticks)):
        for j in range(len(x_ticks)):
            ax.text(j, i, text_formatter.format(data[i, j]), ha="center", va="center",
                    color=text_color if data[i, j] < text_color_threshold else high_text_color)

    print("--  Finalizing plot...")
    plt.tight_layout()

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        plt.close()

    print("--  Plotting completed.")
    return ax
