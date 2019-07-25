from scratch_vars import *

obs = tools.parse_json(fpSC)

for ob in tqdm(obs, desc="Sifting observations"):
    photos = 0
    for direction in ["North", "East", "South", "West", "Upward", "Downward"]:
        photos += 1 if ob.soft_get(direction + "PhotoUrl") is not None else 0

    ob.photos = photos

obs = [ob for ob in obs if ob.photos == 5]

vals = {"North": 0, "East": 0, "South": 0, "West": 0, "Upward": 0, "Downward": 0}

for ob in obs:
    for direction in ["North", "East", "South", "West", "Upward", "Downward"]:
        if ob.soft_get(direction + "PhotoUrl") is None:
            vals[direction] += 1
            break


total = sum(vals[k] for k in vals)

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111)
ax.pie([vals[k] for k in vals], labels=["{} ({:.2%})".format(k, v / total) for k, v in vals.items()],
       labeldistance=None)
ax.legend()
ax.set_title("Jan 2017 - May 2019 global GLOBE\n"
             "Direction of missing photo for observations with 5 photos")
plt.tight_layout()
plt.savefig("img/S015_Jan2017-May2019_global_GLOBE_pie_missing_photo.png")
