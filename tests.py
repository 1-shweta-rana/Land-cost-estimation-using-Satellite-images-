import pandas as pd
import os
from PIL import Image

dataset = pd.read_csv("./dataset1.csv")
print(dataset.columns)
image_path = './images'

for image in os.listdir(image_path):

    curr_image_path = os.path.join(image_path, image)
    curr_image = Image.open(curr_image_path)
    image_id = image.split(".")[0]
    print(image_id)
    # inputs = processor(curr_image, return_tensors = "pt")