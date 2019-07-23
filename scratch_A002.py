from scratch_vars import *

obs = tools.parse_json(fpSC)

vals = {"0 photos": 0, "1 photo": 0, "2 photos": 0, "3 photos": 0, "4 photos": 0, "5 photos": 0, "6 photos": 0}

for ob in tqdm(obs, desc="Sifting observations"):
    photos = 0
    for direction in ["North", "East", "South", "West", "Upward", "Downward"]:
        photos += 1 if ob.soft_get(direction + "PhotoUrl") is not None else 0

    ob.photos = photos

    vals["{} photo{}".format(photos, "s" if photos != 1 else "")] += 1

total = sum(vals[k] for k in vals)

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111)
ax.pie([vals[k] for k in vals], labels=["{} ({:.2%})".format(k, v / total) for k, v in vals.items()],
       labeldistance=None, colors=["#dddddd", "#bbccbb", "#99bb99", "#77aa77", "#559988", "#338899", "#1177aa"])
ax.legend()
plt.show()