import pandas as pd
import json
import os
from transformers import AutoModel, AutoImageProcessor
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
        model = AutoModel.from_pretrained(save_path)
        processor = AutoImageProcessor.from_pretrained(save_path)

    return model,processor


def preprocess_data(dataset: pd.DataFrame) -> None:

    #Cleaning (dropping nulls)
    #remove rows without land_id
    #check for road type if its affecting the price 
    #check for null values in soil type etc, fill missing values or remove
    #come up with most affecting attributes and preprocess accordingly 
    #remove if any unwanted attribute present 
    
    
