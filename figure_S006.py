from scratch_vars import *

obs = tools.parse_json(fpSC)
tools.do_quality_check(obs, tools.prepare_earth_geometry())

# Flag counts where keys are just number of flags
flags = tools.get_flag_counts(obs)
# Keys will be dict[str, int] with strs for each source.
flags2 = dict()

for flag in flags:
    obsFlagged = tools.filter_by_flag_sets(obs, all_of=[flag])
    flags2[flag] = tools.find_all_values(obsFlagged, "DataSource")

source_counts = dict()

for source_name in source_names:
    source_counts[source_name] = [
        flags2[flag][source_name] if source_name in flags2[flag] else 0 for flag in sorted(flags2.keys())
    ]

y_array = np.array([source_counts[k] for k in source_counts])

ax = plotters.plot_stacked_bars(
    x=range(len(flags)),
    ys=y_array,
    labels=[k for k in source_counts],
    colors=[source_color[k] for k in source_counts]
)

ax.set_xticks(range(len(flags)))
ax.set_xticklabels(sorted(flags2.keys()))
ax.set_xlabel("Flag")
ax.set_ylabel("Count")
ax.grid(axis="y")

ax.set_title("Jan 2017 - May 2019 global GLOBE\n "
             "Frequency of quality control flags")

plt.tight_layout()
plt.savefig("img/Jan2019-May2019_global_GLOBE_bar_flag_frequency_S006.png")


ax = plotters.plot_stacked_bars(
    x=range(len(flags)),
    ys=y_array / np.sum(y_array, axis=0),  # Division by sum makes it proportionwise.
    labels=[k for k in source_counts],
    colors=[source_color[k] for k in source_counts]
)

ax.set_xticks(range(len(flags)))
ax.set_xticklabels(sorted(flags2.keys()))
ax.set_xlabel("Flag")
ax.set_ylabel("Count")
ax.set_xlim(0.3, 18)  # Make space for the legend.

ax.set_title("Jan 2017 - May 2019 global GLOBE\n"
             "Proprotional frequency of quality control flags")

plt.tight_layout()
plt.savefig("img/Jan2019-May2019_global_GLOBE_bar_flag_proportional_frequency_S006.png")
