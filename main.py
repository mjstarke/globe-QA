from api_flags import prepare_earth_geometry
import cartopy.crs as ccrs
from datetime import datetime, timedelta
import matplotlib
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from observation import Observation
import os
from tools import *
from typing import List, Optional, Tuple, Any, Iterable


def get_cdf_datetime(cdf: Dataset, index: int) -> datetime:
    """
    Creates a datetime that represents the time at the given index of cdf["time"].
    :param cdf: The CDF Dataset.
    :param index: The time index to process.
    :return: The actual datetime that corresponds to the given index.
    """
    # Get the begin date and begin time from the CDF.  Put them together and convert to a datetime.
    begin_datetime_string = "{}{:0>6}".format(cdf["time"].begin_date, cdf["time"].begin_time)
    begin_datetime = datetime.strptime(begin_datetime_string, "%Y%m%d%H%M%S")

    # Get the value of time at the given index.  This is minutes since the begin time.  It must be converted to int from
    # maskedarray.
    minutes = int(cdf["time"][index])

    # Add to the beginning datetime to get the given datetime.
    return begin_datetime + timedelta(minutes=minutes)


def find_closest_gridbox(cdf: Dataset, t: datetime, lat: float, lon: float) -> Tuple[int, int, int]:
    """
    Find the indicies of the closest gridbox to a given point.

    :param cdf: A NetCDF4 dataset.
    :param t: The datetime of the point.
    :param lat: The signed latitude of the point in degrees.
    :param lon: The signed longitude of the point in degrees.

    :return: The indices for time, latitude, and longitude, respectively, of the gridbox that most closely
    approximates the point.
    """

    # Find first latitude and the step between indicies.
    first_lat = cdf["lat"][0]
    lat_step = cdf["lat"][1] - first_lat
    # Find the difference between the point latitude and the first latitude.  Divide this by the step size to
    # determine which index to use.
    lat_diff = lat - first_lat
    lat_index = round(lat_diff / lat_step)
    lat_size = cdf["lat"].shape[0]

    # As above.
    first_lon = cdf["lon"][0]
    lon_step = cdf["lon"][1] - first_lon
    lon_diff = lon - first_lon
    lon_index = round(lon_diff / lon_step)
    lon_size = cdf["lon"].shape[0]

    # Compose the string that represents the first datetime, then convert it to a datetime.
    begin_datetime_string = "{}{:0>6}".format(cdf["time"].begin_date, cdf["time"].begin_time)
    begin_datetime = datetime.strptime(begin_datetime_string, "%Y%m%d%H%M%S")
    # Deterime the step between indicies.
    time_step = cdf["time"][1]
    # Find the difference between the point time and a first time.  Conver this from a datetime to an integer
    # number of minutes.
    time_diff = t - begin_datetime
    time_diff_minutes = time_diff / timedelta(seconds=60)
    # Divide by the step size to determine which index to use.
    time_index = round(time_diff_minutes / time_step)
    time_size = cdf["time"].shape[0]

    return int(time_index), int(lat_index), int(lon_index)


def parse_observations(fp: str, count: int = 1e30, progress: int = 25000,
                       protocol: Optional[str] = "sky_conditions") -> List[Observation]:
    """
    Parse a GLOBE csv file.
    :param fp: The path to the CSV file.
    :param count: The maximum number of observations to parse.  Default 1e30.
    :param progress: The interval at which to print progress updates.  Larger values cause less frequent updates. If
    not greater than zero, no progress updates will be printed.  Default 25000.
    :param protocol: The protocol that the CSV file comes from.  Default 'sky_conditions'.
    :return: The observations.
    """

    observations = []
    with open(fp, "r") as f:
        header = f.readline().split(',')
        header = [h.strip() for h in header]
        for line in f:
            s = line.split(',')
            observations.append(Observation(header, s, protocol=protocol))
            if len(observations) >= count:
                break
            if (progress > 0) and (len(observations) % progress == 0):
                print("--  Parsed {} observations...".format(len(observations)))

    return observations
# def plot_geos_globe(t, obs, cdf):
#
#     # Set the figure size and initialize the Basemap.
#     plt.figure(figsize=(18, 9))
#     m = Basemap()
#
#     # Draw coastlines.
#     m.drawcoastlines(color="#aaaaaa")
#
#     # Latitude and longitude are provided as one-dimensional arrays, but we need them as two-dimensional arrays.
#     # meshgrid() will achieve that for us.
#     xx, yy = np.meshgrid(cdf["lon"], cdf["lat"])
#
#     # Fill-contour the cloud data.
#     print("... Plotting GEOS-5 fill...")
#     cf_sky = m.contourf(xx, yy, cdf["CLDTT"][t], cmap="Blues_r", levels=np.arange(0., 1.01, 0.05))
#
#     # Add colorbar.
#     m.colorbar(cf_sky, location="right", size="2%")
#
#     # Determine the beginning and end of the window for observations to be plotted.
#     window_center = get_cdf_datetime(cdf, t)
#     window_start = window_center - timedelta(minutes=90)
#     window_end = window_center + timedelta(minutes=90)
#
#     # Loop through GLOBE observations and find those which are inside the aforementioned plotting window.
#     # Properties of the points to plot will be kept in a few lists.
#     scatter_x = []
#     scatter_y = []
#     scatter_z = []  # z is effectively the color of the points
#
#     # This dictionary maps GLOBE observation values to numbers that can be plotted.  In each case, the value to plot
#     # is at the midpoint of the range.
#     cc_dict = {"0": 0.00,
#                "< 10%": 0.05,
#                "20-25%": 0.175,  # 20-25% is a typo in the file.  It should be 10-25%.
#                "25-50%": 0.375,
#                "50-90%": 0.70,
#                "90-100%": 0.95,
#                ">25% obscured": 1.00}
#
#     print("... Searching for valid observations...")
#     for ob in obs:
#         if ob.lat is not None and ob.lon is not None and ob.measured_dt is not None:
#             # If we are inside the observation window...
#             try:
#                 if window_end > ob.measured_dt >= window_start:
#                     # ...add the observation's lat and lon to be plotted.
#                     scatter_x.append(ob.lon)
#                     scatter_y.append(ob.lat)
#
#                     # Use the cloud cover dictionary to get a plottable value for the cloud cover.
#                     scatter_z.append(cc_dict[ob["Total Cloud Cover %"]])
#             except KeyError:
#                 pass
#
#     # Scatter plot the GLOBE observations using the same colorscale as the filled contour.  An edge must be used
#     # or the markers will blend in with the fill.  zorder is set so that the markers render over the coastlines.
#     print("... Plotting valid observations...")
#     m.scatter(scatter_x, scatter_y, s=400, c=scatter_z, cmap="Blues_r", edgecolors="black", marker="P", zorder=9)
#
#     # Title the plot.  Include specific time of the GEOS data and the three-hour window surrounding it for the
#     # observations.
#     plt.title("GEOS-5 total cloud fraction for {} (shaded)\nGLOBE observations from {} through {} (plusses)".format(
#         datetime.strftime(window_center, "%Y-%m-%d  %H%MZ"),
#         datetime.strftime(window_start, "%Y-%m-%d  %H%MZ"),
#         datetime.strftime(window_end, "%Y-%m-%d  %H%MZ")))
#
#     print("... Showing plot...")
#     plt.tight_layout()
#     plt.show()


def plot_ggc(t: int, obs: List[Observation], cdf: Dataset) -> None:
    """
    Plots GEOS data and GLOBE observations on one plot.
    :param t: The time index to use.  The actual time will be pulled from cdf["time"].
    :param obs: The observations to plot.
    :param cdf: The NetCDF dataset to pull cloud data from.
    :return: None.  The file is saved to images/.
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
    print("--- Plotting GEOS-5 fill...")
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
    cmap = matplotlib.cm.get_cmap("Blues_r")

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
    for ob in obs:
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
            ax.scatter(data["x"], data["y"], 200, c=[data["color"]],  edgecolors="black", zorder=9,
                       marker=data["marker"])

    # Title the plot.  Include specific timestamp of the GEOS data and the three-hour window surrounding it for the
    # observations.
    plt.title("GEOS-5 total cloud fraction for {} (shaded)\nGLOBE observations from {} through {} (letters)".format(
        datetime.strftime(window_center, "%Y-%m-%d  %H%MZ"),
        datetime.strftime(window_start, "%Y-%m-%d  %H%MZ"),
        datetime.strftime(window_end, "%Y-%m-%d  %H%MZ")))

    print("--- Finalizing and showing plot...")
    plt.tight_layout()
    plt.savefig("images/GG{:0>4}__{}".format(t, datetime.strftime(window_center, "%Y%m%d_%H%MZ")))
    plt.close()
    print("--- Plotting completed.")


def plot_geo_hm(obs: List[Observation], cdf: Dataset):
    """
    Plots a geographic heatmap of the given observations.
    :param obs: The observations to plot
    :param cdf: The NetCDF dataset that contains the lat/lons.
    """

    # Create lists of x and y points for the observations of interest.
    x = []
    y = []

    # Search through the list of observations for what can be plotted.
    for ob in obs:
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
    plt.tight_layout()
    plt.show()


def plot_cat_hm(obs, cdf, progress=1000):
    histo = np.zeros((7, 6))

    obs_categories = ["obscured", "overcast", "broken", "scattered", "isolated", "few", "none"]
    geos_thresholds = [0.01, 0.10, 0.25, 0.50, 0.90, 1.00]
    geos_categories = ["clear", "few", "isolated", "scattered", "broken", "overcast"]

    print("--- Histogramming observations...")
    for o in range(len(obs)):
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
    im = ax.imshow(histo, cmap="summer_r")

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
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(obs_categories)):
        for j in range(len(geos_categories)):
            text = ax.text(j, i, int(histo[i, j]),
                           ha="center", va="center", color="k")

    ax.set_title("GEOS vs. GLOBE total cloud cover (TCC) at GLOBE observation sites for 2018")
    fig.tight_layout()
    plt.show()
    print("--- Histogram ready.")


def plot_tcc_scatter(obs, cdf, progress=1000):
    x = []
    y = []
    obs_categories = ["none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
    obs_values = [0.00, 0.05, 0.175, 0.375, 0.70, 0.95, 1.00]

    print("--- Processing observations for scatterplot...")
    for o in range(len(obs)):
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

    fig.tight_layout()
    plt.show()



os.chdir("/Users/mjstarke/Documents/GLOBE Task B/")

print("--- Parsing GLOBE csv...")
obs = parse_observations("GLOBE_Cloud_2018.csv")

print("--- Loading GEOS-5 cdf...")
cdf = Dataset("G5GMAO.cldtt.201801.nc4", "r")

land = prepare_earth_geometry()

print("--- Script ending normally.")
