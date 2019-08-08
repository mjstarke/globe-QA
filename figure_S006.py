from figure_common import *

obs = tools.parse_json(fpSC)
# Do QC, to include land geometry detection.
tools.do_quality_check(obs, tools.prepare_earth_geometry())

# This dictionary is flag=count pairs.
flags = tools.get_flag_counts(obs)
# This dictionary will be flag=(source=count) - i.e., it is a dictionary of dictionaries.
flags2 = dict()

# For each flag...
for flag in flags:
    # Filter to only the obs which have this flag.
    obsFlagged = tools.filter_by_flag_sets(obs, all_of=[flag])
    # Set the flags2 entry to the dictionary of source=count pairs.
    flags2[flag] = tools.find_all_values(obsFlagged, "DataSource")

source_counts = dict()
# This dictionary will contain a list of all the counts for a given flag from each source.
# Since the key for a given source may not exist, we check specifically for that and set to 0 when
# a key doesn't exist.
for source_name in ['GLOBE Observer App', 'GLOBE Data Entry Web Forms', 'GLOBE Data Entry App',
                    'GLOBE Data Entry Site Definition', 'GLOBE Email Data Entry', 'GLOBE EMDE SCOOL',
                    'GLOBE Data Entry Legacy']:
    source_counts[source_name] = [
        flags2[flag][source_name] if source_name in flags2[flag] else 0 for flag in sorted(flags2.keys())
    ]

y_array = np.array([source_counts[k] for k in source_counts])

ax = plotters.plot_stacked_bars(
    x=range(len(flags)),
    ys=y_array,
    labels=[k for k in source_counts],
    colors=[std_colors[k] for k in source_counts],
    figsize=(8, 6)
)

ax.set_xticks(range(len(flags)))
ax.set_xticklabels(sorted(flags2.keys()))
ax.set_xlabel("Flag")
ax.set_ylabel("Count")
ax.grid(axis="y")

ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n "
             "Frequency of quality control flags")

plt.tight_layout()
plt.savefig("img/S006_Jan2017-May2019_global_GLOBE_bar_flag_frequency.png")


ax = plotters.plot_stacked_bars(
    x=range(len(flags)),
    ys=y_array / np.sum(y_array, axis=0),  # Division by sum makes it proportionwise.
    labels=[k for k in source_counts],
    colors=[std_colors[k] for k in source_counts],
    figsize=(10, 6)
)

ax.set_xticks(range(len(flags)))
ax.set_xticklabels(sorted(flags2.keys()))
ax.set_xlabel("Flag")
ax.set_ylabel("Proportion")
ax.set_xlim(-0.7, 18)  # Make space for the legend.
ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(["0%", "20%", "40%", "60%", "80%", "100%"])

ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n"
             "Proportional frequency of quality control flags")

plt.tight_layout()
plt.savefig("img/S006_Jan2017-May2019_global_GLOBE-SC_bar_flag-proportional-frequency.png")
