# 🛰️ Land Cost Estimation Using Satellite Images

> **Capstone Project**: Computer Vision & Deep Learning for Agricultural Land Price Prediction

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.9.0-red.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Overview

This project predicts **agricultural land prices per acre** in Telangana, India, by combining:
- 🖼️ **Satellite imagery analysis** using Vision Transformers (DINOv2)
- 📊 **Structured land data** (location, soil, infrastructure)
- 🤖 **Machine Learning** (XGBoost regression)

**Use Case:** Help buyers, sellers, and investors estimate fair land prices based on visual and geographic features.

---

## ✨ Key Features

✅ **Automated data collection** from 1acre.in (N8N + Selenium)  
✅ **Deep learning image embeddings** (facebook/dinov2-small)  
✅ **Robust ML pipeline** (XGBoost with GPU support)  
✅ **Comprehensive evaluation** (MAE, RMSE, R², MAPE)  
✅ **Feature importance analysis** (understand price drivers)  

---

## 🚀 Quick Start

### 1️⃣ Installation
```bash
git clone https://github.com/1-shweta-rana/Land-cost-estimation-using-Satellite-images-.git
cd Land-cost-estimation-using-Satellite-images-
pip install -r requirements.txt
```

### 2️⃣ Collect Data (Optional)
```bash
# Update land_ids.json with land IDs you want
python main.py  # Downloads satellite images
```

### 3️⃣ Train Model
```bash
python training.py  # Trains XGBoost model
# Output: price_predictor.pkl
```

### 4️⃣ Make Predictions
```python
import joblib
model = joblib.load("price_predictor.pkl")
# See PROJECT_DOCUMENTATION.md for full usage
```

---

## 📁 Project Structure

```
├── main.py                  # Data collection orchestrator
├── take_ss.py               # Selenium screenshot capture
├── training.py              # Model training pipeline
├── utils.py                 # Preprocessing & feature extraction
├── dataset4.csv             # Main dataset (300 lands)
├── land_ids.json            # Land IDs for collection
├── workflow.json            # N8N automation workflow
├── images_trial/            # Satellite screenshots (280+ images)
├── saved_transformer/       # DINOv2 model cache
├── price_predictor.pkl      # Trained XGBoost model
└── PROJECT_DOCUMENTATION.md # 📖 Complete technical docs
```

---

## 🔬 Methodology

### Data Collection
1. **N8N Workflow**: Automates API calls to 1acre.in
2. **Selenium Scraper**: Captures full-screen satellite images

### Feature Engineering
- **Image Embeddings**: 384 dims from DINOv2 transformer
- **Structured Features**:
  - 📍 Location: State, District, Mandal, Village
  - 🌱 Land: Soil type, area, zones
  - 🚰 Infrastructure: Electricity, water, roads, fencing

### Model Training
- **Algorithm**: XGBoost (gradient boosting)
- **Features**: 394 total (384 image + 10 structured)
- **Evaluation**: 80/20 train-validation split

---

## 📊 Performance Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **MAE** | Mean Absolute Error | < 0.30 crore |
| **RMSE** | Root Mean Squared Error | < 0.40 crore |
| **R²** | Coefficient of Determination | > 0.80 |
| **MAPE** | Mean Absolute Percentage Error | < 25% |

*1 crore = 10 million INR (Indian Rupees)*

---

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| **ML/DL** | PyTorch, Transformers, XGBoost, scikit-learn |
| **Data** | pandas, NumPy |
| **Scraping** | Selenium, WebDriver Manager |
| **Automation** | N8N (workflow engine) |
| **Visualization** | Matplotlib |

---

## 📖 Documentation

For **detailed technical documentation**, see:
👉 **[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)**

Includes:
- 🏗️ Complete architecture diagrams
- 🔄 Step-by-step workflow explanations
- 🧩 Code walkthroughs
- 📈 Model evaluation details
- 🎓 Learning outcomes

---

## 🌐 Data Source

- **Provider**: [1acre.in](https://1acre.in) - Agricultural land marketplace
- **Coverage**: Telangana State, India
- **Data Points**: 300 land parcels
- **Features**: 19 attributes per land parcel

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- 🌍 Expand to other states/countries
- 🖥️ Build web UI (frontend.py is empty)
- 🧪 Add automated tests
- 📱 Create mobile app

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Authors

**Shweta Rana** - [GitHub](https://github.com/1-shweta-rana)

---

## 🙏 Acknowledgments

- **DINOv2**: Meta AI Research
- **XGBoost**: Distributed ML Community
- **1acre.in**: Land data platform
- **N8N**: Open-source workflow automation

---

## 📞 Contact

Questions? Open an issue or reach out via GitHub!

---

**⭐ Star this repo if you find it helpful!**
