from figure_common import *

graph_start = datetime(2017, 1, 1)
graph_end = datetime(2019, 5, 31)

fp = tools.download_from_api(["sky_conditions"], datetime(2017, 1, 1), datetime(2019, 5, 31))
obs = tools.parse_json(fp)
obs = [ob for ob in obs if "Dust" in ob]

dates = []
d = graph_start
while d <= graph_end:
    dates.append(d)
    d += timedelta(days=1)

ts = np.histogram([ob.measured_dt for ob in obs], dates)[0]

fig = plt.figure(figsize=(10, 3.5))
ax = fig.add_subplot(111)

ax.bar(dates[:-1], ts)
ax.set_xlim(graph_start, graph_end)

ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n"
             "Number of observations reporting dust per day")
plt.tight_layout()
plt.savefig("img/S018_Jan2017-May2019_global_GLOBE-SC_timeseries_dust-observations.png")


ax = plotters.make_pc_fig()
plotters.plot_ob_scatter(obs, ax, c="brown", s=40)
plotters.plot_ob_scatter(obs, ax, c="brown", s=1600, alpha=0.02)

ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n"
             "Locations of observations reporting dust",
             fontdict={"fontsize": 18})
plt.tight_layout()
plt.savefig("img/S018_Jan2017-May2019_global_GLOBE-SC_scattermap_dust-observations.png")
