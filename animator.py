import imageio
import os
from tqdm import tqdm

for t in ["GLOBE"]:
    input_dir = "/Users/mjstarke/Documents/GLOBE_B/images_ggc_x0037/"
    output = "/Users/mjstarke/Documents/GLOBE_B/ggc_0037.mp4"
    fps = 1

    frame_files = []
    all_files = os.listdir(input_dir)
    file_name_list = ["{:0>4.0f}.png".format(t) for t in range(50)]

    for file in file_name_list:
        complete_path = os.path.join(input_dir, file)
        frame_files.append(complete_path)

    writer = imageio.get_writer(output, fps=fps)

    for im in tqdm(frame_files, desc="Writing frames"):
        writer.append_data(imageio.imread(im))
    print("--- Closing writer...")
    writer.close()
    print("--- Script ending normally.")
