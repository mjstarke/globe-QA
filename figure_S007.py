from scratch_vars import *

obs = tools.parse_json(fpSC)

# Create a list of dates from 2017 Jan 01 through 2019 May 31.
day = date(2017, 1, 1)
dates = []
while day <= date(2019, 5, 31):
    dates.append(day)
    day += timedelta(days=1)

# Histogram observations by their measured date.
counts, bin_edges = np.histogram([ob.measured_dt.date() for ob in obs], dates)

fig = plt.figure(figsize=(11, 3.5))
ax = fig.add_subplot(111)
ax.stackplot(bin_edges[:-1], counts)
ax.set_xlabel("Date")
ax.set_ylabel("Daily observations")
ax.set_xlim(date(2017, 1, 1), date(2019, 5, 31))
ax.set_ylim(0, 3000)  # Cut off eclipse spike.
ax.grid(axis="y")

ax.text(date(2017, 8, 26), 1080, "North\nAmerican\nEclipse")
ax.text(date(2018, 5, 5), 1080, "NASA GLOBE\nClouds Data\nChallenge")

ax.set_title("Jan 2017 - May 2019 global GLOBE\n"
             "Number of observations per day")

plt.tight_layout()
plt.savefig("img/S007_Jan2017-May2019_global_GLOBE_timeseries_observations_per_day.png")
