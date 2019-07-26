from scratch_vars import *

sample_count = 1000

globe_categories = [None, "none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
globe_labels = ["null", "none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
geos_categories = ["none", "few", "isolated", "scattered", "broken", "overcast"]
geos_labels = ["none", "few", "isolated", "scattered", "broken", "overcast"]

obs = tools.parse_csv(fpSC_Dec)
obs.extend(tools.parse_csv(fpSC_2018))
cdf1, cdf2 = Dataset(fpGEOS_Dec), Dataset(fpGEOS_Jan)
cdf3, cdf4 = Dataset(fpGEOS_Jun), Dataset(fpGEOS_Jul)

tools.patch_obs(obs, "geos_coincident_cat.csv", "tcc_geos_cat")

obs_winter = tools.filter_by_datetime(obs,
                                      earliest=tools.get_cdf_datetime(cdf1, 0) - timedelta(minutes=30),
                                      latest=tools.get_cdf_datetime(cdf2, -1) + timedelta(minutes=30))
obs_summer = tools.filter_by_datetime(obs,
                                      earliest=tools.get_cdf_datetime(cdf3, 0) - timedelta(minutes=30),
                                      latest=tools.get_cdf_datetime(cdf4, -1) + timedelta(minutes=30))

########################################################################################################################
population_winter = np.zeros((6, 8))
for ob in obs_winter:
    x = geos_categories.index(ob["tcc_geos_cat"])
    y = globe_categories.index(ob.tcc)
    population_winter[x, y] += 1

population_summer = np.zeros((6, 8))
for ob in obs_summer:
    x = geos_categories.index(ob["tcc_geos_cat"])
    y = globe_categories.index(ob.tcc)
    population_summer[x, y] += 1

########################################################################################################################
rowwise_samples_winter = []
columnwise_samples_winter = []

for _ in tqdm(range(sample_count), desc="Sampling observations (winter)"):
    sample = np.random.choice(obs_winter, int(len(obs_winter) / 20), False)

    data = np.zeros((6, 8))
    for ob in sample:
        x = geos_categories.index(ob["tcc_geos_cat"])
        y = globe_categories.index(ob.tcc)
        data[x, y] += 1
    rowwise_samples_winter.append(data / data.sum(axis=0, keepdims=True))
    columnwise_samples_winter.append(data / data.sum(axis=1, keepdims=True))

########################################################################################################################
rowwise_samples_summer = []
columnwise_samples_summer = []

for _ in tqdm(range(sample_count), desc="Sampling observations (summer)"):
    sample = np.random.choice(obs_summer, int(len(obs_summer) / 20), False)

    data = np.zeros((6, 8))
    for ob in sample:
        x = geos_categories.index(ob["tcc_geos_cat"])
        y = globe_categories.index(ob.tcc)
        data[x, y] += 1
    rowwise_samples_summer.append(data / data.sum(axis=0, keepdims=True))
    columnwise_samples_summer.append(data / data.sum(axis=1, keepdims=True))

########################################################################################################################
# WINTER POPULATION
ax = plotters.plot_annotated_heatmap(population_winter, geos_labels, globe_labels, text_color_threshold=2000,
                                     figsize=(6, 8))
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Dec 2017 - Jan 2018 global GLOBE vs GEOS\n"
             "Total cloud cover")
plt.tight_layout()

########################################################################################################################
# WINTER COLUMNWISE
columnwise_mean_winter = np.mean(columnwise_samples_winter, axis=0)
columnwise_sem_winter = np.std(columnwise_samples_winter, axis=0, ddof=1) / np.sqrt(sample_count)
columnwise_labels_winter = [["" for _ in range(8)] for _ in range(6)]

for i in range(columnwise_mean_winter.shape[0]):
    for j in range(columnwise_mean_winter.shape[1]):
        columnwise_labels_winter[i][j] = "{:.2%}\n±{:.2%}".format(columnwise_mean_winter[i, j],
                                                                  columnwise_sem_winter[i, j])

ax = plotters.plot_annotated_heatmap(columnwise_mean_winter, geos_labels, globe_labels, text_color_threshold=0.5,
                                     figsize=(6, 8), labels=columnwise_labels_winter)
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Dec 2017 - Jan 2018 global GLOBE vs GEOS\n"
             "Total cloud cover (columnwise proportions)")
plt.tight_layout()

########################################################################################################################
# WINTER ROWWISE
rowwise_mean_winter = np.nanmean(rowwise_samples_winter, axis=0)
rowwise_sem_winter = np.nanstd(rowwise_samples_winter, axis=0, ddof=1) / np.sqrt(sample_count)
rowwise_labels_winter = [["" for _ in range(8)] for _ in range(6)]

for i in range(rowwise_mean_winter.shape[0]):
    for j in range(rowwise_mean_winter.shape[1]):
        rowwise_labels_winter[i][j] = "{:.2%}\n±{:.2%}".format(rowwise_mean_winter[i, j], rowwise_sem_winter[i, j])

ax = plotters.plot_annotated_heatmap(rowwise_mean_winter, geos_labels, globe_labels, text_color_threshold=0.5,
                                     figsize=(6, 8), labels=rowwise_labels_winter)
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Dec 2017 - Jan 2018 global GLOBE vs GEOS\n"
             "Total cloud cover (rowwise proportions)")
plt.tight_layout()

########################################################################################################################
# SUMMER POPULATION
ax = plotters.plot_annotated_heatmap(population_summer, geos_labels, globe_labels, text_color_threshold=2000,
                                     figsize=(6, 8))
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jun 2018 - Jul 2018 global GLOBE vs GEOS\n"
             "Total cloud cover")
plt.tight_layout()

########################################################################################################################
# SUMMER COLUMNWISE
columnwise_mean_summer = np.mean(columnwise_samples_summer, axis=0)
columnwise_sem_summer = np.std(columnwise_samples_summer, axis=0, ddof=1) / np.sqrt(sample_count)
columnwise_labels_summer = [["" for _ in range(8)] for _ in range(6)]

for i in range(columnwise_mean_summer.shape[0]):
    for j in range(columnwise_mean_summer.shape[1]):
        columnwise_labels_summer[i][j] = "{:.2%}\n±{:.2%}".format(columnwise_mean_summer[i, j],
                                                                  columnwise_sem_summer[i, j])

ax = plotters.plot_annotated_heatmap(columnwise_mean_summer, geos_labels, globe_labels, text_color_threshold=0.5,
                                     figsize=(6, 8), labels=columnwise_labels_summer)
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jun 2018 - Jul 2018 global GLOBE vs GEOS\n"
             "Total cloud cover (columnwise proportions)")
plt.tight_layout()

########################################################################################################################
# SUMMER ROWWISE
rowwise_mean_summer = np.nanmean(rowwise_samples_summer, axis=0)
rowwise_sem_summer = np.nanstd(rowwise_samples_summer, axis=0, ddof=1) / np.sqrt(sample_count)
rowwise_labels_summer = [["" for _ in range(8)] for _ in range(6)]

for i in range(rowwise_mean_summer.shape[0]):
    for j in range(rowwise_mean_summer.shape[1]):
        rowwise_labels_summer[i][j] = "{:.2%}\n±{:.2%}".format(rowwise_mean_summer[i, j], rowwise_sem_summer[i, j])

ax = plotters.plot_annotated_heatmap(rowwise_mean_summer, geos_labels, globe_labels, text_color_threshold=0.5,
                                     figsize=(6, 8), labels=rowwise_labels_summer)
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jun 2018 - Jul 2018 global GLOBE vs GEOS\n"
             "Total cloud cover (rowwise proportions)")
plt.tight_layout()

########################################################################################################################
# DIFF POPULATION
ax = plotters.plot_annotated_heatmap(population_summer - population_winter, geos_labels, globe_labels,
                                     text_color_threshold=-1e9, figsize=(6, 8), cmap="bwr", vmin=-1000., vmax=1000.)
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("(Jun 2018 - Jul 2018) minus (Dec 2017 - Jan 2018)\n"
             "global GLOBE vs GEOS\n"
             "Total cloud cover")
plt.tight_layout()

########################################################################################################################
# DIFF COLUMNWISE
columnwise_mean_diff = columnwise_mean_summer - columnwise_mean_winter
columnwise_sem_diff = columnwise_sem_summer + columnwise_sem_winter
columnwise_labels_diff = [["" for _ in range(8)] for _ in range(6)]

for i in range(columnwise_mean_diff.shape[0]):
    for j in range(columnwise_mean_diff.shape[1]):
        columnwise_labels_diff[i][j] = "{:.2%}\n±{:.2%}".format(columnwise_mean_diff[i, j], columnwise_sem_diff[i, j])

ax = plotters.plot_annotated_heatmap(columnwise_mean_diff, geos_labels, globe_labels, text_color_threshold=-5,
                                     figsize=(6, 8), labels=columnwise_labels_diff, cmap="bwr", vmin=-.3, vmax=.3)
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("(Jun 2018 - Jul 2018) minus (Dec 2017 - Jan 2018)\n"
             "global GLOBE vs GEOS\n"
             "Total cloud cover (columnwise proportions)")
plt.tight_layout()

########################################################################################################################
# DIFF ROWWISE
rowwise_mean_diff = rowwise_mean_summer - rowwise_mean_winter
rowwise_sem_diff = rowwise_sem_summer + rowwise_sem_winter
rowwise_labels_diff = [["" for _ in range(8)] for _ in range(6)]

for i in range(rowwise_mean_diff.shape[0]):
    for j in range(rowwise_mean_diff.shape[1]):
        rowwise_labels_diff[i][j] = "{:.2%}\n±{:.2%}".format(rowwise_mean_diff[i, j], rowwise_sem_diff[i, j])

ax = plotters.plot_annotated_heatmap(rowwise_mean_diff, geos_labels, globe_labels, text_color_threshold=-.3,
                                     figsize=(6, 8),
                                     labels=rowwise_labels_diff, cmap="bwr", vmin=-.3, vmax=.3)
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("(Jun 2018 - Jul 2018) minus (Dec 2017 - Jan 2018)\n"
             "global GLOBE vs GEOS\n"
             "Total cloud cover (rowwise proportions)")
plt.tight_layout()
