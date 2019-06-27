import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
from cartopy.feature.nightshade import Nightshade
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


def make_pc_fig(figsize: Tuple[float, float] = (18, 9), coast_color: str = "#aaaaaa", color_bg: bool = True,
                set_limits_explicitly: bool = True, land_color: Optional[str] = None,
                ocean_color: Optional[str] = None):
    """
    Creates a cartopy figure using the PlateCarree projection.
    :param figsize: The size of the figure for matplotlib (usually in inches).  Default (18, 9).
    :param coast_color: The color of the coastlines.  Default '#aaaaaa' (light grey).
    :param color_bg: Whether to color the background (blue for ocean, orange for land).  Default True.
    :param set_limits_explicitly: Whether to explicitly set the limits to include the entire Earth.  This is necessary
    so that cartopy doesn't resize the limits arbitrarily after a scatter plot.  This should have no effect on other
    plots.  Default True.
    :param land_color: The color to fill land with.  Default None, which uses the default color.
    :param ocean_color: The color to fill ocean with.  Default None, which uses the default color.
    :return: The axis for the figure.
    """
    # Create a figure and axis with cartopy projection.
    plt.figure(figsize=figsize)
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Render coastlines in grey so they don't stand out too much.
    ax.coastlines(color=coast_color)

    if land_color is None:
        land_color = np.array([0.9375, 0.9375, 0.859375])
    if ocean_color is None:
        ocean_color = np.array([0.59375, 0.71484375, 0.8828125])

    if color_bg:
        ax.add_feature(NaturalEarthFeature("physical", "land", "110m", facecolor=land_color, zorder=-1))
        ax.add_feature(NaturalEarthFeature("physical", "ocean", "110m", facecolor=ocean_color, zorder=-1))

    if set_limits_explicitly:
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)

    return ax


def plot_annotated_heatmap(data: np.ndarray, x_ticks: List[str], y_ticks: List[str], save_path: Optional[str] = None,
                           text_formatter: str = "{:.0f}", text_color: str = "white", high_text_color: str = "black",
                           text_color_threshold: float = np.inf, figsize: Optional[Tuple[float, float]] = None,
                           **kwargs):
    """
    Creates a simple annotated heatmap.
    :param data: A two-dimensional array of data for which to create a heatmap.  It will be automatically transposed for
    imshow().
    :param x_ticks: The list of tick labels along the x axis from left to right.  Must have length data.shape[0].
    :param y_ticks: The list of tick labels along the y axis from bottom to top.  Must have length data.shape[1].
    :param save_path: If None, the plot will be shown interactively.  If a file path, the plot will instead be saved to
    that location.  Default None.
    :param text_formatter: The format string for the annotations.  Default '{:.0f}', which produces integers.
    :param text_color: The color for the cell labels.  Default 'white'.
    :param high_text_color: The color for the cell labels if the corresponding value is greater than
    text_color_threshold. Default 'black'.
    :param text_color_threshold: The threshold at which to switch from text_color to high_text_color.  Default np.inf
    (which means that text_color is used everywhere).
    :param figsize: The size of the figure (passed to figure()).  Default None, which lets matplotlib decide.
    :param kwargs: kwargs are passed to imshow().
    :return: The axis of the drawn plot.
    :raises: ValueError if data is not 2-dimensional, or if lengths of x_ticks and y_ticks do not match data.shape.
    """
    if len(data.shape) != 2:
        raise ValueError("'data' must be two-dimensional.")
    if (len(x_ticks), len(y_ticks)) != data.shape:
        raise ValueError("(len(x_ticks), len(y_ticks)) must equal data.shape.")

    data = data.T

    data = np.flipud(data)
    y_ticks = y_ticks[::-1]

    print("--  Readying plot...")
    # Set up a figure and axis.
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
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


def plot_ob_scatter(obs: List[Observation], ax, **kwargs):
    """
    Scatters observations on a map.
    :param obs: The observations to scatter.
    :param ax: The axis to plot on.
    :param kwargs: kwargs are passed to scatter().
    :return: The PathCollection for the point scatter (not the bubble scatter).
    """
    x = []
    y = []

    for ob in tqdm(obs, desc="Preparing observations"):
        if ob.lat is not None and ob.lon is not None:
            x.append(ob.lon)
            y.append(ob.lat)

    # Set default size if none specified..
    if "s" not in kwargs:
        kwargs["s"] = 40

    return ax.scatter(x, y, **kwargs)


def plot_dict_pie(d: dict, keys=None, colors=None):
    """
    Creates a pie chart using a dictionary, and labels each slice with its value and percentage contribution.
    :param d: The dictionary to plot.  All values must be numeric.
    :param keys: The keys to plot, and the order in which to plot them.  If None, d.keys() is called instead and the
    order will be arbitrary.
    :param colors: The colors to plot with; one for each key.  Default None, which lets matplotlib set default colors.
    :return: The axis on which the pie is plotted.
    """
    if keys is None:
        keys = list(d.keys())

    values = [d[key] for key in keys]
    total = sum(values)
    labels = ["{}\n{}\n{:.2%}".format(k, d[k], d[k] / total) for k in keys]

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111)

    ax.pie(values, labels=labels, colors=colors)

    plt.tight_layout()
    plt.show()
    return ax


def plot_stacked_bars(x, ys, labels, colors, legend: bool = True, **kwargs):
    """
    Creates a stacked bar chart.
    :param x: The horizontal positions of the bars.
    :param ys: A list of lists of heights for the bars.  Each element of the outer list is a group of bars that all have
    the same color; each element of the inner lists are the bars' heights.
    :param labels: A list of legend labels corresponding to the lists of y value lists.
    :param colors: A list of colors corresponding to the lists of y value lists.
    :param legend: Whether to draw the legend.  Default True.
    :param kwargs: kwargs are passed to bar().  kwargs 'color' and 'bottom' should not be passed.
    :return: The axis on which the bar was plotted.
    :raises: ValueError if ys, labels, and colors are not all the same length, or if the elements of y do not all have
    the same length as x.
    """
    # For each group of bars...
    for y in ys:
        # If the number of bars does not match the number of x positions, raise an error.
        if len(y) != len(x):
            raise ValueError("All sets of y values must be equal in length to 'x'.")
    # If the number of bar GROUPS does not match the number of labels and colors, raise an error.
    if not (len(ys) == len(labels) == len(colors)):
        raise ValueError("'y', 'labels', and 'colors' must be equal in length.")

    # Create a figure.
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Collect artists for the legend.
    artists = []

    # Keep track of the previous tops of the bars.
    prev_y = None

    # For each group of bars...
    for i in range(len(ys)):
        y = np.array(ys[i])
        # Plot the group of bars.
        bar = ax.bar(x, y, color=colors[i], bottom=prev_y, **kwargs)
        artists.append(bar)
        # Set prev_y to the tops of these bars if this is the first group of bars; otherwise, add the heights of these
        # bars to the previous value.
        prev_y = y if prev_y is None else prev_y + y

    if legend:
        ax.legend(artists, labels)

    return ax
