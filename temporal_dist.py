import cartopy.crs as ccrs
from datetime import time
from globeqa import tools
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

fpSC = "/Users/mjstarke/Documents/GLOBE_A/sky_conditions_20170101_20190531.json"

obs = tools.parse_json(fpSC)

times = [60 * ob.measured_dt.hour + ob.measured_dt.minute for ob in obs]

histo, bin_lefts = np.histogram(times, np.arange(0, 1441, 15))

fig = plt.figure(figsize=(16, 8))
ax = fig.add_subplot(111)

ax.bar(bin_lefts[:-1], histo, align="edge", width=15)

ax.set_xticks(np.arange(0, 1440, 60))
ax.set_xticklabels(["{:0>2.0f}Z".format(v / 60) for v in np.arange(0, 1440, 60)])
ax.set_xlim(0, 1440)
plt.title("Temporal distribution of SC observations in 15-minute bins as of 2019 May 31")
ax.set_xlabel("Time (UTC)")
ax.set_ylabel("Count")

plt.show()