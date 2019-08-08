from contextlib import closing
from datetime import datetime, timedelta
from globeqa import tools
from os import mkdir
from shutil import copyfileobj
from tqdm import tqdm
from urllib.request import urlopen

# Whether to download photos.
DOWNLOAD = False
# The folder to download photos to.
DOWNLOAD_TO = "photos"
# Whether to exclude "downward" photos.
EXCLUDE_DOWNWARD = True

# Set endpoints of data to collect - in this case, the last 3 days (including today).
start_date = datetime.today().date() - timedelta(2)
end_date = datetime.today().date()

# Download and parse observations.
fp = tools.download_from_api(["sky_conditions"], start_date, end_date)
obs = tools.parse_json(fp)

# Filter to observations reporting obscured sky.
obs = [ob for ob in obs if ob.tcc == "obscured"]

# Prepare to collect photos.
photos = {}

# For each observation...
for ob in obs:
    # For each photo (direction and URL) in the observation...
    for direction, url in ob.photo_urls.items():
        # If the direction is not downward (or if we're not excluding downward anyway)...
        if direction != "Downward" or not EXCLUDE_DOWNWARD:
            # If the URL is valid (e.g., not "pending approval" or "rejected")...
            if url.startswith("http"):
                # Set a key in the dictionary that combines the observation's ID and the photo's direction with the URL
                # as the value.
                key = "{}-{}".format(ob.id, direction)
                photos[key] = url

if DOWNLOAD:
    # Try to make the directory specified at top.
    try:
        mkdir(DOWNLOAD_TO)
    except FileExistsError:
        pass

    # For each photo...
    for photo_name, photo_url in tqdm(photos.items(), desc="Downloading photos"):
        # Open the photo URL...
        with closing(urlopen(photo_url)) as r:
            # Open a local file...
            with open("{}/{}.jpg".format(DOWNLOAD_TO, photo_name), 'wb') as f:
                # ...and copy.
                copyfileobj(r, f)
