from datetime import datetime, timedelta
from globeqa import plotters, tools
import matplotlib.pyplot as plt
import numpy as np

# Set endpoints of data to collect - in this case, the last week (including today).
graph_start = datetime.today().date() - timedelta(days=6)
graph_end = datetime.today().date()

# Download and parse observations.
fp = tools.download_from_api(["sky_conditions"], graph_start, graph_end)
obs = tools.parse_json(fp)

# Filter to observations reporting dust.
obs = [ob for ob in obs if "Dust" in ob and ob["Dust"] == "true"]

# Create a list of all dates between the endpoints specified above.
dates = []
d = graph_start
while d <= graph_end:
    dates.append(d)
    d += timedelta(days=1)

# Bins values by day.
ts = np.histogram([ob.measured_dt for ob in obs], dates)[0]


# Plot a histogram.
fig = plt.figure(figsize=(10, 3.5))
ax = fig.add_subplot(111)
ax.bar(dates[:-1], ts)
ax.set_xlim(graph_start, graph_end)
ax.set_title("Jan 2017 - May 2019 global GLOBE\n"
             "Number of observations reporting dust per day")
plt.tight_layout()
plt.show()


# Plot a scattermap.
ax = plotters.make_pc_fig()
plotters.plot_ob_scatter(obs, ax, c="brown", s=40)
plotters.plot_ob_scatter(obs, ax, c="brown", s=1600, alpha=0.02)
ax.set_title("Jan 2017 - May 2019 global GLOBE\n"
             "Locations of observations reporting dust",
             fontdict={"fontsize": 18})
plt.tight_layout()
plt.show()
