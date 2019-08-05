from scratch_vars import *

obs = tools.parse_json(fpSC)
obs = [ob for ob in obs if not (-300 <= ob.elevation <= 6000)]

ax = plotters.make_pc_fig(figsize=(15.5, 9))

sources = tools.find_all_values(obs, "DataSource")
artists = []

for source in sources:
    theseObs = [ob for ob in obs if ob["DataSource"] == source]
    dot = plotters.plot_ob_scatter(theseObs, ax, s=40, marker=".", color=source_color[source])
    bubble = plotters.plot_ob_scatter(theseObs, ax, s=1600, marker=".", color=source_color[source], alpha=0.02)
    artists.append((dot, bubble))

ax.legend(artists, sources, fontsize=18)
ax.set_title("Jan 2017 - May 2019 global GLOBE\n"
             "Locations of observations whose elevations lie outside the range -300m to 6000m",
             fontdict={"fontsize": 18})
plt.tight_layout()
plt.savefig("img/S009_Jan2017-May2019_global_GLOBE_scattermap_suspect_elevation.png")
