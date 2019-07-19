from scratch_vars import *

obs = tools.parse_json("/Users/mjstarke/PycharmProjects/GLOBE/globeqa/examples/land_covers__mosquito_habitat_mapper__tree_heights_20170101_20190531.json")
tools.do_quality_check(obs, tools.prepare_earth_geometry())
obs = tools.filter_by_flag_sets(obs, all_of=["LW"])

# Create a figure and axis with cartopy projection.
ax = plotters.make_pc_fig()

artists = [
    (
        plotters.plot_ob_scatter([ob for ob in obs if ob["protocol"] == "land_covers"], ax, s=40, marker="_", color="black"),
        plotters.plot_ob_scatter([ob for ob in obs if ob["protocol"] == "land_covers"], ax, s=1600, marker=".", color="black", alpha=0.03)
    ),
    (
        plotters.plot_ob_scatter([ob for ob in obs if ob["protocol"] == "tree_heights"], ax, s=40, marker="1", color="green"),
        plotters.plot_ob_scatter([ob for ob in obs if ob["protocol"] == "tree_heights"], ax, s=1600, marker=".", color="green", alpha=0.03)
    ),
    (
        plotters.plot_ob_scatter([ob for ob in obs if ob["protocol"] == "mosquito_habitat_mapper"], ax, s=40, marker="x", color="red"),
        plotters.plot_ob_scatter([ob for ob in obs if ob["protocol"] == "mosquito_habitat_mapper"], ax, s=1600, marker=".", color="red", alpha=0.03)
    ),
]

ax.legend(artists, ["land_covers", "tree_heights", "mosquito_habitat_mapper"], loc="lower left", fontsize=18)

plt.tight_layout()
plt.show()
