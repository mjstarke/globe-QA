from figure_common import *

obs = tools.parse_csv(fp_obs_with_satellite_matches_2017_Dec)
obs.extend(tools.parse_csv(fp_obs_with_satellite_matches_2018))
# cdf1, cdf2 = Dataset(fpGEOS_Dec), Dataset(fpGEOS_Jan)  # B220 - B223
cdf1, cdf2 = Dataset(fp_GEOS_Jun), Dataset(fp_GEOS_Jul)  # B224 - B227
sample_count = 1000

filtered_obs = [ob for ob in obs if ob.tcc is not None]
filtered_obs = tools.filter_by_datetime(
    filtered_obs,
    tools.get_cdf_datetime(cdf1, 0) - timedelta(minutes=30),
    tools.get_cdf_datetime(cdf2, -1) + timedelta(minutes=30)
)

tools.patch_obs(obs, "geos_coincident.csv", "tcc_geos", float)

pop_geos = [ob["tcc_geos"] for ob in filtered_obs]
pop_aqua = [ob.tcc_aqua for ob in filtered_obs if ob.tcc_aqua is not None]
pop_terra = [ob.tcc_terra for ob in filtered_obs if ob.tcc_terra is not None]
pop_geo = [ob.tcc_geo for ob in filtered_obs if ob.tcc_geo is not None]

bin_edges = np.arange(0., 1.01, 0.01)

histo_geos = np.histogram(pop_geos, bin_edges)[0]
histo_aqua = np.histogram(pop_aqua, bin_edges)[0]
histo_terra = np.histogram(pop_terra, bin_edges)[0]
histo_geo = np.histogram(pop_geo, bin_edges)[0]

geos_zeros = sum(1 for tcc in pop_geos if tcc <= 0.00) / histo_geos.sum()
geos_ones = sum(1 for tcc in pop_geos if tcc >= 1.00) / histo_geos.sum()
aqua_zeros = sum(1 for tcc in pop_aqua if tcc <= 0.00) / histo_aqua.sum()
aqua_ones = sum(1 for tcc in pop_aqua if tcc >= 1.00) / histo_aqua.sum()
terra_zeros = sum(1 for tcc in pop_terra if tcc <= 0.00) / histo_terra.sum()
terra_ones = sum(1 for tcc in pop_terra if tcc >= 1.00) / histo_terra.sum()
geo_zeros = sum(1 for tcc in pop_geo if tcc <= 0.00) / histo_geo.sum()
geo_ones = sum(1 for tcc in pop_geo if tcc >= 1.00) / histo_geo.sum()

histo_geos = histo_geos / histo_geos.sum()
histo_aqua = histo_aqua / histo_aqua.sum()
histo_terra = histo_terra / histo_terra.sum()
histo_geo = histo_geo / histo_geo.sum()

fig = plt.figure(figsize=(8, 4))
ax = fig.add_subplot(111)

artists = [
    ax.bar(bin_edges[:-1], histo_geos, align="edge", width=0.01, color="orange"),
    ax.bar([0.0, 0.99], [geos_zeros, geos_ones], align="edge", width=0.01, color="brown")
]

ax.legend(artists, ["Proportion in 0.01-width bins", "Proportion at endpoints"], loc="upper left")
ax.set_xticks([0.0, 0.1, 0.25, 0.50, 0.90, 1.0])
ax.grid(axis="both")
ax.set_xlim(0, 1)
ax.set_yticklabels(["{:.0%}".format(label) for label in ax.get_yticks()])
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("Proportion")
plt.tight_layout()


fig = plt.figure(figsize=(8, 4))
ax = fig.add_subplot(111)

artists = [
    ax.bar(bin_edges[:-1], histo_aqua, align="edge", width=0.01, color="#6666ff"),
    ax.bar([0.0, 0.99], [aqua_zeros, aqua_ones], align="edge", width=0.01, color="#333388")
]

ax.legend(artists, ["Proportion in 0.01-width bins", "Proportion at endpoints"], loc="upper left")
ax.set_xticks([0.0, 0.1, 0.25, 0.50, 0.90, 1.0])
ax.grid(axis="both")
ax.set_xlim(0, 1)
ax.set_yticklabels(["{:.0%}".format(label) for label in ax.get_yticks()])
ax.set_xlabel("Aqua total cloud cover")
ax.set_ylabel("Proportion")
plt.tight_layout()


fig = plt.figure(figsize=(8, 4))
ax = fig.add_subplot(111)

artists = [
    ax.bar(bin_edges[:-1], histo_terra, align="edge", width=0.01, color="#55ff00"),
    ax.bar([0.0, 0.99], [terra_zeros, terra_ones], align="edge", width=0.01, color="#228800")
]

ax.legend(artists, ["Proportion in 0.01-width bins", "Proportion at endpoints"], loc="upper left")
ax.set_xticks([0.0, 0.1, 0.25, 0.50, 0.90, 1.0])
ax.grid(axis="both")
ax.set_xlim(0, 1)
ax.set_yticklabels(["{:.0%}".format(label) for label in ax.get_yticks()])
ax.set_xlabel("Terra total cloud cover")
ax.set_ylabel("Proportion")
plt.tight_layout()


fig = plt.figure(figsize=(8, 4))
ax = fig.add_subplot(111)

artists = [
    ax.bar(bin_edges[:-1], histo_geo, align="edge", width=0.01, color="#888888"),
    ax.bar([0.0, 0.99], [geo_zeros, geo_ones], align="edge", width=0.01, color="#555555")
]

ax.legend(artists, ["Proportion in 0.01-width bins", "Proportion at endpoints"], loc="upper left")
ax.set_xticks([0.0, 0.1, 0.25, 0.50, 0.90, 1.0])
ax.grid(axis="both")
ax.set_xlim(0, 1)
ax.set_yticklabels(["{:.0%}".format(label) for label in ax.get_yticks()])
ax.set_xlabel("Geostationary total cloud cover")
ax.set_ylabel("Proportion")
plt.tight_layout()
