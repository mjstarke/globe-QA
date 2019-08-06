from datetime import datetime, timedelta
from globeqa import plotters, tools
import matplotlib.pyplot as plt
import numpy as np

# Set endpoints of data to collect - in this case, the last week (including today).
# We need both endpoints as date and datetime objects because, obviously, the two types cannot be compared.
graph_start_date = datetime.today().date() - timedelta(days=6)
graph_end_date = datetime.today().date()
graph_start_datetime = datetime.combine(graph_start_date, datetime.min.time())
graph_end_datetime = datetime.combine(graph_end_date, datetime.max.time())

# Download and parse observations.
fp = tools.download_from_api(["sky_conditions"], graph_start_date, graph_end_date)
obs = tools.parse_json(fp)

# Filter to observations reporting dust.
obs = [ob for ob in obs if "Dust" in ob and ob["Dust"] == "true"]

# Create a list of all dates between the endpoints specified above.
dates = []
d = graph_start_datetime
while d <= graph_end_datetime:
    dates.append(d)
    d += timedelta(days=1)

# Bins values by day.
ts = np.histogram([ob.measured_dt for ob in obs], dates)[0]


# Plot a histogram.
fig = plt.figure(figsize=(10, 3.5))
ax = fig.add_subplot(111)
ax.bar(dates[:-1], ts)
ax.set_xlim(graph_start_datetime - timedelta(days=0.5), graph_end_datetime + timedelta(days=0.5))
ax.set_xlabel("Date (UTC)")
ax.set_ylabel("Dust observations per day")
ax.set_title("Number of observations reporting dust per day")
plt.tight_layout()
plt.show()


# Plot a scattermap.
ax = plotters.make_pc_fig()
plotters.plot_ob_scatter(obs, ax, c="brown", s=40)
plotters.plot_ob_scatter(obs, ax, c="brown", s=1600, alpha=0.02)
ax.set_title("Locations of observations reporting dust",
             fontdict={"fontsize": 18})
plt.tight_layout()
plt.show()
