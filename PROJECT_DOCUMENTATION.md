# Land Cost Estimation Using Satellite Images - Complete Project Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Workflow](#architecture--workflow)
3. [Technology Stack](#technology-stack)
4. [File Structure & Purpose](#file-structure--purpose)
5. [Data Collection Pipeline](#data-collection-pipeline)
6. [Machine Learning Pipeline](#machine-learning-pipeline)
7. [Key Features & Components](#key-features--components)
8. [Installation & Setup](#installation--setup)
9. [Usage Guide](#usage-guide)
10. [Model Performance](#model-performance)

---

## 🎯 Project Overview

This is a **Computer Vision and Deep Learning capstone project** that predicts land prices per acre using satellite imagery and various land characteristics. The project combines:

- **Satellite imagery analysis** using Vision Transformers (DINOv2)
- **Traditional ML** (XGBoost) for regression
- **Web scraping** to collect satellite images
- **Feature engineering** with geospatial data

### Problem Statement
Estimate the price per acre of agricultural land in Telangana, India, by analyzing:
- Satellite images of the land
- Location (State, District, Mandal, Village)
- Soil type
- Infrastructure (electricity, water sources, road access)
- Geographic features (latitude, longitude)

---

## 🏗️ Architecture & Workflow

### High-Level Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION PHASE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. N8N Workflow (workflow.json)                                    │
│     │                                                                │
│     ├─► Fetch Land IDs from land_ids.json                          │
│     │                                                                │
│     ├─► API Call to 1acre.in for each land ID                      │
│     │                                                                │
│     └─► Store data in database (dataset4.csv)                       │
│                                                                       │
│  2. Selenium Scraping (main.py + take_ss.py)                       │
│     │                                                                │
│     ├─► Read land IDs from land_ids.json                           │
│     │                                                                │
│     ├─► Extract lat/long from dataset4.csv                         │
│     │                                                                │
│     ├─► Navigate to 1acre.in map view                              │
│     │                                                                │
│     └─► Capture satellite screenshots → images_trial/              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    TRAINING PHASE                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  3. Image Feature Extraction (training.py + utils.py)              │
│     │                                                                │
│     ├─► Load DINOv2 transformer (facebook/dinov2-small)            │
│     │                                                                │
│     ├─► Process all images in images_trial/                        │
│     │                                                                │
│     ├─► Extract 384-dim embeddings per image                       │
│     │                                                                │
│     └─► Attach embeddings to dataset4.csv                          │
│                                                                       │
│  4. Data Preprocessing (utils.py)                                   │
│     │                                                                │
│     ├─► Handle missing values                                       │
│     │                                                                │
│     ├─► Encode categorical features                                │
│     │   ├─ Ordinal: Soil_Type, Approach_Road_Type                 │
│     │   └─ One-Hot: State, District                               │
│     │                                                                │
│     ├─► Keep numerical features as-is                              │
│     │                                                                │
│     └─► Train/validation split (80/20)                             │
│                                                                       │
│  5. Model Training (training.py)                                    │
│     │                                                                │
│     ├─► XGBoost Regressor with GPU support                         │
│     │                                                                │
│     ├─► Train on processed features + embeddings                   │
│     │                                                                │
│     ├─► Evaluate: MAE, RMSE, R², MAPE                             │
│     │                                                                │
│     └─► Save model → price_predictor.pkl                           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    INFERENCE PHASE                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  6. Prediction (price_predictor.pkl)                                │
│     │                                                                │
│     ├─► Load trained model                                          │
│     │                                                                │
│     ├─► Process new land data + satellite image                    │
│     │                                                                │
│     └─► Output: Predicted price per acre                           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.x** - Main programming language
- **PyTorch 2.9.0** - Deep learning framework
- **Transformers 4.50.3** (Hugging Face) - Vision Transformer models
- **XGBoost 3.1.1** - Gradient boosting for regression
- **scikit-learn 1.7.2** - Data preprocessing & metrics
- **Selenium 4.38.0** - Web scraping & screenshot capture

### Supporting Libraries
- **pandas 2.3.3** - Data manipulation
- **Pillow 12.0.0** - Image processing
- **joblib 1.4.2** - Model serialization
- **webdriver-manager 4.0.2** - Chrome driver management

### External Services
- **N8N** - Workflow automation for data collection
- **1acre.in API** - Land data source
- **Mapbox** - Satellite imagery provider (via 1acre.in)

---

## 📁 File Structure & Purpose

### Core Python Scripts

#### **1. main.py** - Data Collection Entry Point
```python
Purpose: Orchestrates the satellite image collection process
Flow:
  1. Load dataset4.csv
  2. Extract land IDs from land_ids.json
  3. Setup Selenium WebDriver
  4. Loop through each land ID
  5. Call extract_and_save_with_id() for each
  6. Save screenshots to images_trial/
```

#### **2. take_ss.py** - Screenshot Capture Module
```python
Key Functions:

sel_setup() → webdriver.Chrome
  - Creates headless Chrome driver
  - Sets window size to 1280x1024
  - Configures options for server environments

extract_and_save_with_id(driver, land_id, data, output_dir)
  - Extracts lat/long from dataset
  - Constructs 1acre.in URL
  - Navigates to map view
  - Executes JavaScript to hide UI elements
  - Captures full-screen satellite image
  - Saves as {land_id}.png
```

**JavaScript Injection Details:**
The script injects JavaScript that:
- Hides headers, navigation bars, and controls
- Makes map canvas full-screen (100vw × 100vh)
- Removes padding/margins
- Ensures pure satellite imagery capture

#### **3. training.py** - Model Training Pipeline
```python
Key Steps:

1. Load dataset4.csv
2. Attach image embeddings (if not already attached)
3. Preprocess data using utils.preprocess_data()
4. Train XGBoost with hyperparameters:
   - n_estimators: 100
   - tree_method: 'hist'
   - device: 'cuda' (if available) or 'cpu'
5. Evaluate on validation set
6. Save model to price_predictor.pkl
7. Generate feature importance plot
```

**Model Evaluation Metrics:**
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **R²** (Coefficient of Determination)
- **MAPE** (Mean Absolute Percentage Error)

#### **4. utils.py** - Utility Functions
```python
Contains functions for:

DATA COLLECTION:
  - extract_lat_long_from_data()
  - extract_ids()

TRANSFORMER MODELS:
  - get_model_and_processor() - Loads/saves DINOv2
  
DATA PROCESSING:
  - attach_embeddings_to_data() - Extracts image features
  - find_and_attach() - Links embeddings to dataset rows
  - preprocess_data() - Full preprocessing pipeline
  - sanitize_feature_names() - Cleans column names
  - haversine() - Calculates geo distances
```

#### **5. tests.py** - Data Exploration Script
```python
Purpose: Debugging and data validation
- Prints data types for all columns
- Checks for missing values
- Tests preprocessing functions
```

#### **6. frontend.py** - Empty (Placeholder for Future UI)

---

### Data Files

#### **dataset4.csv** - Main Dataset
300 rows of land data with columns:
- **Identifiers:** Land_ID, id, createdAt, updatedAt
- **Location:** State, District, Mandal, Village, Latitude, Longitude
- **Land Features:** Soil_Type, Land_Zone_Data, Electricity, Fencing
- **Infrastructure:** Approach_Road_Length, Approach_Road_Type, Water_Source_Data
- **Target:** Price_per_Acre (in crores)
- **Status:** active/inactive

#### **dataset1.csv** - Older Version
256 rows - similar structure, used for comparison

#### **land_ids.json** - Land ID Registry
```json
{
  "land_ids": [5096, 8625, 4953, ..., 499]
}
```
Contains 300 unique land IDs for data collection

#### **workflow.json** - N8N Automation Workflow
Defines the data collection pipeline:
1. **Manual Trigger** - Starts workflow
2. **Fetch Land IDs** - Reads from GitHub
3. **Restructure land ids** - Splits into individual items
4. **Loop over Land IDs** - Batches requests
5. **Wait** - 7-second delay between requests
6. **Fetch Land Details** - API call to 1acre.in
7. **Insert into DB** - Stores in n8n database

---

### Model Files

#### **price_predictor.pkl** - Trained XGBoost Model
Serialized model trained on:
- 384 image embedding features (from DINOv2)
- 10+ structured features (location, soil, infrastructure)

#### **saved_transformer/** - DINOv2 Model Cache
Contains:
- `model.safetensors` (88MB) - Model weights
- `config.json` - Model configuration
- `preprocessor_config.json` - Image preprocessing settings

---

### Image Data

#### **images_trial/** - Satellite Screenshots
~280 PNG images (1280×1024 pixels each)
- Named by Land_ID (e.g., `5096.png`)
- Captured from Mapbox via 1acre.in
- Used for feature extraction

---

## 🔄 Data Collection Pipeline

### Phase 1: N8N Workflow Automation

**Purpose:** Collect structured land data from 1acre.in API

**Process:**
1. Read `land_ids.json` from GitHub repository
2. For each land ID:
   - Wait 7 seconds (rate limiting)
   - Make GET request: `https://prod-be.1acre.in/lands/{land_id}/`
   - Extract relevant fields
   - Transform data:
     ```javascript
     // Price calculation
     Price_per_Acre = crore + (lakh / 100)
     
     // Water source scoring (0-1 scale)
     Water_Source_Data = (
       well * 0.2 + canal * 0.5 + drip * 0.3 +
       sprinkler * 0.1 + bore_well * 0.6 + stream * 0.4
     ) / 1.7
     
     // Land zone counting
     Land_Zone_Data = count(true_values)
     ```
   - Insert into n8n database table

**Output:** Structured CSV file (`dataset4.csv`)

---

### Phase 2: Selenium Screenshot Capture

**Purpose:** Collect satellite imagery for each land parcel

**Workflow (main.py):**
```python
driver = sel_setup()  # Headless Chrome
for land_id in land_ids_list:
    extract_and_save_with_id(driver, land_id, data)
driver.quit()
```

**Screenshot Process (take_ss.py):**
1. Extract lat/long for land_id from dataset
2. Build URL: `https://www.1acre.in/@{lat}-{long}-15m/data-!land{land_id}`
3. Navigate to URL
4. Wait 5 seconds for map load
5. Inject JavaScript to:
   - Hide all UI elements
   - Make map full-screen
   - Remove white bars/padding
6. Wait 2 more seconds
7. Save screenshot: `images_trial/{land_id}.png`

**Error Handling:**
- Catches exceptions per land_id
- Logs errors without stopping process
- Continues to next land_id

---

## 🤖 Machine Learning Pipeline

### Phase 1: Image Feature Extraction

**Model:** facebook/dinov2-small (Vision Transformer)

**Process (attach_embeddings_to_data):**
```python
model, processor = get_model_and_processor(
    model_name='facebook/dinov2-small',
    save_path='./saved_transformer'
)

for image in images_trial/:
    # 1. Load image
    image = Image.open(image_path)
    
    # 2. Preprocess
    inputs = processor(image, return_tensors="pt")
    
    # 3. Extract features (GPU if available)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 4. Get CLS token embedding (384 dims)
    embedding = outputs.last_hidden_state[:, 0, :]
    
    # 5. Attach to dataset row
    dataset.loc[row_index, emb_0:emb_383] = embedding
```

**Why DINOv2?**
- Self-supervised learning (no labels needed)
- Excellent for aerial/satellite imagery
- Captures spatial patterns (fields, roads, water bodies)
- Pre-trained on diverse image datasets

---

### Phase 2: Data Preprocessing

**Missing Value Handling:**
```python
Water_Source_Data    → 0 (no water source)
Approach_Road_Length → 10 meters (default)
Soil_Type            → "black" (most common)
Land_Zone_Data       → 0 (no special zones)
Approach_Road_Type   → "kacha" (unpaved)
```

**Feature Encoding:**

1. **Ordinal Encoding** (preserves order):
   - `Soil_Type`: ["black", "red"] → [0, 1]
   - `Approach_Road_Type`: ["kacha", "formation", "blacktop", "highway_road"]

2. **One-Hot Encoding** (no order):
   - `State`: Creates binary columns per state
   - `District`: Creates binary columns per district
   - Drops first category to avoid multicollinearity

3. **Numerical Features** (kept as-is):
   - Latitude, Longitude
   - Approach_Road_Length
   - Electricity, Fencing
   - Water_Source_Data, Land_Zone_Data
   - emb_0 through emb_383

**Normalization:** None applied (tree-based models don't require it)

**Train/Test Split:**
- 80% training, 20% validation
- Stratified by State (ensures balanced geographic distribution)

---

### Phase 3: Model Training

**Algorithm:** XGBoost (Extreme Gradient Boosting)

**Hyperparameters:**
```python
{
    "n_estimators": 100,      # Number of trees
    "tree_method": 'hist',    # Fast histogram-based method
    "device": "cuda",         # GPU acceleration
    "verbosity": 0            # Suppress logs
}
```

**Why XGBoost?**
- Handles mixed feature types well
- Robust to outliers
- Minimal hyperparameter tuning needed
- Fast training with GPU support
- Provides feature importance

**Training Process:**
1. Load preprocessed data (features + embeddings)
2. Fit model on training set
3. Predict on validation set
4. Calculate metrics
5. Save model to disk

**Feature Importance Analysis:**
- Uses 'gain' metric (improvement in loss)
- Plots top 20 features
- Helps understand what drives land prices

---

### Phase 4: Model Evaluation

**Metrics Explained:**

1. **MAE (Mean Absolute Error)**
   - Average absolute difference between predicted and actual prices
   - In crores (1 crore = 10 million INR)
   - Lower is better

2. **RMSE (Root Mean Squared Error)**
   - Penalizes large errors more than MAE
   - Same units as target (crores)
   - Lower is better

3. **R² (R-squared)**
   - Proportion of variance explained (0 to 1)
   - 0 = no better than mean, 1 = perfect predictions
   - Higher is better

4. **MAPE (Mean Absolute Percentage Error)**
   - Percentage error (scale-independent)
   - Useful for comparing across datasets
   - Lower is better

---

## 🔑 Key Features & Components

### 1. Geospatial Features
- **Latitude & Longitude**: Precise location
- **State/District/Mandal/Village**: Administrative hierarchy
- **Haversine Distance**: For calculating proximity (future use)

### 2. Land Quality Indicators
- **Soil Type**: Black (fertile) vs. Red (less fertile)
- **Water Sources**: Scoring system based on:
  - Bore well (0.6 weight)
  - Canal (0.5 weight)
  - Stream (0.4 weight)
  - Drip irrigation (0.3 weight)
  - Well (0.2 weight)
  - Sprinkler (0.1 weight)

### 3. Infrastructure
- **Electricity**: Binary (0/1)
- **Fencing**: Binary (0/1)
- **Road Access**:
  - Length: Distance to main road
  - Type: Highway > Blacktop > Formation > Kacha (unpaved)

### 4. Special Zones
- **Land Zone Data**: Count of applicable zones (agricultural, residential, etc.)

### 5. Visual Features (from DINOv2)
- 384 dimensions capturing:
  - Terrain patterns
  - Vegetation density
  - Nearby infrastructure
  - Field boundaries
  - Water bodies

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- CUDA-capable GPU (optional, for faster training)
- Chrome browser (for Selenium)
- 4GB+ RAM
- 2GB+ disk space (for models and images)

### Step 1: Clone Repository
```bash
git clone https://github.com/1-shweta-rana/Land-cost-estimation-using-Satellite-images-.git
cd Land-cost-estimation-using-Satellite-images-
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- PyTorch (with CUDA support if available)
- Transformers & DINOv2
- XGBoost
- Selenium & WebDriver Manager
- pandas, scikit-learn, Pillow, etc.

### Step 3: Verify Installation
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

---

## 📖 Usage Guide

### Scenario 1: Collect New Data

#### Step 1: Update land_ids.json
```json
{
  "land_ids": [12345, 67890, ...]
}
```

#### Step 2: Run Data Collection
```bash
python main.py
```
- Downloads satellite images to `images_trial/`
- Takes ~5 minutes for 10 lands
- Requires internet connection

### Scenario 2: Train Model

#### Step 1: Ensure Data is Ready
- `dataset4.csv` exists
- `images_trial/` contains satellite images

#### Step 2: Run Training
```bash
python training.py
```

**Output:**
```
Is GPU Available: True
Loading model from ./saved_transformer
Successfully loaded model from ./saved_transformer
Added embeddings to 5096
Added embeddings to 8625
...
✅ Data cleaned and preprocessed. Shape: (240, 394)
Model not found in current working directory, training new model...
Model has been trained
Do you want to save the model? (y/n): y
Model has been saved

MAE: 0.234
RMSE: 0.312
R²: 0.856
MAPE: 18.45%
```

#### Step 3: Review Feature Importance
- A plot will display showing top 20 features
- Helps identify what matters most for pricing

### Scenario 3: Make Predictions

```python
import joblib
import pandas as pd
from utils import preprocess_data, attach_embeddings_to_data

# Load model
model = joblib.load("price_predictor.pkl")

# Prepare new land data
new_land = pd.read_csv("new_land_data.csv")

# Extract embeddings from satellite image
attach_embeddings_to_data(
    image_path="./new_images/",
    dataset=new_land,
    model_name='facebook/dinov2-small',
    save_path='./saved_transformer'
)

# Preprocess
X_new = preprocess_data(new_land)

# Predict
predicted_price = model.predict(X_new)
print(f"Estimated price: ₹{predicted_price[0]:.2f} crore per acre")
```

---

## 📊 Model Performance

### Expected Metrics (on validation set)
- **MAE**: 0.15 - 0.30 crore
- **RMSE**: 0.25 - 0.40 crore
- **R²**: 0.80 - 0.90
- **MAPE**: 15% - 25%

### Feature Importance Insights
Based on feature importance analysis, the most influential factors are likely:
1. **Location features** (District, Latitude, Longitude)
2. **Image embeddings** (visual patterns from satellite)
3. **Soil type** (black vs. red)
4. **Water source score**
5. **Road infrastructure**

### Limitations
1. **Geographic scope**: Trained only on Telangana, India
2. **Temporal**: Prices from Nov 2025 snapshot
3. **Sample size**: ~300 land parcels
4. **Image quality**: Depends on satellite imagery resolution
5. **Market dynamics**: Doesn't capture real-time market trends

---

## 🎓 Learning Outcomes

This project demonstrates:
1. ✅ End-to-end ML pipeline (data → model → inference)
2. ✅ Computer vision with transformers (DINOv2)
3. ✅ Web scraping with Selenium
4. ✅ Feature engineering for tabular + image data
5. ✅ Model evaluation & interpretation
6. ✅ Workflow automation (N8N)
7. ✅ Production ML practices (model serialization, GPU usage)

---

## 🔮 Future Enhancements

1. **Frontend UI** (frontend.py)
   - Upload land details
   - Display predicted price
   - Show feature importance

2. **Model Improvements**
   - Try larger transformers (DINOv2-base, DINOv2-large)
   - Ensemble methods (XGBoost + LightGBM)
   - Time-series features (price trends)

3. **Data Expansion**
   - More states/districts
   - Historical price data
   - Weather patterns
   - Crop yield data

4. **Deployment**
   - REST API (FastAPI)
   - Dockerization
   - Cloud hosting (AWS/GCP)

5. **Explainability**
   - SHAP values for predictions
   - Attention visualization for images
   - Regional pricing heatmaps

---

## 📝 Notes

- All prices in **Indian Rupees (₹), crores** (1 crore = 10 million)
- Images are **Mapbox satellite tiles** via 1acre.in
- Model trained on **CPU/GPU** (auto-detected)
- Selenium runs in **headless mode** (no browser window)

---

## 🤝 Credits

- **DINOv2**: Meta AI Research
- **XGBoost**: DMLC
- **1acre.in**: Land data source
- **N8N**: Workflow automation
- **Mapbox**: Satellite imagery

---

**Last Updated:** November 2025  
**Status:** ✅ Fully Functional Training Pipeline
