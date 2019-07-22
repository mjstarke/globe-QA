from scratch_vars import *

obs = tools.parse_csv(fpSC_Dec)
obs.extend(tools.parse_csv(fpSC_2018))
# cdf1, cdf2 = Dataset(fpGEOS_Dec), Dataset(fpGEOS_Jan)  # B205
cdf1, cdf2 = Dataset(fpGEOS_Jun), Dataset(fpGEOS_Jul)  # B206
sample_count = 1000

filtered_obs = [ob for ob in obs if ob.tcc is not None]
filtered_obs = tools.filter_by_datetime(
    filtered_obs,
    tools.get_cdf_datetime(cdf1, 0) - timedelta(minutes=30),
    tools.get_cdf_datetime(cdf2, -1) + timedelta(minutes=30)
)

filtered_obs = [ob for ob in filtered_obs if (-126 <= ob.lon <= -69) and (23 <= ob.lat <= 51.5)]

tools.patch_obs(filtered_obs, "geos_coincident.csv", "tcc_geos", float)
tools.patch_obs(filtered_obs, "geos_coincident_cat.csv", "tcc_geos_cat")

globe_tallies = []
geos_tallies = []
aqua_tallies = []
terra_tallies = []
g15_tallies = []
g16_tallies = []

globe_categories = ["none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
geos_categories = ["none", "few", "isolated", "scattered", "broken", "overcast"]

#################################################
for _ in tqdm(range(sample_count), desc="Sampling observations"):
    # Randomly sample 5% of all the obs.
    sample = np.random.choice(filtered_obs, int(len(filtered_obs) / 20), False)

    # Tally all the TCCs in each category.
    globe_tally = [sum(1 for ob in sample if ob.tcc == category) for category in globe_categories]
    geos_tally = [sum(1 for ob in sample if ob["tcc_geos_cat"] == category) for category in geos_categories]
    aqua_tally = [sum(1 for ob in sample if ob.tcc_aqua_cat == category) for category in geos_categories]
    terra_tally = [sum(1 for ob in sample if ob.tcc_terra_cat == category) for category in geos_categories]
    g15_tally = [sum(1 for ob in sample if ob.tcc_geo_cat == category and ob.which_geo == "GOES-15") for category in geos_categories]
    g16_tally = [sum(1 for ob in sample if ob.tcc_geo_cat == category and ob.which_geo == "GOES-16") for category in geos_categories]

    # Press overcast and obscured into one.
    globe_tally[-2] += globe_tally[-1]
    globe_tally = globe_tally[:-1]

    # Convert to arrays.
    globe_tally = np.array(globe_tally)
    geos_tally = np.array(geos_tally)
    aqua_tally = np.array(aqua_tally)
    terra_tally = np.array(terra_tally)
    g15_tally = np.array(g15_tally)
    g16_tally = np.array(g16_tally)

    # Divide by sum to get percentages.
    globe_tally = globe_tally / globe_tally.sum()
    geos_tally = geos_tally / geos_tally.sum()
    aqua_tally = aqua_tally / aqua_tally.sum()
    terra_tally = terra_tally / terra_tally.sum()
    g15_tally = g15_tally / g15_tally.sum()
    g16_tally = g16_tally / g16_tally.sum()

    globe_tallies.append(globe_tally)
    geos_tallies.append(geos_tally)
    aqua_tallies.append(aqua_tally)
    terra_tallies.append(terra_tally)
    g15_tallies.append(g15_tally)
    g16_tallies.append(g16_tally)

#################################################
pop_globe_tally = [sum(1 for ob in filtered_obs if ob.tcc == category) for category in globe_categories]
pop_geos_tally = [sum(1 for ob in filtered_obs if ob["tcc_geos_cat"] == category) for category in geos_categories]
pop_aqua_tally = [sum(1 for ob in filtered_obs if ob.tcc_aqua_cat == category) for category in geos_categories]
pop_terra_tally = [sum(1 for ob in filtered_obs if ob.tcc_terra_cat == category) for category in geos_categories]
pop_g15_tally = [sum(1 for ob in filtered_obs if ob.tcc_geo_cat == category and ob.which_geo == "GOES-15") for category in geos_categories]
pop_g16_tally = [sum(1 for ob in filtered_obs if ob.tcc_geo_cat == category and ob.which_geo == "GOES-16") for category in geos_categories]

pop_globe_tally[-2] += pop_globe_tally[-1]
pop_globe_tally = pop_globe_tally[:-1]

pop_globe_tally = np.array(pop_globe_tally)
pop_geos_tally = np.array(pop_geos_tally)
pop_aqua_tally = np.array(pop_aqua_tally)
pop_terra_tally = np.array(pop_terra_tally)
pop_g15_tally = np.array(pop_g15_tally)
pop_g16_tally = np.array(pop_g16_tally)

pop_globe_tally = pop_globe_tally / pop_globe_tally.sum()
pop_geos_tally = pop_geos_tally / pop_geos_tally.sum()
pop_aqua_tally = pop_aqua_tally / pop_aqua_tally.sum()
pop_terra_tally = pop_terra_tally / pop_terra_tally.sum()
pop_g15_tally = pop_g15_tally / pop_g15_tally.sum()
pop_g16_tally = pop_g16_tally / pop_g16_tally.sum()

globe_sem = np.std(globe_tallies, axis=0, ddof=1) / np.sqrt(sample_count)
geos_sem = np.std(geos_tallies, axis=0, ddof=1) / np.sqrt(sample_count)
aqua_sem = np.std(aqua_tallies, axis=0, ddof=1) / np.sqrt(sample_count)
terra_sem = np.std(terra_tallies, axis=0, ddof=1) / np.sqrt(sample_count)
g15_sem = np.std(g15_tallies, axis=0, ddof=1) / np.sqrt(sample_count)
g16_sem = np.std(g16_tallies, axis=0, ddof=1) / np.sqrt(sample_count)

#################################################
fig = plt.figure(figsize=(8, 7.2))
ax = fig.add_subplot(111)

artists = []

artists.append(ax.bar(np.arange(6) - 0.30, pop_globe_tally, color="purple", width=0.12))
artists.append(ax.bar(np.arange(6) - 0.18, pop_geos_tally, color="orange", width=0.12))
artists.append(ax.bar(np.arange(6) - 0.06, pop_aqua_tally, color="#6666ff", width=0.12))
artists.append(ax.bar(np.arange(6) + 0.06, pop_terra_tally, color="#55ff00", width=0.12))
artists.append(ax.bar(np.arange(6) + 0.18, pop_g15_tally, color="#004400", width=0.12))
artists.append(ax.bar(np.arange(6) + 0.30, pop_g16_tally, color="#228822", width=0.12))

#################################################
ax.errorbar(np.arange(6) - 0.30, pop_globe_tally, globe_sem, fmt="none", capsize=5, ecolor="black")
ax.errorbar(np.arange(6) - 0.18, pop_geos_tally, geos_sem, fmt="none", capsize=5, ecolor="black")
ax.errorbar(np.arange(6) - 0.06, pop_aqua_tally, aqua_sem, fmt="none", capsize=5, ecolor="black")
artists.append(ax.errorbar(np.arange(6) + 0.06, pop_terra_tally, terra_sem, fmt="none", capsize=5, ecolor="black"))
ax.errorbar(np.arange(6) + 0.18, pop_g15_tally, g15_sem, fmt="none", capsize=5, ecolor="black")
ax.errorbar(np.arange(6) + 0.30, pop_g16_tally, g16_sem, fmt="none", capsize=5, ecolor="black")

#################################################
for a in np.arange(-0.5, 5.6, 1.0):
    ax.axvline(a, color="#aaaaaa")

#################################################
ax.set_xlabel("Total cloud cover category")
ax.set_xticks(np.arange(6))
ax.set_xticklabels(["none", "few", "isolated", "scattered", "broken", "overcast + obscured"])
ax.set_ylabel("Proportion")
ax.set_yticklabels(["{:.0%}".format(tick) for tick in ax.get_yticks()])
ax.legend(artists, ["GLOBE", "GEOS", "Aqua", "Terra", "GOES-15", "GOES-16", "Standard error"], loc="upper center")
ax.grid(axis="y")

plt.tight_layout()
plt.show()
