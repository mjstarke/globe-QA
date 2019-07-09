import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
import matplotlib.pyplot as plt
import numpy as np
from globeqa.observation import Observation
from tqdm import tqdm
from typing import List, Optional, Tuple


def make_pc_fig(figsize: Tuple[float, float] = (18, 9), coast_color: str = "#444444", color_bg: bool = True,
                set_limits_explicitly: bool = True, land_color: Optional[str] = "#999999",
                ocean_color: Optional[str] = "#98B6E2"):
    """
    Creates a cartopy figure using the PlateCarree projection.
    :param figsize: The size of the figure for matplotlib (usually in inches).  Default (18, 9).
    :param coast_color: The color of the coastlines.  Default '#444444' (dark grey).
    :param color_bg: Whether to color the background (blue for ocean, orange for land).  Default True.
    :param set_limits_explicitly: Whether to explicitly set the limits to include the entire Earth.  This is necessary
    so that cartopy doesn't resize the limits arbitrarily after a scatter plot.  This should have no effect on other
    plots.  Default True.
    :param land_color: The color to fill land with.  Default '#999999' (medium grey).
    :param ocean_color: The color to fill ocean with.  Default '#98B6E2' (bluish; Cartopy default).
    :return: The axis for the figure.
    """
    # Create a figure and axis with cartopy projection.
    plt.figure(figsize=figsize)
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.coastlines(color=coast_color)

    # Add and color background if requested.
    if color_bg:
        ax.add_feature(NaturalEarthFeature("physical", "land", "110m", facecolor=land_color, zorder=-1))
        ax.add_feature(NaturalEarthFeature("physical", "ocean", "110m", facecolor=ocean_color, zorder=-1))

    # Set limits explicitly if requested.
    if set_limits_explicitly:
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)

    return ax


def plot_annotated_heatmap(data: np.ndarray, x_ticks: List[str], y_ticks: List[str], save_path: Optional[str] = None,
                           text_formatter: str = "{:.0f}", text_color: str = "white", high_text_color: str = "black",
                           text_color_threshold: float = np.inf, figsize: Optional[Tuple[float, float]] = None,
                           labels: List[List[str]] = None, ax=None,
                           **kwargs):
    """
    Creates a simple annotated heatmap.  Read how each parameter works carefully - ordering of lists is important.
    :param data: A two-dimensional array of data for which to create a heatmap.  It will be automatically transposed for
    imshow().
    :param x_ticks: The list of tick labels along the x axis from left to right.  Must have length data.shape[0].
    :param y_ticks: The list of tick labels along the y axis from bottom to top.  Must have length data.shape[1].
    :param save_path: If None, the plot will be shown interactively.  If a file path, the plot will instead be saved to
    that location.  Default None.
    :param text_formatter: The format string for the annotations.  Default '{:.0f}', which produces integers.  Ignored
    if labels is not None.
    :param text_color: The color for the cell labels.  Default 'white'.
    :param high_text_color: The color for the cell labels if the corresponding value is greater than
    text_color_threshold. Default 'black'.
    :param text_color_threshold: The threshold at which to switch from text_color to high_text_color.  Default np.inf
    (which means that text_color is used everywhere).
    :param figsize: The size of the figure (passed to figure()).  Default None, which lets matplotlib decide.  Ignored
    if ax is not None.
    :param kwargs: kwargs are passed to imshow().
    :param labels: Labels to use for the cells.  It should be a list of lists of strings, such that labels[i][j]
    corresponds to the cell in column i (from the left) and row j (from the bottom). Default None, which instead uses
    text_formatter on the value of each cell.
    :param ax: The axis to use for plotting.  Default None, which automatically creates a new axis on a new figure.
    :return: The axis of the drawn plot.
    :raises ValueError: If data is not 2-dimensional, or if lengths of x_ticks and y_ticks do not match data.shape.
    """
    if len(data.shape) != 2:
        raise ValueError("'data' must be two-dimensional.")
    if (len(x_ticks), len(y_ticks)) != data.shape:
        raise ValueError("(len(x_ticks), len(y_ticks)) must equal data.shape.")

    # Transpose the data (required for imshow()).
    data = data.T

    # Flip data upside down, so that options can be specified as if the data is in the first quadrant.
    data = np.flipud(data)
    # Flip y_ticks.
    y_ticks = y_ticks[::-1]

    print("--  Readying plot...")
    # Set up a figure and axis.
    if ax is None:
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

    # Loop over data dimensions and create text annotations.  The exact ways that i and j are used here may seem
    # arbitrary - it's due the transposition required by imshow() and the fact that labels is a list of lists, not an
    # array.  I don't know exactly how this works, but it works.
    for i in range(len(y_ticks)):
        for j in range(len(x_ticks)):
            text = text_formatter.format(data[i, j]) if labels is None else labels[j][-i-1]
            ax.text(j, i, text, ha="center", va="center",
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

    # Set default size if none specified.  Default size is not be visible on a world map.
    if "s" not in kwargs:
        kwargs["s"] = 40

    return ax.scatter(x, y, **kwargs)


def plot_dict_pie(d: dict, keys=None, labels_include_values: bool = True, labels_include_percentages: bool = True,
                  **kwargs):
    """
    Creates a pie chart using a dictionary, and labels each wedge with its value and percentage contribution.
    :param d: The dictionary to plot.  All values must be numeric.
    :param keys: The keys to plot, and the order in which to plot them.  If None, d.keys() is called instead and the
    order will be arbitrary.
    :param labels_include_values: Whether the wedge labels should include the values.  Default True.
    :param labels_include_percentages: Whether the wedge labels should include percentages.  Default True.
    :return: The axis on which the pie is plotted.
    """

    # If no key order is specified, use an arbitrary list.
    if keys is None:
        keys = list(d.keys())

    # Extract the values of d as a list and get the sum.
    values = [d[key] for key in keys]
    total = sum(values)

    # Make labels up to three lines:  key, value, fraction of total.
    labels = [("{}".format(k)) +
              ("\n{}".format(d[k]) if labels_include_values else "") +
              ("\n{:.2%}".format(d[k] / total) if labels_include_percentages else "")
              for k in keys]

    # Create figure and plot pie.
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111)
    ax.pie(values, labels=labels, **kwargs)

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
    :raises ValueError: If ys, labels, and colors are not all the same length, or if the elements of y do not all have
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
