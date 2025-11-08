import transformers
import torch
import xgboost
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import os
import pandas as pd
from utils import preprocess_data, attach_embeddings_to_data, clean_data
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
import joblib
import re

dataset = pd.read_csv('./dataset1.csv')
dataset_cleaned = clean_data(dataset)
transformer_model_name = 'facebook/dinov2-small'
save_path = './saved_transformer'
image_path = './images'


attach_embeddings_to_data(image_path, dataset, transformer_model_name, save_path)
x_train, x_valid, y_train, y_valid = preprocess_data(dataset)

hyperparams = {
    "n_estimators":200,
    "tree_method": 'hist',
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "verbosity":0
}

pattern = re.compile(r".*\.pkl$", re.IGNORECASE)
pkl_files = [i for i in os.listdir(".") if pattern.match(i)]

if not pkl_files:

    print("Model not found in current working directory, training new model...")
    model = XGBRegressor(**hyperparams)
    model.fit(x_train, y_train)
    print("Model has been trained")
    
    response = input("Do you want to save the model? (y/n)").lower().strip()
    if response == "y":
        joblib.dump(model, filename="price_predictor.pkl")
        print("Model has been saved")
    else:
        print("Model has not been saved")

else:
    path = pkl_files[0]
    model = joblib.load(path)
    print("Model has been loaded from working directory")


preds = model.predict(x_valid)
mae = mean_absolute_error(y_valid, preds)
print(f"{mae=}")












