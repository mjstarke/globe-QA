from figure_common import *

fp = tools.download_from_api(["sky_conditions"], datetime(2017, 1, 1), datetime(2019, 5, 31))
obs = tools.parse_json(fp)
obs = [ob for ob in obs if not (-300 <= ob.elevation <= 6000)]

ax = plotters.make_pc_fig(figsize=(15.5, 9))

sources = tools.find_all_values(obs, "DataSource")
artists = []

for source in sources:
    theseObs = [ob for ob in obs if ob["DataSource"] == source]
    dot = plotters.plot_ob_scatter(theseObs, ax, s=40, marker=".", color=std_colors[source])
    bubble = plotters.plot_ob_scatter(theseObs, ax, s=1600, marker=".", color=std_colors[source], alpha=0.02)
    artists.append((dot, bubble))

ax.legend(artists, sources, fontsize=18)
ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n"
             "Locations of observations whose elevations lie outside the range -300m to 6000m",
             fontdict={"fontsize": 18})
plt.tight_layout()
plt.savefig("img/S009_Jan2017-May2019_global_GLOBE-SC_scattermap_suspect-elevation.png")
