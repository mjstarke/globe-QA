from figure_common import *

obs = tools.parse_json(fpSC)

# Find frequency of all values for DataSource.
vals = tools.find_all_values(obs, "DataSource")
# Fix the order of the keys for later.
keys = ['GLOBE Observer App', 'GLOBE Data Entry Web Forms', 'GLOBE Data Entry App', 'GLOBE Email Data Entry',
        'GLOBE EMDE SCOOL', 'GLOBE Data Entry Legacy']

total = sum(vals[k] for k in vals)

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111)
ax.pie([vals[k] for k in keys],
       labels=["{} ({:.2%})".format(k, vals[k] / total) for k in keys],
       labeldistance=None,  # This removes the labels from the pie slices.
       colors=[std_colors[k] for k in keys])
ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds\n"
             "Sources of observations")

plt.tight_layout()
plt.savefig("img/S005_Jan2019-May2019_global_GLOBE-SC_pie_data-sources-no-legend.png")
ax.legend()
plt.savefig("img/S005_Jan2019-May2019_global_GLOBE-SC_pie_data-sources.png")
