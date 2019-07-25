from scratch_vars import *

obs = tools.parse_csv(fpSC_2018)

globe_categories = [None, "none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
globe_labels = ["null", "none", "few", "isolated", "scattered", "broken", "overcast", "obscured"]
satellite_categories = ["none", "few", "isolated", "scattered", "broken", "overcast"]
satellite_labels = ["none", "few", "isolated", "scattered", "broken", "overcast"]


data = np.zeros((6, 8))
for ob in [ob for ob in obs if ob.tcc_aqua is not None]:
    x = satellite_categories.index(tools.bin_cloud_fraction(ob.tcc_aqua / 100., clip=True))
    y = globe_categories.index(ob.tcc)
    data[x, y] += 1

ax = plotters.plot_annotated_heatmap(data, satellite_labels, globe_labels, text_formatter="{:.0f}", figsize=(6, 7), text_color_threshold=1250)
ax.set_xlabel("Aqua total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jan 2018 - Dec 2018 global GLOBE\n"
             "GLOBE vs Aqua total cloud cover")
plt.tight_layout()
plt.savefig("img/S014_Jan2018-Dec2018_global_GLOBEvAqua_coincidence_cloud_cover.png")

ax = plotters.plot_annotated_heatmap(data / data.sum(axis=0, keepdims=True), satellite_labels, globe_labels, text_formatter="{:.2%}", figsize=(6, 7), text_color_threshold=0.5)
ax.set_xlabel("Aqua total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jan 2018 - Dec 2018 global GLOBE\n"
             "GLOBE vs Aqua total cloud cover (rowwise proportions)")
plt.tight_layout()
plt.savefig("img/S014_Jan2018-Dec2018_global_GLOBEvAqua_coincidence_cloud_cover_rowwise.png")

ax = plotters.plot_annotated_heatmap(data / data.sum(axis=1, keepdims=True), satellite_labels, globe_labels, text_formatter="{:.2%}", figsize=(6, 7), text_color_threshold=0.5)
ax.set_xlabel("Aqua total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jan 2018 - Dec 2018 global GLOBE\n"
             "GLOBE vs Aqua total cloud cover (columnwise proportions)")
plt.tight_layout()
plt.savefig("img/S014_Jan2018-Dec2018_global_GLOBEvAqua_coincidence_cloud_cover_columnwise.png")


data = np.zeros((6, 8))
for ob in [ob for ob in obs if ob.tcc_terra is not None]:
    x = satellite_categories.index(tools.bin_cloud_fraction(ob.tcc_terra / 100., clip=True))
    y = globe_categories.index(ob.tcc)
    data[x, y] += 1

ax = plotters.plot_annotated_heatmap(data, satellite_labels, globe_labels, text_formatter="{:.0f}", figsize=(6, 7), text_color_threshold=1300)
ax.set_xlabel("Terra total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jan 2018 - Dec 2018 global GLOBE\n"
             "GLOBE vs Terra total cloud cover")
plt.tight_layout()
plt.savefig("img/S014_Jan2018-Dec2018_global_GLOBEvTerra_coincidence_cloud_cover.png")

ax = plotters.plot_annotated_heatmap(data / data.sum(axis=0, keepdims=True), satellite_labels, globe_labels, text_formatter="{:.2%}", figsize=(6, 7), text_color_threshold=0.5)
ax.set_xlabel("Terra total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jan 2018 - Dec 2018 global GLOBE\n"
             "GLOBE vs Terra total cloud cover (rowwise proportions)")
plt.tight_layout()
plt.savefig("img/S014_Jan2018-Dec2018_global_GLOBEvTerra_coincidence_cloud_cover_rowwise.png")

ax = plotters.plot_annotated_heatmap(data / data.sum(axis=1, keepdims=True), satellite_labels, globe_labels, text_formatter="{:.2%}", figsize=(6, 7), text_color_threshold=0.5)
ax.set_xlabel("Terra total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jan 2018 - Dec 2018 global GLOBE\n"
             "GLOBE vs Terra total cloud cover (columnwise proportions)")
plt.tight_layout()
plt.savefig("img/S014_Jan2018-Dec2018_global_GLOBEvTerra_coincidence_cloud_cover_columnwise.png")


data = np.zeros((6, 8))
for ob in [ob for ob in obs if ob.tcc_geo is not None]:
    x = satellite_categories.index(tools.bin_cloud_fraction(ob.tcc_geo / 100., clip=True))
    y = globe_categories.index(ob.tcc)
    data[x, y] += 1

ax = plotters.plot_annotated_heatmap(data, satellite_labels, globe_labels, text_formatter="{:.0f}", figsize=(6, 7), text_color_threshold=8000)
ax.set_xlabel("GEO total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jan 2018 - Dec 2018 global GLOBE\n"
             "GLOBE vs geostationary total cloud cover")
plt.tight_layout()
plt.savefig("img/S014_Jan2018-Dec2018_global_GLOBEvGeostationary_coincidence_cloud_cover.png")

ax = plotters.plot_annotated_heatmap(data / data.sum(axis=0, keepdims=True), satellite_labels, globe_labels, text_formatter="{:.2%}", figsize=(6, 7), text_color_threshold=0.5)
ax.set_xlabel("GEO total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jan 2018 - Dec 2018 global GLOBE\n"
             "GLOBE vs geostationary total cloud cover (rowwise proportions)")
plt.tight_layout()
plt.savefig("img/S014_Jan2018-Dec2018_global_GLOBEvGeostationary_coincidence_cloud_cover_rowwise.png")

ax = plotters.plot_annotated_heatmap(data / data.sum(axis=1, keepdims=True), satellite_labels, globe_labels, text_formatter="{:.2%}", figsize=(6, 7), text_color_threshold=0.5)
ax.set_xlabel("GEO total cloud cover")
ax.set_ylabel("GLOBE total cloud cover")
ax.set_title("Jan 2018 - Dec 2018 global GLOBE\n"
             "GLOBE vs geostationary total cloud cover (columnwise proportions)")
plt.tight_layout()
plt.savefig("img/S014_Jan2018-Dec2018_global_GLOBEvGeostationary_coincidence_cloud_cover_columnwise.png")