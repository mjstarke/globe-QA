from scratch_vars import *

obs = tools.parse_json(fpSC)

# Get number of obs with each cloud cover category.
vals = tools.find_all_values(obs, "CloudCover")
keys = ["none", "clear", "isolated", "scattered", "broken", "overcast", "obscured"]

total = sum(vals[k] for k in vals)

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111)
ax.pie([vals[k] for k in keys],  # Slices ordered by cloud cover category.
       labels=["{} ({:.2%})".format(k, vals[k] / total) for k in keys],
       labeldistance=None,  # Disables automatic labelling outside of legend.
       colors=["#aaaaff", "#8888ff", "#7777dd", "#6666bb", "#555599", "#444477", "#333366"])

ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n"
             "Frequency of each cloud cover category")

plt.tight_layout()
plt.savefig("img/S003_Jan2017-May2019_global_GLOBE-SC_pie_cloud-cover-no-legend.png")
ax.legend()
plt.savefig("img/S003_Jan2017-May2019_global_GLOBE-SC_pie_cloud-cover.png")
