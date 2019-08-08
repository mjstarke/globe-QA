from figure_common import *

obs = tools.parse_csv(fpSC_2018)

none = 0
aqua = 0
terra = 0
geo = 0
aqua_terra = 0
aqua_geo = 0
terra_geo = 0
all_three = 0

for ob in tqdm(obs, desc="Sifting observations"):
    if ob.tcc_aqua and ob.tcc_terra and ob.tcc_geo:
        all_three += 1
    elif ob.tcc_aqua and ob.tcc_terra:
        aqua_terra += 1
    elif ob.tcc_aqua and ob.tcc_geo:
        aqua_geo += 1
    elif ob.tcc_terra and ob.tcc_geo:
        terra_geo += 1
    elif ob.tcc_aqua:
        aqua += 1
    elif ob.tcc_terra:
        terra += 1
    elif ob.tcc_geo:
        geo += 1
    else:
        none += 1

vals = [none, aqua, terra, geo, aqua_terra, aqua_geo, terra_geo, all_three]
labels = ["None", "Aqua", "Terra", "GEO", "Aqua + Terra", "Aqua + GEO", "Terra + GEO", "Aqua + Terra + GEO"]

total = sum(vals)

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111)
ax.pie(vals,
       labels=["{} ({:.2%})".format(k, v / total) for k, v in zip(labels, vals)],
       labeldistance=None)  # This removes the labels from the slices.
ax.legend()
ax.set_title("Jan 2018 - Dec 2018 / Global / GLOBE Clouds\n"
             "Frequency of satellite matches")

plt.tight_layout()
plt.savefig("img/S004_Jan2018-Dec2018_global_GLOBE_pie_satellite-matches.png")
