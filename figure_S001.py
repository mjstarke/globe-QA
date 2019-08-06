from scratch_vars import *

obs = tools.parse_json(fpSC)

# Histogram observations by number of obscurations.
histo, xedges = np.histogram([len(ob.obscurations) for ob in obs if ob.tcc == "obscured"], bins=np.arange(-0.5, 11.5, 1.))

fig = plt.figure(figsize=(7, 6))
ax = fig.add_subplot(111)
ax.bar(np.arange(0, 10.1, 1), np.log10(histo))

# Specify axis ticks.
minor_ticks = [2, 3, 5, 20, 30, 50, 200, 300, 500, 2000, 3000, 5000, 20000, 30000]
major_ticks = [1, 10, 100, 1000, 10000]

# Set ticks to log of those values while setting labels to non-log versions.
ax.set_yticks(np.log10(major_ticks))
ax.set_yticklabels(major_ticks)
ax.set_yticks(np.log10(minor_ticks), minor=True)
ax.set_yticklabels(minor_ticks, minor=True)
ax.grid(which="major", axis="y")
ax.set_xlabel("Concurrent obscurations")
ax.set_ylabel("Number of observations")
ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n"
             "Number of obscurations for all observations with 'obscured' cloud cover")

plt.tight_layout()
plt.savefig("img/S001_Jan2017-May2019_global_GLOBE-SC_bar_concurrent-obscurations.png")
