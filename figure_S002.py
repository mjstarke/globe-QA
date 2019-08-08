from figure_common import *

fp = tools.download_from_api(["sky_conditions"], datetime(2017, 1, 1), datetime(2019, 5, 31))
obs = tools.parse_json(fp)

for loop in range(2):
    # Prepare dict to collect plotted values.
    vals = {"0 photos": 0, "1 photo": 0, "2 photos": 0, "3 photos": 0, "4 photos": 0, "5 photos": 0, "6 photos": 0}
    vals_2 = {"North": 0, "East": 0, "South": 0, "West": 0, "Upward": 0, "Downward": 0}

    # For each observation...
    for ob in tqdm(obs, desc="Sifting observations"):
        # Count how many photos are included.
        photos = len(ob.photo_urls)

        vals["{} photo{}".format(photos, "s" if photos != 1 else "")] += 1

        if photos == 5:
            for direction in vals_2.keys():
                if direction not in ob.photo_urls.keys():
                    vals_2[direction] += 1

    # Find total number of observations for calculating percentages for slice labels.
    total = sum(vals[k] for k in vals)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111)
    ax.pie([vals[k] for k in vals], labels=["{} ({:.2%})".format(k, v / total) for k, v in vals.items()],
           labeldistance=None, colors=["#dddddd", "#bbccbb", "#99bb99", "#77aa77", "#559988", "#338899", "#1177aa"])

    ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds{}\n"
                 "Number of photos in each observation".format(" (Observer only)" if loop == 1 else ""))

    plt.tight_layout()
    plt.savefig("img/S002_Jan2017-May2019_global_GLOBE{}-SC_pie_concurrent-photos-no-legend.png"
                "".format("-GO" if loop == 1 else ""))
    ax.legend()
    plt.savefig("img/S002_Jan2017-May2019_global_GLOBE{}-SC_pie_concurrent-photos.png"
                "".format("-GO" if loop == 1 else ""))

    total = sum(vals_2[k] for k in vals_2)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111)
    ax.pie([vals_2[k] for k in vals_2], labels=["{} ({:.2%})".format(k, v / total) for k, v in vals_2.items()],
           labeldistance=None)

    ax.set_title("Jan 2017 - May 2019 / Global / GLOBE Clouds{}\n"
                 "Direction omitted when 5 photos are taken".format(" (Observer only)" if loop == 1 else ""))

    plt.tight_layout()
    plt.savefig("img/S002_Jan2017-May2019_global_GLOBE{}-SC_pie_missing-sixth-photo-no-legend.png"
                "".format("-GO" if loop == 1 else ""))
    ax.legend()
    plt.savefig("img/S002_Jan2017-May2019_global_GLOBE{}-SC_pie_missing_sixth_photo.png"
                "".format("-GO" if loop == 1 else ""))

    # On the second loop, only Observer observation will be processed.
    obs = [ob for ob in obs if ob.is_from_observer]
