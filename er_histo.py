from globeqa import *
import matplotlib.pyplot as plt
import numpy as np

fpLC = "/Users/mjstarke/Documents/GLOBE_A/land_covers_20181001_20190531.json"
fpMM = "/Users/mjstarke/Documents/GLOBE_A/mosquito_habitat_mapper_20170501_20190531.json"
fpSC = "/Users/mjstarke/Documents/GLOBE_A/sky_conditions_20170101_20190531.json"
fpTH = "/Users/mjstarke/Documents/GLOBE_A/tree_heights_20190323_20190531.json"

obs = tools.parse_json(fpSC)
tools.do_quality_check(obs)
obsER = tools.filter_by_flag(obs, {"ER": True})

elevs = [ob.elevation for ob in obsER]

histo, bin_lefts = np.histogram(elevs, np.arange(-6000., 8000.1, 250.))
bin_size = bin_lefts[1] - bin_lefts[0]
# bin_middles = bin_edges[:-1] + (bin_size / 2.)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.bar(bin_lefts[:-1], histo, width=bin_size, align="edge")

plt.title("Histogram of ER elevations for all sky_conditions observations from 2017-Jan-01 to 2019-May-31 (250m bin width)")
ax.set_xlabel("Elevation (m)")
ax.set_ylabel("Count")
ax.grid(axis='y')

plt.show()
