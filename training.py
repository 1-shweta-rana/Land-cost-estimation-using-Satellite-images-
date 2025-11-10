import transformers
import torch
import xgboost
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import os
import pandas as pd
from utils import preprocess_data, attach_embeddings_to_data
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, root_mean_squared_error, r2_score
from xgboost import XGBRegressor
import joblib
import re
import warnings
import shap
import matplotlib.pyplot as plt

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.filterwarnings(action="ignore", category=pd.errors.SettingWithCopyWarning)

# dataset_path = "./dataset2.csv"
# dataset_cleaned = clean_data(dataset_path)
dataset_cleaned = pd.read_csv("./dataset4.csv")
transformer_model_name = 'facebook/dinov2-small'
save_path = './saved_transformer'
image_path = './images_trial'


attach_embeddings_to_data(image_path, dataset_cleaned, transformer_model_name, save_path)
x_train, x_valid, y_train, y_valid = preprocess_data(dataset_cleaned)

hyperparams = {
    "n_estimators":100,
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
rmse = root_mean_squared_error(y_valid, preds)
r2 = r2_score(y_valid, preds)
mape = mean_absolute_percentage_error(y_valid, preds) * 100

print(f"MAE: {mae:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"R²: {r2:.3f}")
print(f"MAPE: {mape:.2f}%")

# Extract feature importances based on average gain
booster = model.get_booster()
importance = booster.get_score(importance_type='gain')

# Convert to DataFrame
importance_df = (
    pd.DataFrame(list(importance.items()), columns=["Feature", "Importance"])
    .sort_values(by="Importance", ascending=False)
)

# Plot top 20 important features
plt.figure(figsize=(10, 6))
plt.barh(importance_df["Feature"].head(20)[::-1], importance_df["Importance"].head(20)[::-1])
plt.xlabel("Feature Importance (Gain)")
plt.title("Top 20 Most Influential Features in Land Price Prediction")
plt.tight_layout()
plt.show()









