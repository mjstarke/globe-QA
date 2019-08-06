from scratch_vars import *

obs = tools.parse_json(fpSC)

# Find frequency of all values for DataSource.
vals = tools.find_all_values(obs, "DataSource")
# Fix the order of the keys for later.
keys = source_names
# Remove Site Definition since that only applies to land covers.
keys.remove('GLOBE Data Entry Site Definition')

total = sum(vals[k] for k in vals)

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111)
ax.pie([vals[k] for k in keys],
       labels=["{} ({:.2%})".format(k, vals[k] / total) for k in keys],
       labeldistance=None,  # This removes the labels from the pie slices.
       colors=[source_color[k] for k in keys])
ax.set_title("Jan 2017 - May 2019 / Global / GLOBE clouds\nSources of observations")

plt.tight_layout()
plt.savefig("img/S005_Jan2019-May2019_global_GLOBE-SC_pie_data-sources-no-legend.png")
ax.legend()
plt.savefig("img/S005_Jan2019-May2019_global_GLOBE-SC_pie_data-sources.png")
