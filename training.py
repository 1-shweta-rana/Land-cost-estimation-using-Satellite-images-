import transformers
import torch
import xgboost
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import os
import pandas as pd
from utils import preprocess_data, attach_embeddings_to_data
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

dataset = pd.read_csv('./dataset1.csv')

transformer_model_name = 'facebook/dinov2-small'
save_path = './saved_transformer'
image_path = './images'

preprocess_data(dataset)
attach_embeddings_to_data(image_path, dataset, transformer_model_name, save_path)


print(dataset.head())

# Training
X = dataset.drop(columns=["Price_per_Acre"])
y = dataset["Price_per_Acre"]

x_train, x_valid, y_train, y_valid = train_test_split(X, y, stratify=y)

hyperparams = {
    "n_estimators":100,
    "device":"cuda" if torch.cuda.is_available() else "cpu"
}

model = XGBRegressor(**hyperparams)
model.fit(x_train, y_train)
preds = model.predict(x_valid)

mae = mean_absolute_error(y_valid, preds)
print(f"{mae=}")











