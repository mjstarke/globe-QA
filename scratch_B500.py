from scratch_vars import *


def rebin(a, factor):
    """
    Rebins a three-dimensional array with dimensions [t, y, x] into an array that is smaller by the given factor in both
    y and x, averaging factor*factor boxes to generate the new array.
    :param a: The array to rebin.
    :param factor: The factor by which to shrink the array.
    :return: The rebinned array.
    """
    # Determine how many values in each dimension must be chopped off for the rebin to work.  For instance, 7x7 cannot
    # be rebinned with factor 2, so we must chop it to 6x6.  The number of values chopped in each dimension is exactly
    # the modulo of the size of that dimension over the rebin factor.
    y_end = -(a.shape[1] % factor)
    x_end = -(a.shape[2] % factor)
    # We cannot use -0 as an endpoint.  Replace it with None.
    y_end = None if y_end == 0 else y_end
    x_end = None if x_end == 0 else x_end
    # Chop the array.
    ret = a[:, :y_end, :x_end]
    # Reshape for averaging, then take the averages.
    ret = ret.reshape([
        ret.shape[0],
        ret.shape[1] // factor,
        factor,
        ret.shape[2] // factor,
        factor]
    ).mean(4).mean(2)
    return ret


def histogram(a):
    zeros = (a == 0).sum()
    histo = np.histogram(a, [-0.1, 0.0, 0.1, 0.25, 0.50, 0.90, 1.00])[0]
    histo[0] += zeros
    histo[1] -= zeros
    histo = histo / histo.sum()
    return histo


cdf = Dataset("/Users/mjstarke/Documents/GLOBE_B/CLDTT.CONUS.201608.01-05.nc4")

data_3km = np.array(cdf["CLDTT"])
histo_3km = histogram(data_3km)

data_15km = rebin(np.array(cdf["CLDTT"]), 5)
histo_15km = histogram(data_15km)

data_30km = rebin(np.array(cdf["CLDTT"]), 10)
histo_30km = histogram(data_30km)

data_45km = rebin(np.array(cdf["CLDTT"]), 15)
histo_45km = histogram(data_45km)

data_60km = rebin(np.array(cdf["CLDTT"]), 20)
histo_60km = histogram(data_60km)


fig = plt.figure(figsize=(8, 7.2))
ax = fig.add_subplot(111)

artists = [ax.bar(np.arange(6) - 0.3, histo_3km, color="#55ffff", width=0.15),
           ax.bar(np.arange(6) - 0.15, histo_15km, color="#33dddd", width=0.15),
           ax.bar(np.arange(6) - 0, histo_30km, color="#11aaaa", width=0.15),
           ax.bar(np.arange(6) + 0.15, histo_45km, color="#008888", width=0.15),
           ax.bar(np.arange(6) + 0.3, histo_60km, color="#005555", width=0.15), ]

#################################################
for a in np.arange(-0.5, 5.6, 1.0):
    ax.axvline(a, color="#aaaaaa")

#################################################
ax.set_xlabel("Total cloud cover category")
ax.set_xticks(np.arange(6))
ax.set_xticklabels(["none", "few", "isolated", "scattered", "broken", "overcast + obscured"])
ax.set_ylabel("Proportion")
ax.set_yticklabels(["{:.1%}".format(tick) for tick in ax.get_yticks()])
ax.legend(artists, ["3km", "15km", "30km", "45km", "60km"], loc="upper center")
ax.grid(axis="y")

ax.set_title("01 - 05 Aug 2016 CONUS GEOS\n"
             "Distribution of cloud cover at various rebinned resolutions")
plt.tight_layout()
plt.savefig("img/S022_01Aug2016-05Aug2016_CONUS_GEOS_cloud_cover_vs_resolution.png")
