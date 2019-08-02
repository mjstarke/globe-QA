from scratch_vars import *
import matplotlib.patches as mpatches

plt.figure(figsize=(6, 6))
ax = plt.axes(projection=ccrs.PlateCarree())

dc_lat = 38.996944
dc_lon = -76.848333
ax.set_xlim(dc_lon - 1, dc_lon + 1)
ax.set_ylim(dc_lat - 1, dc_lat + 1)

ax.add_feature(NaturalEarthFeature("physical", "land", "50m", facecolor="#999999", zorder=-1), edgecolor="#444444", linewidth=1)
ax.add_feature(NaturalEarthFeature("physical", "ocean", "50m", facecolor="#98B6E2", zorder=-1), edgecolor="#444444", linewidth=1)

for lat in np.arange(38., 41., 0.25) + 0.125:
    ax.axhline(lat, color="orange")

for lon in np.arange(-80., -73., 0.3125) + (0.3125 / 2):
    ax.axvline(lon, color="orange")

ax.add_patch(mpatches.Circle((dc_lon, dc_lat), 0.4, alpha=0.3, edgecolor="cyan", facecolor="cyan", lw=0))
ax.add_patch(mpatches.Circle((dc_lon, dc_lat), 0.4, fill=False, edgecolor="cyan", lw=3))

ax.scatter([dc_lon], [dc_lat], s=100, c="black", zorder=1000)

states_provinces = NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='50m',
        facecolor='none')

ax.add_feature(states_provinces, edgecolor="#444444", linewidth=1)

ax.set_title("Comparison of GEOS output resolution (orange grid)\nand 40-km satellite averaging radius (cyan circle)")
plt.tight_layout()
plt.savefig("img/S023_none_none_none_schematic_resolution_comparison.png")
