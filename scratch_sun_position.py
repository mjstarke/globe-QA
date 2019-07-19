from datetime import datetime, timedelta
import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u

print("Setting location...")
loc = coord.EarthLocation(lon=100.0 * u.deg,
                          lat=30.0 * u.deg)
print("Setting time...")
now = Time.now()

print("Setting alt azimuth...")
altaz = coord.AltAz(location=loc, obstime=now)

print("Getting sun coords...")
sun = coord.get_sun(now)

print(sun.transform_to(altaz).alt)

