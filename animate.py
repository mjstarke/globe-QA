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
