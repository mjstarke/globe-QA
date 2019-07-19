from scratch_vars import *

globe_categories = [None, "none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
globe_labels = ["null", "none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
geos_categories = ["none", "few", "isolated", "scattered", "broken", "overcast"]
geos_labels = ["none", "few", "isolated", "scattered", "broken", "overcast"]

obs = tools.parse_csv(fpSC_2018)


########################################################################################################################
cdf_jan = Dataset(fpGEOS_Jan)
obs_jan = tools.filter_by_datetime(obs,
                                   earliest=tools.get_cdf_datetime(cdf_jan, 0) - timedelta(minutes=30),
                                   latest=tools.get_cdf_datetime(cdf_jan, -1) + timedelta(minutes=30))

for ob in tqdm(obs_jan, desc="Gathering coincident GEOS output"):
    ob.tcc_geos = cdf_jan["CLDTOT"][tools.find_closest_gridbox(cdf_jan, ob.measured_dt, ob.lat, ob.lon)]
    ob.tcc_geos_category = tools.bin_cloud_fraction(ob.tcc_geos, True)


########################################################################################################################
absolute_jan = np.zeros((6, 8))
for ob in obs_jan:
    x = geos_categories.index(ob.tcc_geos_category)
    y = globe_categories.index(ob.tcc)
    absolute_jan[x, y] += 1

rowwise_jan = absolute_jan / absolute_jan.sum(axis=0, keepdims=True)
columnwise_jan = absolute_jan / absolute_jan.sum(axis=1, keepdims=True)


########################################################################################################################
fig = plt.figure(figsize=(14, 7))
ax1 = fig.add_subplot(131)
ax2 = fig.add_subplot(132)
ax3 = fig.add_subplot(133)

plotters.plot_annotated_heatmap(absolute_jan, geos_labels, globe_labels, text_color_threshold=1000, ax=ax1)
ax1.set_xlabel("GEOS total cloud cover")
ax1.set_ylabel("GLOBE total cloud cover")
plt.tight_layout()

plotters.plot_annotated_heatmap(columnwise_jan, geos_labels, ["" for _ in globe_labels], text_color_threshold=0.4, text_formatter="{:.2%}", ax=ax2)
ax2.set_xlabel("GEOS total cloud cover")
ax2.yaxis.set_ticks_position("none")
plt.tight_layout()

plotters.plot_annotated_heatmap(rowwise_jan, geos_labels, globe_labels, text_color_threshold=0.4, text_formatter="{:.2%}", ax=ax3)
ax3.set_xlabel("GEOS total cloud cover")
ax3.yaxis.set_ticks_position("right")
plt.tight_layout()


########################################################################################################################
cdf_jul = Dataset(fpGEOS_Jul)
obs_jul = tools.filter_by_datetime(obs,
                                   earliest=tools.get_cdf_datetime(cdf_jul, 0) - timedelta(minutes=30),
                                   latest=tools.get_cdf_datetime(cdf_jul, -1) + timedelta(minutes=30))

for ob in tqdm(obs_jul, desc="Gathering coincident GEOS output"):
    ob.tcc_geos = cdf_jul["CLDTOT"][tools.find_closest_gridbox(cdf_jul, ob.measured_dt, ob.lat, ob.lon)]
    ob.tcc_geos_category = tools.bin_cloud_fraction(ob.tcc_geos, True)


########################################################################################################################
absolute_jul = np.zeros((6, 8))
for ob in obs_jul:
    x = geos_categories.index(ob.tcc_geos_category)
    y = globe_categories.index(ob.tcc)
    absolute_jul[x, y] += 1

rowwise_jul = absolute_jul / absolute_jul.sum(axis=0, keepdims=True)
columnwise_jul = absolute_jul / absolute_jul.sum(axis=1, keepdims=True)


########################################################################################################################
fig = plt.figure(figsize=(14, 7))
ax1 = fig.add_subplot(131)
ax2 = fig.add_subplot(132)
ax3 = fig.add_subplot(133)

plotters.plot_annotated_heatmap(absolute_jul, geos_labels, globe_labels, text_color_threshold=800, ax=ax1)
ax1.set_xlabel("GEOS total cloud cover")
ax1.set_ylabel("GLOBE total cloud cover")
plt.tight_layout()

plotters.plot_annotated_heatmap(columnwise_jul, geos_labels, ["" for _ in globe_labels], text_color_threshold=0.4, text_formatter="{:.2%}", ax=ax2)
ax2.set_xlabel("GEOS total cloud cover")
ax2.yaxis.set_ticks_position("none")
plt.tight_layout()

plotters.plot_annotated_heatmap(rowwise_jul, geos_labels, globe_labels, text_color_threshold=0.4, text_formatter="{:.2%}", ax=ax3)
ax3.set_xlabel("GEOS total cloud cover")
ax3.yaxis.set_ticks_position("right")
plt.tight_layout()


########################################################################################################################
fig = plt.figure(figsize=(14, 7))
ax1 = fig.add_subplot(131)
ax2 = fig.add_subplot(132)
ax3 = fig.add_subplot(133)

plotters.plot_annotated_heatmap(absolute_jul - absolute_jan, geos_labels, globe_labels, text_color_threshold=-600, ax=ax1, cmap="bwr")
ax1.set_xlabel("GEOS total cloud cover")
ax1.set_ylabel("GLOBE total cloud cover")
plt.tight_layout()

plotters.plot_annotated_heatmap(columnwise_jul - columnwise_jan, geos_labels, ["" for _ in globe_labels], text_color_threshold=-5, text_formatter="{:.2%}", ax=ax2, cmap="bwr", vmin=-.3, vmax=.3)
ax2.set_xlabel("GEOS total cloud cover")
ax2.yaxis.set_ticks_position("none")
plt.tight_layout()

plotters.plot_annotated_heatmap(rowwise_jul - rowwise_jan, geos_labels, globe_labels, text_color_threshold=-0.2, text_formatter="{:.2%}", ax=ax3, cmap="bwr", vmin=-.3, vmax=.3)
ax3.set_xlabel("GEOS total cloud cover")
ax3.yaxis.set_ticks_position("right")
plt.tight_layout()
