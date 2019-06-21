import cartopy.crs as ccrs
from cartopy.feature import LAND, OCEAN
from datetime import datetime
from globeqa import tools
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from tqdm import tqdm

fpSC = "/Users/mjstarke/Documents/GLOBE_A/sky_conditions_20170101_20190531.json"

obs = tools.parse_json(fpSC)

sources = tools.find_all_values(obs, "DataSource")
keys = list(sources.keys())
keys[1], keys[2] = keys[2], keys[1]
values = [sources[key] for key in keys]
labels = ["{} ({})".format(k, v) for k, v in sources.items()]

fig = plt.figure(figsize=(9, 9))
ax = fig.add_subplot(111)

ax.pie(values, labels=labels)

plt.tight_layout()
plt.show()
