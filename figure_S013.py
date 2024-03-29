from figure_common import *

fp = tools.download_from_api(["sky_conditions"], datetime(2017, 1, 1), datetime(2019, 5, 31))
obs = tools.parse_json(fp)

times = [60 * ob.measured_dt.hour + ob.measured_dt.minute for ob in obs]

histo, bin_lefts = np.histogram(times, np.arange(0, 1441, 15))
zeros = sum(1 for ob in obs if ob.measured_dt.hour == ob.measured_dt.minute == 0)

fig = plt.figure(figsize=(11, 5))
ax = fig.add_subplot(111)

ax.bar(bin_lefts[:-1], histo, align="edge", width=15, color="purple")

ax.set_xticks(np.arange(0, 1441, 60))
ax.set_xticklabels(["{:0>2.0f}Z".format(v / 60) for v in np.arange(0, 1440, 60)] + ["00Z"])
ax.set_xlim(0, 1440)
ax.set_xlabel("Time (UTC)")
ax.set_ylabel("Count")

artists = [
    ax.bar([0], zeros, align="edge", width=15, color="pink"),
    ax.axvline(6.5*60, ls=":", lw=2, c="black"),
    ax.axvline(11*60, ls="--", lw=2, c="black"),
    ax.axvline(18*60, ls="-.", lw=2, c="black"),
]

ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n"
             "Temporal distribution of observations")

plt.tight_layout()
plt.savefig("img/S013_Jan2017-May2019_global_GLOBE-SC_histogram_temporal-no-legend.png")
ax.legend(artists, ["Observations at 0000Z",
                    "Noon India Standard Time",
                    "Noon Central European Time",
                    "Noon Central Standard Time"], loc="upper left")
plt.savefig("img/S013_Jan2017-May2019_global_GLOBE-SC_histogram_temporal.png")
