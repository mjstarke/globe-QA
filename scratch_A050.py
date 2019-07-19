from scratch_vars import *

obs = tools.parse_json(fpSC)
tools.do_quality_check(obs)
obs = tools.filter_by_flag_sets(obs, all_of=["ER"])

ax = plotters.make_pc_fig()

sources = tools.find_all_values(obs, "DataSource")
artists = []

for source in sources:
    theseObs = [ob for ob in obs if ob["DataSource"] == source]
    dot = plotters.plot_ob_scatter(theseObs, ax, s=40, marker=".", color=source_color[source])
    bubble = plotters.plot_ob_scatter(theseObs, ax, s=1600, marker=".", color=source_color[source], alpha=0.02)
    artists.append((dot, bubble))

ax.legend(artists, sources, loc="lower left", fontsize=18)
plt.tight_layout()
plt.show()
