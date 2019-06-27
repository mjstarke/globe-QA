"""
Download and parse all cloud observations for 2019 May, then print the relative frequency of each value for CloudCover
and plot a pie chart.
"""

from datetime import date
from globeqa import tools, plotters

# Download from the API.  Won't re-download if the file already exists locally.
path = tools.download_from_api(["sky_conditions"], date(2019, 5, 1), date(2019, 5, 31), check_existing=True)

# Parse the downloaded file.
obs = tools.parse_json(path)

# Create a dictionary that contains category=count pairs for each cloud cover category.
d = tools.find_all_values(obs, "CloudCover")

# Specify the key ordering for the table and pie chart - otherwise, the order is alphabetical.
key_order = ["none", "clear", "isolated", "scattered", "broken", "overcast", "obscured"]

# Print the summary table.
tools.pretty_print_dictionary(d, sorting=key_order)

# Create the pie chart.
ax = plotters.plot_dict_pie(d, keys=key_order, colors=[
    "#ff8800", "#8888ff", "#7777dd", "#6666bb", "#555599", "#444477", "#333366"
])

ax.set_title("CloudCovers for all 2019 May SC observations")
