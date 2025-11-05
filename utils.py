import pandas as pd
import json

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

def preprocess_data(dataset: pd.DataFrame) -> None:

    # Cleaning (dropping nulls)
    
    
