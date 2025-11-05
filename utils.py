import pandas as pd
import json
import os
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import torch

def extract_lat_long_from_data(dataset: pd.DataFrame, land_id:int) -> dict:

    row = dataset.loc[dataset["Land_ID"] == land_id, ["Latitude", "Longitude"]]
    res = dict()

    if row.empty:
        print(f"Warning: Land_ID {land_id} not found in the dataset")
        return res
    
    lat = row["Latitude"].iloc[0]
    lat = round(lat, 2)
    long = row["Longitude"].iloc[0]
    long = round(long, 2)

    res["lat"] = lat
    res["long"] = long

    return res

def extract_ids(input_file:str = "./land_ids.json") -> list:
    land_ids = dict()
    with open(input_file, 'r') as f:
        land_ids = json.load(f)
    land_ids_list = list(set(land_ids["land_ids"]))
    return land_ids_list

def get_model_and_processor(model_name: str, save_path : str):
    
    if not os.path.exists(save_path):
        print("Can't find transformer locally...")
        model = AutoModel.from_pretrained(model_name)
        processor = AutoImageProcessor.from_pretrained(model_name)
        
        model.save_pretrained(save_path)
        processor.save_pretrained(save_path)
        print(f"Saved model to {save_path}")
    else:
        print(f"Loading model from {save_path}")
        model = AutoModel.from_pretrained(save_path)
        processor = AutoImageProcessor.from_pretrained(save_path)
        print(f"Successfully loaded model from {save_path}")

    return model,processor

def find_and_attach(image_embedding: torch.Tensor, dataset: pd.DataFrame, image) -> None:

    image_id = image.split(".")[0]
    row = dataset["Land_ID"] == image_id
    embedding_np = image_embedding.cpu().numpy() if image_embedding.is_cuda else image_embedding.numpy()
    dataset.loc(row, 'embedding') = [embedding_np]

def attach_embeddings_to_data(image_path: str, dataset: pd.DataFrame, model_name: str, save_path: str) -> None:

    print(f"Is GPU Available: {torch.cuda.is_available()}")
    model, processor = get_model_and_processor(model_name, save_path)
    for image in os.listdir(image_path):

        curr_image_path = os.path.join(image_path, image)
        curr_image = Image.open(curr_image_path)
        inputs = processor(curr_image, return_tensors = "pt")
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        image_embedding = outputs.last_hidden_state[:, 0, ::]

        find_and_attach(image_embedding, dataset, image)
        print(f"Attached embedding for {image}")

# def preprocess_data(dataset: pd.DataFrame) -> None:

    #Cleaning (dropping nulls)
    #remove rows without land_id
    #check for road type if its affecting the price 
    #check for null values in soil type etc, fill missing values or remove
    #come up with most affecting attributes and preprocess accordingly 
    #remove if any unwanted attribute present 
    
    
