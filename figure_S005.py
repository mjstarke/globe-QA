from scratch_vars import *

obs = tools.parse_json(fpSC)

vals = tools.find_all_values(obs, "DataSource")
keys = source_names
keys.remove('GLOBE Data Entry Site Definition')

total = sum(vals[k] for k in vals)

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111)
ax.pie([vals[k] for k in keys],
       labels=["{} ({:.2%})".format(k, vals[k] / total) for k in keys],
       labeldistance=None,  # This removes the labels from the pie slices.
       colors=[source_color[k] for k in keys])
ax.legend()
ax.set_title("Jan 2017 - May 2019 global GLOBE\nSources of GLOBE observations")

plt.tight_layout()
plt.savefig("img/Jan2019-May2019_global_GLOBE_pie_data_sources_S005.png")
