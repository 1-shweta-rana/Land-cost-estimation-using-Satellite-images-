# 🔄 Workflow & Architecture Explanation

## 📋 Table of Contents
1. [N8N Workflow Diagram](#n8n-workflow-diagram)
2. [Data Collection Flow](#data-collection-flow)
3. [Image Processing Flow](#image-processing-flow)
4. [Training Pipeline Flow](#training-pipeline-flow)
5. [Component Interactions](#component-interactions)

---

## 🎯 N8N Workflow Diagram (workflow.json)

### Visual Representation

```
START
  ↓
┌──────────────────────┐
│  Manual Trigger      │ ← User initiates workflow
└──────────────────────┘
  ↓
┌──────────────────────┐
│ Fetch Land ID's      │ ← GET https://raw.githubusercontent.com/.../land_ids.json
└──────────────────────┘
  ↓
┌──────────────────────┐
│ Restructure land ids │ ← Transform: {"land_ids": [1,2,3]} → [{1}, {2}, {3}]
└──────────────────────┘
  ↓
┌──────────────────────┐
│ Loop over Land IDs   │ ← SplitInBatches (processes one at a time)
└──────────────────────┘
  ↓
  ├─────────────────────────────────────────┐
  │                                         │
  ↓                                         │
┌──────────────────────┐                    │
│ Wait (7 seconds)     │ ← Rate limiting    │
└──────────────────────┘                    │
  ↓                                         │
┌──────────────────────┐                    │
│ Fetch Land Details   │ ← GET https://prod-be.1acre.in/lands/{id}/
└──────────────────────┘                    │
  ↓                                         │
┌──────────────────────┐                    │
│ Insert into DB       │ ← Save to n8n DataTable
└──────────────────────┘                    │
  ↓                                         │
┌──────────────────────┐                    │
│ Get next ID          │ ← NoOp (continue)  │
└──────────────────────┘                    │
  ↓                                         │
  └─────────────────────────────────────────┘ (Loop back)
  ↓
END (when all IDs processed)
```

### Node-by-Node Breakdown

#### 1. Manual Trigger
- **Type**: n8n-nodes-base.manualTrigger
- **Purpose**: Starts the workflow manually
- **Position**: Entry point
- **Output**: Single execution trigger

#### 2. Fetch Land ID's
- **Type**: n8n-nodes-base.httpRequest
- **URL**: `https://raw.githubusercontent.com/1-shweta-rana/Land-cost-estimation-using-Satellite-images-/main/land_ids.json`
- **Method**: GET
- **Output**: JSON object with array of land IDs
  ```json
  {
    "land_ids": [5096, 8625, 4953, ...]
  }
  ```

#### 3. Restructure land id's
- **Type**: n8n-nodes-base.code (Python)
- **Purpose**: Convert single array into multiple items
- **Code**:
  ```python
  land_ids = _input.first().json["land_ids"]
  return [
      {"json": {"land_ids": id}}
      for id in land_ids
  ]
  ```
- **Input**: `{"land_ids": [1, 2, 3]}`
- **Output**: 
  ```
  Item 1: {"land_ids": 1}
  Item 2: {"land_ids": 2}
  Item 3: {"land_ids": 3}
  ```

#### 4. Loop over Land ID's
- **Type**: n8n-nodes-base.splitInBatches
- **Purpose**: Process items one by one
- **Batch Size**: 1 (default)
- **Behavior**: 
  - Takes first item → sends to next node
  - Waits for loop completion
  - Takes next item → repeats

#### 5. Wait before sending next request
- **Type**: n8n-nodes-base.wait
- **Duration**: 7 seconds
- **Purpose**: 
  - Respect API rate limits
  - Avoid overwhelming the server
  - Prevent IP blocking
- **Webhook ID**: 4cfa862f-4132-423b-b8d9-36579d1610fa

#### 6. Fetch Land Details
- **Type**: n8n-nodes-base.httpRequest
- **URL**: `https://prod-be.1acre.in/lands/{{ $json.land_ids }}/`
- **Method**: GET
- **Error Handling**: continueRegularOutput (doesn't stop on errors)
- **Response Example**:
  ```json
  {
    "id": 5096,
    "lat": 17.1463817,
    "long": 78.09244,
    "division_info": [
      {"name": "Telangana"},    // State
      {"name": "Rangareddy"},   // District
      {"name": "Kondurg"},      // Mandal
      {"name": "Tekulapalle"}   // Village
    ],
    "soil_type": "Black",
    "electricity": 0,
    "fencing": 0,
    "land_price": {
      "price_per_acre_crore": {
        "crore": 0,
        "lakh": 85
      }
    },
    "water_source_data": [
      {"well": false, "bore_well": false, ...}
    ],
    "approach_road_length": 25,
    "approach_road_type": "kacha",
    "land_zone_data": [
      {"agricultural": true, "residential": false, ...}
    ],
    "status": "active"
  }
  ```

#### 7. Insert into DB
- **Type**: n8n-nodes-base.dataTable
- **Data Table ID**: f6kQAQCxANDL65kM (n8n internal database)
- **Mapping** (transforms API response to CSV columns):
  ```javascript
  Land_ID: {{ $json.id }}
  State: {{ $json.division_info[0].name }}
  District: {{ $json.division_info[1].name }}
  Mandal: {{ $json.division_info[2].name }}
  Village: {{ $json.division_info[3].name }}
  Latitude: {{ $json.lat }}
  Longitude: {{ $json.long }}
  
  // Price calculation (crore + lakh/100)
  Price_per_Acre: {{ 
    ($json.land_price.price_per_acre_crore.crore || 0) + 
    (($json.land_price.price_per_acre_crore.lakh || 0) / 100) 
  }}
  
  // Water source score (weighted average)
  Water_Source_Data: {{ 
    (
      ($json.water_source_data[0].well ? 0.2 : 0) +
      ($json.water_source_data[0].canal ? 0.5 : 0) +
      ($json.water_source_data[0].drip ? 0.3 : 0) +
      ($json.water_source_data[0].sprinkler ? 0.1 : 0) +
      ($json.water_source_data[0].bore_well ? 0.6 : 0) +
      ($json.water_source_data[0].stream ? 0.4 : 0)
    ) / 1.7
  }}
  
  // Land zone count (number of applicable zones)
  Land_Zone_Data: {{ 
    Object.values($json.land_zone_data[0])
      .filter(v => v === true)
      .length 
  }}
  ```
- **Error Handling**: continueRegularOutput

#### 8. Get next ID
- **Type**: n8n-nodes-base.noOp (No Operation)
- **Purpose**: Acts as connector to loop back
- **Connection**: Returns to "Loop over Land IDs"

---

## 🔄 Data Collection Flow

### Complete Pipeline Visualization

```
┌────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  GitHub Repository                1acre.in API                      │
│  land_ids.json                    prod-be.1acre.in/lands/{id}/     │
│       │                                  │                          │
└───────┼──────────────────────────────────┼──────────────────────────┘
        │                                  │
        ↓                                  ↓
┌────────────────────────────────────────────────────────────────────┐
│                    N8N WORKFLOW ENGINE                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [Manual Trigger] → [Fetch IDs] → [Restructure] → [Loop]          │
│                                         ↓                           │
│                              [Wait 7s] → [Fetch Details]           │
│                                         ↓                           │
│                                    [Insert DB]                     │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓ (Export CSV)
┌────────────────────────────────────────────────────────────────────┐
│                    LOCAL STORAGE                                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  dataset4.csv (300 rows × 19 columns)                              │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓ (Read by main.py)
┌────────────────────────────────────────────────────────────────────┐
│                    SELENIUM SCRAPER                                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  main.py:                                                           │
│    1. Load dataset4.csv                                            │
│    2. Load land_ids.json                                           │
│    3. For each land_id:                                            │
│         ├─ Extract lat/long from dataset                           │
│         ├─ Build URL: 1acre.in/@{lat}-{long}-15m/...              │
│         ├─ Navigate with Chrome (headless)                         │
│         ├─ Inject JS to hide UI                                    │
│         └─ Save screenshot: images_trial/{land_id}.png             │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓
┌────────────────────────────────────────────────────────────────────┐
│                    IMAGE STORAGE                                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  images_trial/                                                      │
│    ├─ 5096.png (1280×1024, ~1.4MB)                                │
│    ├─ 8625.png                                                     │
│    └─ ... (280+ images)                                            │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

### Timing & Performance

- **N8N Workflow**:
  - Per land ID: ~8 seconds (7s wait + 1s API)
  - 300 land IDs: ~40 minutes total
  - Error rate: ~5% (API failures handled gracefully)

- **Selenium Scraper**:
  - Per screenshot: ~12 seconds (5s load + 2s JS + 5s buffer)
  - 300 screenshots: ~60 minutes total
  - Success rate: ~93% (some lands have missing/invalid coords)

---

## 🖼️ Image Processing Flow

### DINOv2 Feature Extraction Pipeline

```
┌────────────────────────────────────────────────────────────────────┐
│                    INPUT: RAW IMAGES                                │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  images_trial/5096.png                                              │
│  ├─ Format: PNG                                                     │
│  ├─ Size: 1280 × 1024 pixels                                       │
│  ├─ Channels: RGB (3)                                               │
│  └─ Content: Satellite view (Mapbox)                               │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓ (PIL Image.open)
┌────────────────────────────────────────────────────────────────────┐
│                    IMAGE PREPROCESSING                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  AutoImageProcessor (from saved_transformer/)                      │
│    ├─ Resize to 224×224 (DINOv2 input size)                       │
│    ├─ Normalize: mean=[0.485, 0.456, 0.406]                       │
│    │             std=[0.229, 0.224, 0.225]                         │
│    └─ Convert to tensor: [1, 3, 224, 224]                         │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓ (Move to GPU if available)
┌────────────────────────────────────────────────────────────────────┐
│                    DINOV2 MODEL                                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  facebook/dinov2-small (88MB)                                       │
│                                                                      │
│  Architecture:                                                      │
│    Input: [1, 3, 224, 224]                                         │
│      ↓                                                              │
│    [Patch Embedding Layer]                                         │
│      ↓ (16×16 patches → 196 patches)                              │
│    [12 Transformer Blocks]                                         │
│      ├─ Multi-head self-attention                                  │
│      ├─ Feed-forward network                                       │
│      └─ Layer normalization                                        │
│      ↓                                                              │
│    Output: [1, 197, 384]                                           │
│      ├─ Token 0: [CLS] token (global image summary)               │
│      └─ Tokens 1-196: Patch embeddings                            │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓ (Extract CLS token)
┌────────────────────────────────────────────────────────────────────┐
│                    EMBEDDING EXTRACTION                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  outputs.last_hidden_state[:, 0, :]                                │
│  ├─ Shape: [1, 384]                                                │
│  ├─ Type: torch.Tensor (float32)                                   │
│  └─ Represents: Global visual features                             │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓ (Convert to numpy)
┌────────────────────────────────────────────────────────────────────┐
│                    FEATURE ATTACHMENT                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  find_and_attach(embedding, dataset, image_name)                   │
│    1. Parse Land_ID from image name (5096.png → 5096)             │
│    2. Find matching row in dataset4.csv                            │
│    3. Add columns: emb_0, emb_1, ..., emb_383                     │
│    4. Insert embedding values                                       │
│                                                                      │
│  Result: Dataset now has 403 columns (19 + 384)                    │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

### What DINOv2 Learns from Satellite Images

DINOv2 (Self-Supervised Vision Transformer) captures:

1. **Spatial Patterns**
   - Field boundaries and shapes
   - Parcel layout and geometry
   - Neighboring land usage

2. **Land Cover Types**
   - Vegetation density (green fields)
   - Bare soil vs. cultivated land
   - Built-up areas (buildings, roads)

3. **Infrastructure Visibility**
   - Road networks (even if not in structured data)
   - Water bodies (ponds, canals)
   - Nearby development

4. **Terrain Features**
   - Slope and elevation (from shadows)
   - Drainage patterns
   - Soil moisture (color variations)

5. **Context & Surroundings**
   - Urban proximity
   - Agricultural vs. residential zones
   - Regional development level

---

## 🤖 Training Pipeline Flow

### Complete ML Pipeline

```
┌────────────────────────────────────────────────────────────────────┐
│                    INPUT DATA                                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  dataset4.csv (with embeddings)                                     │
│  ├─ 300 rows                                                        │
│  ├─ 403 columns (19 original + 384 embeddings)                    │
│  └─ Target: Price_per_Acre                                         │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓
┌────────────────────────────────────────────────────────────────────┐
│                    DATA PREPROCESSING                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Step 1: Drop Unused Columns                                        │
│    ├─ createdAt, updatedAt, id, Status                            │
│    └─ Longitude, Latitude (used only for scraping)                │
│                                                                      │
│  Step 2: Handle Missing Values                                      │
│    ├─ Water_Source_Data → 0                                        │
│    ├─ Approach_Road_Length → 10                                    │
│    ├─ Soil_Type → "black"                                          │
│    ├─ Land_Zone_Data → 0                                           │
│    └─ Approach_Road_Type → "kacha"                                 │
│                                                                      │
│  Step 3: Feature Engineering                                        │
│    ├─ Normalize text: lowercase, strip whitespace                  │
│    ├─ Ordinal encode: Soil_Type, Approach_Road_Type               │
│    ├─ One-hot encode: State, District                             │
│    └─ Keep numeric: Embeddings, Electricity, etc.                 │
│                                                                      │
│  Step 4: Train/Validation Split                                     │
│    ├─ 80% training (240 rows)                                      │
│    ├─ 20% validation (60 rows)                                     │
│    └─ Stratified by State (balanced distribution)                 │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓
┌────────────────────────────────────────────────────────────────────┐
│                    FEATURE MATRIX                                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  X_train: [240, 394]                                                │
│    ├─ Ordinal features: 2 columns                                  │
│    ├─ One-hot features: ~8 columns (depends on unique values)     │
│    └─ Numeric features: 384 embeddings + other numeric            │
│                                                                      │
│  y_train: [240]                                                     │
│    └─ Price_per_Acre (continuous values)                           │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓
┌────────────────────────────────────────────────────────────────────┐
│                    XGBOOST TRAINING                                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Hyperparameters:                                                   │
│    ├─ n_estimators: 100 (number of trees)                         │
│    ├─ tree_method: 'hist' (fast histogram-based)                  │
│    ├─ device: 'cuda' or 'cpu' (auto-detected)                     │
│    └─ verbosity: 0 (silent mode)                                   │
│                                                                      │
│  Training Process:                                                  │
│    1. Initialize 100 trees                                         │
│    2. For each tree:                                               │
│         ├─ Find best split using gradient & hessian               │
│         ├─ Build tree structure                                    │
│         └─ Update predictions                                      │
│    3. Combine all trees (ensemble)                                 │
│                                                                      │
│  Output: Trained model (in-memory)                                 │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓
┌────────────────────────────────────────────────────────────────────┐
│                    MODEL EVALUATION                                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Validation Set: X_valid [60, 394] → y_pred [60]                  │
│                                                                      │
│  Metrics:                                                           │
│    ├─ MAE = mean(|y_true - y_pred|)                               │
│    ├─ RMSE = sqrt(mean((y_true - y_pred)²))                       │
│    ├─ R² = 1 - (SS_res / SS_tot)                                  │
│    └─ MAPE = mean(|y_true - y_pred| / y_true) × 100               │
│                                                                      │
│  Feature Importance (top 20):                                       │
│    ├─ Gain metric (improvement in loss)                           │
│    └─ Visualized as horizontal bar chart                          │
│                                                                      │
└────────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ↓ (User confirms save)
┌────────────────────────────────────────────────────────────────────┐
│                    MODEL PERSISTENCE                                │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  joblib.dump(model, "price_predictor.pkl")                         │
│  ├─ Format: Pickle (joblib-optimized)                             │
│  ├─ Size: ~1-2 MB                                                  │
│  └─ Contains: All 100 trees + metadata                            │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

### XGBoost Tree Example (Simplified)

```
Tree 1 (out of 100):
                     [Root: All samples]
                             │
                ┌────────────┴────────────┐
                │                         │
         [emb_42 < 0.5]           [emb_42 >= 0.5]
                │                         │
      ┌─────────┴────────┐      ┌────────┴────────┐
      │                  │      │                 │
[District=X]     [District≠X]  [Soil=black]  [Soil=red]
  │                  │           │                │
Predict: 0.8     Predict: 1.2  Predict: 1.5   Predict: 0.6
(crore)          (crore)       (crore)        (crore)

Final Prediction = Tree1 + Tree2 + ... + Tree100 (summed)
```

---

## 🔗 Component Interactions

### Data Flow Summary

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   GitHub    │─────▶│     N8N     │─────▶│ dataset4.csv│
│ land_ids.json│      │  Workflow   │      │             │
└─────────────┘      └─────────────┘      └─────────────┘
                            │                     │
                            ▼                     ▼
                     ┌─────────────┐      ┌─────────────┐
                     │ 1acre.in API│      │   main.py   │
                     │             │      │  (Selenium) │
                     └─────────────┘      └─────────────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │ images_trial│
                                          │    /*.png   │
                                          └─────────────┘
                                                 │
                                                 ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  training.py│◀─────│  utils.py   │◀─────│   DINOv2    │
│  (XGBoost)  │      │ (preprocess)│      │  (embedder) │
└─────────────┘      └─────────────┘      └─────────────┘
       │
       ▼
┌─────────────┐
│price_pred...│
│   .pkl      │
└─────────────┘
```

### File Dependencies

```
main.py
├── imports: take_ss, utils, pandas
├── reads: dataset4.csv, land_ids.json
└── writes: images_trial/*.png

take_ss.py
├── imports: selenium, pandas, utils
├── reads: dataset4.csv (for lat/long)
└── writes: images_trial/*.png

utils.py
├── imports: transformers, torch, sklearn, pandas
├── reads: images_trial/*.png, saved_transformer/
└── writes: saved_transformer/ (first run only)

training.py
├── imports: utils, xgboost, sklearn, joblib
├── reads: dataset4.csv, images_trial/, saved_transformer/
└── writes: price_predictor.pkl, feature_importance.png

tests.py
├── imports: utils, pandas
├── reads: dataset4.csv
└── writes: (none)
```

---

## 🎓 Key Design Decisions

### 1. Why DINOv2 over other models?
- **Self-supervised**: No need for labeled satellite data
- **Patch-based**: Captures fine-grained spatial patterns
- **Small variant**: Good balance (88MB) vs. accuracy
- **Pre-trained**: Works well with limited data (300 samples)

### 2. Why XGBoost over Neural Networks?
- **Tabular data**: XGBoost excels with mixed features
- **Small dataset**: 300 samples insufficient for deep learning
- **Interpretability**: Feature importance is crucial
- **Speed**: Fast training (~seconds vs. minutes)
- **Robustness**: Handles missing values naturally

### 3. Why separate data collection + training?
- **Reusability**: Images can be used for multiple experiments
- **Debugging**: Easier to isolate issues
- **Efficiency**: Scraping is slow; train multiple times on same data
- **Modularity**: Can update dataset without re-scraping

### 4. Why N8N + Selenium instead of just one?
- **N8N**: Structured data (API) - fast, reliable
- **Selenium**: Visual data (screenshots) - needs browser rendering
- **Division of labor**: Each tool does what it's best at

---

## 📊 Performance Bottlenecks & Optimizations

### Current Bottlenecks
1. **Selenium scraping**: ~12s per image (60 min for 300)
   - **Optimization**: Use async Selenium or Playwright
2. **DINOv2 inference**: ~1s per image on CPU (5 min for 300)
   - **Optimization**: Batch processing, use GPU
3. **N8N workflow**: ~40 min for 300 API calls
   - **Optimization**: Parallel requests (with rate limit)

### Implemented Optimizations
1. ✅ **Headless browser**: No GUI overhead
2. ✅ **Model caching**: Download DINOv2 once
3. ✅ **GPU support**: Auto-detect CUDA for training
4. ✅ **Histogram tree method**: Faster XGBoost training

---

**For questions about specific components, refer to:**
- N8N details → See `workflow.json` file
- Python code → See `PROJECT_DOCUMENTATION.md`
- Usage instructions → See `README.md`
