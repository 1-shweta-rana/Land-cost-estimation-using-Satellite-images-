import pandas as pd
#import os
#from PIL import Image
# from utils import attach_embeddings_to_data, pre
#import torch
from utils import preprocess_data
dataset = pd.read_csv("./dataset4.csv")
# preprocess_data(dataset)
# dataset.to_csv("processed_dataset.csv", index=False)

# print("✅ Processed dataset saved as 'processed_dataset.csv'")
for i in dataset.columns:
    print(f"{i}: {dataset[i].dtype}")
print("Rows before cleaning:", len(dataset))
print("Missing Land_ID:", dataset["Land_ID"].isna().sum())
print("Missing Price_per_Acre:", dataset["Price_per_Acre"].isna().sum())

# transformer_model_name = 'facebook/dinov2-small'
# save_path = './saved_transformer'
# image_path = './images'

# attach_embeddings_to_data(image_path, dataset, transformer_model_name, save_path)

# print(dataset.head())

#print(torch.cuda.is_available())



    # missing_soil = dataset[dataset['Soil_Type'].isnull() | (dataset['Soil_Type'].astype(str).str.strip() == '')].copy()
    # known_soil = dataset[dataset['Soil_Type'].notnull() & (dataset['Soil_Type'].astype(str).str.strip() != '')].copy()

    # for idx, row in missing_soil.iterrows():
    #     lat, lon = row['Latitude'], row['Longitude']
    #     if pd.isna(lat) or pd.isna(lon) or known_soil.empty:
    #         continue

    #     # Compute distances safely
    #     distances = known_soil.apply(
    #         lambda x: haversine(lat, lon, x['Latitude'], x['Longitude']), axis=1
    #     )
    #     nearest_idx = distances.idxmin()
    #     nearest_dist = distances.min()
    #     distance_threshold: float = 
    #     if nearest_dist <= distance_threshold:
    #         dataset.at[idx, 'Soil_Type'] = known_soil.at[nearest_idx, 'Soil_Type']
