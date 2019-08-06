from datetime import date, datetime
from globeqa import tools

# Download and parse one month of observations.
filepath = tools.download_from_api(["sky_conditions"], date(2019, 5, 1), date(2019, 5, 31))
obs = tools.parse_json(filepath)

total = len(obs)
print("There are {} observations in total. Of those:".format(total))

obs_dust = [ob for ob in obs if "Dust" in ob]
print("   {:6.2%} ({:5}) report dust.".format(len(obs_dust) / total, len(obs_dust)))

obs_scattered = [ob for ob in obs if ob.tcc == "scattered"]
print("   {:6.2%} ({:5}) report scattered clouds.".format(len(obs_scattered) / total, len(obs_scattered)))

obs_four_day = tools.filter_by_datetime(obs, datetime(2019, 5, 7), datetime(2019, 5, 10))
print("   {:6.2%} ({:5}) are between 7 May 2019 and 10 May 2019.".format(len(obs_four_day) / total, len(obs_four_day)))

obs_observer = [ob for ob in obs if ob.is_from_observer]
print("   {:6.2%} ({:5}) are from the GLOBE Observer app.".format(len(obs_observer) / total, len(obs_observer)))

obs_3photos = [ob for ob in obs if len(ob.photo_urls) >= 3]
print("   {:6.2%} ({:5}) have at least 3 photos.".format(len(obs_3photos) / total, len(obs_3photos)))

obs_3obscurations = [ob for ob in obs if len(ob.obscurations) >= 3]
print("   {:6.2%} ({:5}) report at least 3 obscurations.".format(len(obs_3obscurations) / total, len(obs_3obscurations)))

obs_arctic = [ob for ob in obs if ob.lat >= 66.5]
print("   {:6.2%} ({:5}) are north of the Arctic Circle.".format(len(obs_arctic) / total, len(obs_arctic)))
