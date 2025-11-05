import transformers
import torch
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import os
import pandas as pd
from utils import preprocess_data

dataset = pd.read_csv('./dataset1.csv')

model_name = 'facebook/dinov2-small'
print(f"Is GPU Available: {torch.cuda.is_available()}")
save_path = './saved_transformer'

if not os.path.exists('./saved_transformer'):
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

image_path = './images'





