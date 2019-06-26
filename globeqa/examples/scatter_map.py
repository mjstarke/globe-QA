from datetime import date, timedelta
from globeqa import tools, plotters
import matplotlib.pyplot as plt

protocols = ["sky_conditions", "land_covers", "mosquito_habitat_mapper", "tree_heights"]
day = date.today() - timedelta(days=1)

# Download yesterday's observations.
path = tools.download_from_api(protocols, day)

# Parse the downloaded file.
obs = tools.parse_json(path)

# Create a figure and axis with cartopy projection.
ax = plotters.fig_pc()

# Prepare to collect artists for the legend.
artists = []

# Define colors and makers for each protocol.
colors = ("blue", "orange", "red", "green")
markers = ("^", "v", "X", "1")

# For each of those sources...
for a in range(4):
    # Get the observations that have that protocol.
    obs_from_protocol = [ob for ob in obs if ob["protocol"] == protocols[a]]
    artists.append(plotters.scatter_obs(obs_from_protocol, ax, s=40, marker=markers[a], color=colors[a]))
    # Plot a transparent bubble so overlapping observations stand out.
    plotters.scatter_obs(obs_from_protocol, ax, s=2000, marker=".", color=colors[a], alpha=0.04)

# Add a legend.
ax.legend(artists, protocols, loc="lower center")

# Finalize plot.
ax.set_title("GLOBE observations from selected protocols for {}".format(day))
plt.tight_layout()
plt.show()
