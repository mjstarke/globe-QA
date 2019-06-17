# /Users/mjstarke/Documents/GLOBE Task A/sky_conditions_20170101_20190531.json
# def test(fp: str, maximum: int = None, ret: bool = False):
#     obs = parse_json(fp)
#     if maximum is not None:
#         obs = obs[:maximum]
#     land = prepare_earth_geometry()
#     do_quality_check(obs, land)
#     flag_counts = dict(total=len(obs))
#     print("--- Enumerating flags...")
#     for ob in obs:
#         for flag in ob.flags:
#             try:
#                 flag_counts[flag] += 1
#             except KeyError:
#                 flag_counts[flag] = 1
#
#     print("--- Flag counts are as follows:")
#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(flag_counts)
#     return obs if ret else None

import globeqa

sc_flags = {'CI': 38432,
            'CX': 2367,
            'DM': 4219,
            'ER': 1240,
            'HC': 2113,
            'HO': 22,
            'LW': 25108,
            'NR': 482,
            'OM': 468,
            'OO': 342,
            'OT': 2200,
            'OX': 178,
            'total': 441707}
lc_flags = {'DM': 3, 'ER': 4, 'LW': 123, 'total': 3510}
th_flags = {'DM': 216, 'ER': 1, 'LW': 94, 'total': 4308}
mm_flags = {'DM': 6, 'ER': 30, 'LW': 450, 'MR': 48, 'total': 12431}

for group in [lc_flags, mm_flags]:
    for k, v in group.items():
        print("{}  {}  {:.2%}".format(k, v, v / group["total"]))


import os
import imageio

input_dir = "/Users/mjstarke/Documents/GLOBE Task B/images/"
start = "GG"
output = "/Users/mjstarke/Documents/GLOBE Task B/GG.mp4"
fps = 1

frame_files = []
all_files = os.listdir(input_dir)

for i in range(100):
    found = False
    for file in all_files:
        if file.startswith("{}{:0>4}".format(start, i)):
            complete_path = os.path.join(input_dir, file)
            frame_files.append(complete_path)
            found = True
            break
    if not found:
        break

writer = imageio.get_writer(output, fps=fps)

for im in frame_files:
    print("... Writing frame {}...".format(im))
    writer.append_data(imageio.imread(im))
print("... Closing writer...")
writer.close()
print("... Script ending normally.")
