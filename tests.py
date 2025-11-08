import pandas as pd
#import os
#from PIL import Image
# from utils import attach_embeddings_to_data, pre
#import torch
from utils import preprocess_data
dataset = pd.read_csv("./dataset1.csv")
preprocess_data(dataset)
dataset.to_csv("processed_dataset.csv", index=False)

print("✅ Processed dataset saved as 'processed_dataset.csv'")
print(dataset)


# transformer_model_name = 'facebook/dinov2-small'
# save_path = './saved_transformer'
# image_path = './images'

# attach_embeddings_to_data(image_path, dataset, transformer_model_name, save_path)

# print(dataset.head())

#print(torch.cuda.is_available())