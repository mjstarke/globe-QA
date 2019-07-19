from scratch_vars import *

sample_count = 1000

globe_categories = [None, "none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
globe_labels = ["null", "none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
geos_categories = ["none", "few", "isolated", "scattered", "broken", "overcast"]
geos_labels = ["none", "few", "isolated", "scattered", "broken", "overcast"]

obs = tools.parse_csv(fpSC_2018)
cdf = Dataset(fpGEOS_Jan)

obs = tools.filter_by_datetime(obs,
                               earliest=tools.get_cdf_datetime(cdf, 0) - timedelta(minutes=30),
                               latest=tools.get_cdf_datetime(cdf, -1) + timedelta(minutes=30))

for ob in tqdm(obs, desc="Gathering coincident GEOS output"):
    ob.tcc_geos = cdf["CLDTOT"][tools.find_closest_gridbox(cdf, ob.measured_dt, ob.lat, ob.lon)]
    ob.tcc_geos_category = tools.bin_cloud_fraction(ob.tcc_geos, True)

absolute_samples = []
rowwise_samples = []
columnwise_samples = []


########################################################################################################################
for _ in tqdm(range(sample_count), desc="Sampling observations"):
    sample = np.random.choice(obs, int(len(obs) / 20), False)

    data = np.zeros((6, 8))
    for ob in sample:
        x = geos_categories.index(ob.tcc_geos_category)
        y = globe_categories.index(ob.tcc)
        data[x, y] += 1
    absolute_samples.append(data)
    rowwise_samples.append(data / data.sum(axis=0, keepdims=True))
    columnwise_samples.append(data / data.sum(axis=1, keepdims=True))


########################################################################################################################
absolute_mean = np.mean(absolute_samples, axis=0)
absolute_sem = np.std(absolute_samples, axis=0) / np.sqrt(sample_count)
absolute_labels = [["" for _ in range(8)] for _ in range(6)]

for i in range(absolute_mean.shape[0]):
    for j in range(absolute_mean.shape[1]):
        absolute_labels[i][j] = "{:.1f}\n±{:.2f}".format(absolute_mean[i, j], absolute_sem[i, j])

ax = plotters.plot_annotated_heatmap(absolute_mean, geos_labels, globe_labels, text_color_threshold=45, figsize=(6, 7),
                                     labels=absolute_labels)
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
plt.tight_layout()


########################################################################################################################
columnwise_mean = np.mean(columnwise_samples, axis=0)
columnwise_sem = np.std(columnwise_samples, axis=0) / np.sqrt(sample_count)
columnwise_labels = [["" for _ in range(8)] for _ in range(6)]

for i in range(columnwise_mean.shape[0]):
    for j in range(columnwise_mean.shape[1]):
        columnwise_labels[i][j] = "{:.2%}\n±{:.2%}".format(columnwise_mean[i, j], columnwise_sem[i, j])

ax = plotters.plot_annotated_heatmap(columnwise_mean, geos_labels, globe_labels, text_color_threshold=0.5, figsize=(6, 7),
                                     labels=columnwise_labels)
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
plt.tight_layout()


########################################################################################################################
rowwise_mean = np.nanmean(rowwise_samples, axis=0)
rowwise_sem = np.nanstd(rowwise_samples, axis=0) / np.sqrt(sample_count)
rowwise_labels = [["" for _ in range(8)] for _ in range(6)]

for i in range(rowwise_mean.shape[0]):
    for j in range(rowwise_mean.shape[1]):
        rowwise_labels[i][j] = "{:.2%}\n±{:.2%}".format(rowwise_mean[i, j], rowwise_sem[i, j])

ax = plotters.plot_annotated_heatmap(rowwise_mean, geos_labels, globe_labels, text_color_threshold=0.5, figsize=(6, 7),
                                     labels=rowwise_labels)
ax.set_xlabel("GEOS total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
plt.tight_layout()