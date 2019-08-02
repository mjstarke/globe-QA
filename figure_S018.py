from scratch_vars import *

graph_start = datetime(2017, 1, 1)
graph_end = datetime(2019, 5, 31)

obs = tools.parse_json(fpSC)
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

ax.title("Jan 2017 - May 2019 global GLOBE"
         "Number of observations reporting dust per day")
plt.tight_layout()
plt.savefig("img/S018_Jan2017-May2019_global_GLOBE_timeseries_dust_observations.png")


ax = plotters.make_pc_fig()
plotters.plot_ob_scatter(obs, ax, c="brown", s=40)
plotters.plot_ob_scatter(obs, ax, c="brown", s=16000, alpha=0.03)

ax.set_title("Jan 2017 - May 2019 global GLOBE"
             "Locations of observations reporting dust")
plt.tight_layout()
plt.savefig("img/S018_Jan2017-May2019_global_GLOBE_scattermap_dust_observations.png")
