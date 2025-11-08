import pandas as pd
import json
import os
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder,OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import re
from math import radians, sin, cos, sqrt, atan2

#------------------------------DATA COLLECTION FUNCTIONS START------------------------------------
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
#------------------------------DATA COLLECTION FUNCTIONS END------------------------------------

#------------------------------HF MODELS FUNCTIONS START----------------------------------------
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
#------------------------------HF MODELS FUNCTIONS END----------------------------------------

#------------------------------DATA PROCESSING FUNCTIONS START----------------------------------------
def find_and_attach(image_embedding: torch.Tensor, dataset: pd.DataFrame, image) -> None:

    image_id = image.split(".")[0].strip()
    image_id = int(image_id)
    # print(image_id)
    embedding_np = image_embedding.cpu().numpy() if image_embedding.is_cuda else image_embedding.numpy()

    if embedding_np.ndim > 1:
        embedding_1d = embedding_np.flatten()
    else:
        embedding_1d = embedding_np

    matching_rows = dataset[dataset["Land_ID"] == image_id]

    if not matching_rows.empty:
        row_index = matching_rows.index[0]

        emb_cols = [f"emb_{i}" for i in range(len(embedding_1d))]

        for col in emb_cols:
            if col not in dataset.columns:
                dataset[col] = None
        
        dataset.loc[row_index, emb_cols] = embedding_1d
        print(f"Added embeddings to {image_id}")
    else:
        print("Couldn't add embeddings")


def attach_embeddings_to_data(image_path: str, dataset: pd.DataFrame, model_name: str, save_path: str) -> None:

    print(f"Is GPU Available: {torch.cuda.is_available()}")
    model, processor = get_model_and_processor(model_name, save_path)
    for image in os.listdir(image_path):
        curr_image_path = os.path.join(image_path, image)
        curr_image = Image.open(curr_image_path)

        device = "cuda" if torch.cuda.is_available() else "cpu"

        model = model.to(device)
        inputs = processor(curr_image, return_tensors = "pt").to(device)

        with torch.no_grad():
            outputs = model(**inputs)
        
        image_embedding = outputs.last_hidden_state[:, 0, :]
        # print(len(image_embedding))
        find_and_attach(image_embedding, dataset, image)
    
    print("Added embeddings for the entire dataset")

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans messy CSV data for consistent model preprocessing.
    Fixes quote/newline issues, trims whitespace, and drops bad rows.
    """

    # 1️⃣ Clean string columns: remove weird quotes, stray newlines, and excess spaces
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = (
                df[col]
                .astype(str)
                .replace({r'"\s*\n\s*"': '"0"'}, regex=True)  # fix "0\n"
                .replace({r'\s+': ' '}, regex=True)           # normalize whitespace
                .replace({r'^"+|"+$': ''}, regex=True)        # remove leading/trailing quotes
                .str.strip()
            )

    # 2️⃣ Drop fully empty or null rows
    df = df.dropna(how="all")

    # 3️⃣ Remove Unnamed garbage columns (CSV parsing leftovers)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # 4️⃣ Drop rows where Land_ID is missing or blank
    if "Land_ID" in df.columns:
        df = df[df["Land_ID"].notna() & (df["Land_ID"].astype(str).str.strip() != '')]

    # 5️⃣ Convert numeric-looking columns to proper numeric dtype
    for col in df.columns:
        # Heuristic: if half or more values look numeric, try converting
        if df[col].astype(str).str.match(r"^[\d\.\-]+$").sum() > len(df) * 0.5:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df.reset_index(drop=True, inplace=True)
    return df

def sanitize_feature_names(columns):
    return [re.sub(r"[\[\]<>]", "_", c) for c in columns]



def haversine(lat1, lon1, lat2, lon2):
    """Compute the Haversine distance (km) between two lat/lon points."""
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a)) * R

def preprocess_data(dataset: pd.DataFrame):

    # --- CLEANING STAGE ---
    dataset = clean_data(dataset)

    # --- BASIC DROPS ---
    dataset.dropna(subset=["Land_ID"], inplace=True)
    useless_cols = ["createdAt", "updatedAt", "id", "Status", "Longitude", "Latitude"]

    for col in useless_cols:
        if col in dataset.columns:
            dataset = dataset.drop(columns=[col])
        else:
            print(f"Column {col} not found in dataset")

    # --- FILL MISSING VALUES ---
    dataset["Water_Source_Data"].fillna(0, inplace=True)
    dataset["Approach_Road_Length"].fillna(10, inplace=True)

    missing_soil = dataset[dataset['Soil_Type'].isnull() | (dataset['Soil_Type'].astype(str).str.strip() == '')].copy()
    known_soil = dataset[dataset['Soil_Type'].notnull() & (dataset['Soil_Type'].astype(str).str.strip() != '')].copy()

    for idx, row in missing_soil.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        if pd.isna(lat) or pd.isna(lon) or known_soil.empty:
            continue

        # Compute distances safely
        distances = known_soil.apply(
            lambda x: haversine(lat, lon, x['Latitude'], x['Longitude']), axis=1
        )
        nearest_idx = distances.idxmin()
        nearest_dist = distances.min()
        distance_threshold: float = 50.0
        if nearest_dist <= distance_threshold:
            dataset.at[idx, 'Soil_Type'] = known_soil.at[nearest_idx, 'Soil_Type']

    dataset["Land_Zone_Data"].fillna(0, inplace=True)
    dataset["Approach_Road_Type"].fillna("kacha", inplace=True)

    # --- SPLIT FEATURES & TARGET ---
    X = dataset.drop(columns=["Price_per_Acre"])
    y = dataset["Price_per_Acre"]

    # --- DEFINE COLUMN TYPES ---
    cols_to_ord_encode = ["Soil_Type", "Approach_Road_Type"]
    cols_to_one_hot_encode = ["State", "District", "Mandal", "Village"]

    all_categorical_cols = cols_to_ord_encode + cols_to_one_hot_encode
    numerical_cols = [col for col in X.columns if col not in all_categorical_cols]

    # --- PIPELINES ---
    ord_pipeline = Pipeline([
        ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
    ])

    one_hot_pipeline = Pipeline([
        ('encoder', OneHotEncoder(handle_unknown='ignore', drop='first', sparse_output=False))
    ])

    num_pipeline = Pipeline([
        ('scaler', StandardScaler())
    ])

    # --- COLUMN TRANSFORMER ---
    preprocessor = ColumnTransformer(
        transformers=[
            ('ordinal', ord_pipeline, cols_to_ord_encode),
            ('onehot', one_hot_pipeline, cols_to_one_hot_encode),
            ('numeric', num_pipeline, numerical_cols)
        ],
        remainder='drop'
    )

    # --- TRAIN/VALIDATION SPLIT ---
    x_train, x_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=100
    )

    # --- FIT + TRANSFORM ---
    preprocessor.fit(x_train)
    x_train_processed = preprocessor.transform(x_train)
    x_valid_processed = preprocessor.transform(x_valid)

    # --- CONVERT BACK TO DATAFRAMES ---
    feature_names = preprocessor.get_feature_names_out()
    x_train_processed = pd.DataFrame(x_train_processed, columns=feature_names, index=x_train.index)
    x_valid_processed = pd.DataFrame(x_valid_processed, columns=feature_names, index=x_valid.index)

    # --- DEBUG INFO ---
    print(f"✅ Data cleaned and preprocessed. Shape: {x_train_processed.shape}")
    print("All features converted to numeric (float64):")
    print(x_train_processed.dtypes.value_counts())
    x_train_processed.columns = sanitize_feature_names(x_train_processed.columns)
    x_valid_processed.columns = sanitize_feature_names(x_valid_processed.columns)
    
    return x_train_processed, x_valid_processed, y_train, y_valid
    
#------------------------------DATA PROCESSING FUNCTIONS END----------------------------------------
    
