from figure_common import *

fp = tools.download_from_api(["sky_conditions"], datetime(2017, 1, 1), datetime(2019, 5, 31))
obs = tools.parse_json(fp)

bottom = np.zeros(60)
artists = []
sources = ["GLOBE Observer App", "GLOBE Data Entry Web Forms", "GLOBE Data Entry App"]

fig = plt.figure(figsize=(11, 5))
ax = fig.add_subplot(111)

for source in sources:

    minutes = [ob.measured_dt.minute for ob in obs if ob.source == source]

    histo, bin_lefts = np.histogram(minutes, np.arange(0, 61, 1))

    artists.append(
        ax.bar(bin_lefts[:-1], histo, align="edge", width=1, color=std_colors[source], bottom=bottom)
    )

    bottom += histo

ax.set_xticks(np.arange(0, 60, 5))
ax.set_xticklabels([":{:0>2.0f}".format(v) for v in np.arange(0, 60, 5)] + [":00"])
ax.set_xlim(0, 60)
ax.set_xlabel("Minute (UTC)")
ax.set_ylabel("Count")

ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n"
             "Temporal distribution of observations (minute only)")

plt.tight_layout()
ax.legend(artists, sources)
plt.savefig("img/S024_Jan2017-May2019_global_GLOBE-SC_histogram_minute.png")
