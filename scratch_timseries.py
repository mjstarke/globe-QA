from datetime import date
from globeqa import plotters, tools
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from tqdm import tqdm


path = tools.download_from_api(["sky_conditions"], date(2017, 12, 1), date(2017, 12, 31))
obs = tools.parse_json(path)
cdf = Dataset("/Users/mjstarke/Documents/GLOBE_B/x0037.CLDTOT.201712.nc4")

cat_to_num = {
    "none": 0.00,
    "clear": 0.05,
    "isolated": 0.175,
    "scattered": 0.375,
    "broken": 0.70,
    "overcast": 0.95,
    "obscured": 1.00,
}

x = []
y = []

for ob in tqdm(obs, desc="Gathering observations"):
    try:
        globe = cat_to_num[ob.tcc]
        geos = cdf["CLDTOT"][
            tools.find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)
        ]

        y.append(geos - globe)
        x.append(ob.measured_dt)
    except KeyError:
        pass

fig = plt.figure(figsize=(15, 9))
ax = fig.add_subplot(111)
ax.scatter(x, y)

plt.tight_layout()
plt.show()
