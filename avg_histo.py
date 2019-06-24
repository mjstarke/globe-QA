"""
Plots a geographic heatmap of the given observations.
"""
from datetime import datetime
from globeqa import tools
from globeqa.plotters import fig_pc
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from os.path import join
from tqdm import tqdm

fpSC_2018 = "/Users/mjstarke/Documents/GLOBE_B/GLOBE_Cloud_2018.csv"
fpGEOS_Jan = "/Users/mjstarke/Documents/GLOBE_B/G5GMAO.cldtt.201801.nc4"
fpSaveTo = "/Users/mjstarke/Documents/GLOBE_B/images_avg_histo"

obs = tools.parse_csv(fpSC_2018, count=11000)
cdf = Dataset(fpGEOS_Jan)

print("--- Filtering obs by datetime...")
obsDT = tools.filter_by_datetime(obs, latest=datetime(2018, 1, 30, 23, 59))

category_to_midpoint = dict(
    none=0.00,
    clear=0.00,
    few=0.05,
    isolated=0.175,
    scattered=0.375,
    broken=0.70,
    overcast=0.95,
    obscured=1.00
)

for hours in [[i, i+1, i+2] for i in range(0, 24, 3)]:
    this_hour_string = "considering only observations occurring between {:0>2}00Z and {:0>2}59Z each day".format(
        hours[0],
        hours[-1]
    )
    obsHR = tools.filter_by_hour(obsDT, hours)

    # Create lists of x and y points for the observations of interest.
    x = []
    y = []
    globe = []
    geos = []
    geos_binned = []

    # Search through the list of observations for what can be plotted.
    for ob in tqdm(obsHR, desc="Collecting observation properties"):
        if ob.lat is not None and ob.lon is not None and ob.tcc is not None:
            x.append(ob.lon)
            y.append(ob.lat)
            globe.append(category_to_midpoint[ob.tcc])
            geos_cloud_fraction = cdf["CLDTT"][tools.find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)]
            geos.append(geos_cloud_fraction)
            geos_binned.append(category_to_midpoint[tools.bin_cloud_fraction(geos_cloud_fraction)])

    reduced_lons = cdf["lon"][::4]
    reduced_lats = cdf["lat"][::4]

    print("--- Histogramming...")
    # Create the first numerator histogram that is the sum of all GLOBE reports in each gridbox.
    histo_num_globe, xedges, yedges = np.histogram2d(x, y, [reduced_lons, reduced_lats], weights=globe)
    # Create the second numerator histogram that is the sum of all GEOS reports in each gridbox.
    histo_num_geos, dummy, dummy = np.histogram2d(x, y, [reduced_lons, reduced_lats], weights=geos)
    # Create the second numerator histogram that is the sum of all GEOS reports (binned) in each gridbox.
    histo_num_geos_binned, dummy, dummy = np.histogram2d(x, y, [reduced_lons, reduced_lats], weights=geos_binned)
    # Create the denominator histrogram that is the unweighted heatmap, effectively.
    histo_den, dummy, dummy = np.histogram2d(x, y, [reduced_lons, reduced_lats])

    # Convert the 1D lists of bin edges to 2D lists.
    xx, yy = np.meshgrid(xedges, yedges)

    # Create the weighted histograms.
    histo_globe = histo_num_globe / histo_den
    histo_geos = histo_num_geos / histo_den
    histo_geos_binned = histo_num_geos_binned / histo_den

    # In order to use pcolormesh, we need to transpose the arrays.
    histo_globe = histo_globe.T
    histo_geos = histo_geos.T
    histo_geos_binned = histo_geos_binned.T


    print("--- Preparing to plot #1: GLOBE...")
    ax = fig_pc()

    # Plot as colormesh.
    print("--- Plotting...")
    pcm = ax.pcolormesh(xx, yy, histo_globe, cmap="Blues_r", vmin=0.0, vmax=1.0)

    # Create colorbar with specific ticks for GLOBE TCC category bins.
    plt.colorbar(pcm, ticks=[0.0, 0.1, 0.25, 0.50, 0.90, 1.0], fraction=0.025)

    # Set title, use the space, and show.
    plt.title(
        "Average GLOBE cloud fraction in each bin for all observations \n"
        "between 2018-Jan-01 0000Z and 2018-Jan-30 2359Z" +
        "\n" + this_hour_string
    )
    plt.tight_layout()
    plt.savefig(join(fpSaveTo, "GLOBE_{}.png".format(hours[0])))
    plt.close()
    print("--- Plotting completed.")


    print("--- Preparing to plot #2: GEOS...")
    ax = fig_pc()

    # Plot as colormesh.
    print("--- Plotting...")
    pcm = ax.pcolormesh(xx, yy, histo_geos, cmap="Blues_r", vmin=0.0, vmax=1.0)

    # Create colorbar with specific ticks for GLOBE TCC category bins.
    plt.colorbar(pcm, ticks=[0.0, 0.1, 0.25, 0.50, 0.90, 1.0], fraction=0.025)

    # Set title, use the space, and show.
    plt.title(
        "Average GEOS cloud fraction in each bin coincident with GLOBE observations \n"
        "between 2018-Jan-01 0000Z and 2018-Jan-30 2359Z" +
        "\n" + this_hour_string
    )
    plt.tight_layout()
    plt.savefig(join(fpSaveTo, "GEOS_{}.png".format(hours[0])))
    plt.close()
    print("--- Plotting completed.")


    print("--- Preparing to plot #3: diff...")
    ax = fig_pc()

    # Plot as colormesh.
    print("--- Plotting...")
    pcm = ax.pcolormesh(xx, yy, histo_globe - histo_geos, cmap="coolwarm", vmin=-1.0, vmax=1.0)

    # Create colorbar with specific ticks for GLOBE TCC category bins.
    plt.colorbar(pcm, ticks=np.arange(-1.0, 1.1, 0.25), fraction=0.025)

    # Set title, use the space, and show.
    plt.title(
        "Difference of histograms (GLOBE - GEOS) \n"
        "between 2018-Jan-01 0000Z and 2018-Jan-30 2359Z" +
        "\n" + this_hour_string
    )
    plt.tight_layout()
    plt.savefig(join(fpSaveTo, "diff_{}.png".format(hours[0])))
    plt.close()
    print("--- Plotting completed.")


    print("--- Preparing to plot #4: GEOS binned...")
    ax = fig_pc()

    # Plot as colormesh.
    print("--- Plotting...")
    pcm = ax.pcolormesh(xx, yy, histo_geos_binned, cmap="Blues_r", vmin=0.0, vmax=1.0)

    # Create colorbar with specific ticks for GLOBE TCC category bins.
    plt.colorbar(pcm, ticks=[0.0, 0.1, 0.25, 0.50, 0.90, 1.0], fraction=0.025)

    # Set title, use the space, and show.
    plt.title(
        "Average GEOS cloud fraction (after binning and midpointing) in each bin coincident with GLOBE observations \n"
        "between 2018-Jan-01 0000Z and 2018-Jan-30 2359Z \n" +
        this_hour_string
    )
    plt.tight_layout()
    plt.savefig(join(fpSaveTo, "GEOS_binned_{}.png".format(hours[0])))
    plt.close()
    print("--- Plotting completed.")


    print("--- Preparing to plot #5: diff with GEOS binned...")
    ax = fig_pc()

    # Plot as colormesh.
    print("--- Plotting...")
    pcm = ax.pcolormesh(xx, yy, histo_globe - histo_geos_binned, cmap="coolwarm", vmin=-1.0, vmax=1.0)

    # Create colorbar.
    plt.colorbar(pcm, ticks=np.arange(-1.0, 1.1, 0.25), fraction=0.025)

    # Set title, use the space, and show.
    plt.title(
        "Difference of histograms (GLOBE - GEOS after binning and midpointing) \n"
        "between 2018-Jan-01 0000Z and 2018-Jan-30 2359Z \n" +
        this_hour_string
    )
    plt.tight_layout()
    plt.savefig(join(fpSaveTo, "diff_binned_{}.png".format(hours[0])))
    plt.close()
    print("--- Plotting completed.")
