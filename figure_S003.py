from scratch_vars import *

obs = tools.parse_json(fpSC)

vals = tools.find_all_values(obs, "CloudCover")
keys = ["none", "clear", "isolated", "scattered", "broken", "overcast", "obscured"]

total = sum(vals[k] for k in vals)

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111)
ax.pie([vals[k] for k in keys],
       labels=["{} ({:.2%})".format(k, vals[k] / total) for k in keys],
       labeldistance=None,
       colors=["#aaaaff", "#8888ff", "#7777dd", "#6666bb", "#555599", "#444477", "#333366"])
ax.legend()
ax.set_title("Jan 2017 - May 2019 global GLOBE\nFrequency of each cloud cover category")

plt.tight_layout()
plt.savefig("img/S003_Jan2017-May2019_global_GLOBE_pie_cloud_cover.png")
