# Land Cost Estimation Using Satellite Images

A novel machine learning approach to predict **land price in India** using **satellite imagery + geospatial data**.
---

##  Overview
Due to the lack of a proper land-price dataset in India, we built a **custom dataset** integrating:
- Satellite images (Google Maps / Earth Engine)
- Coordinates & location-based features
- Government circle rates & publicly available listings

The model learns visual cues like infrastructure, vegetation, and accessibility that influence land value.

---
##  Method
- Extract visual features using **CNN / Vision Transformer**
- Combine with structured attributes
- Train regression models (RF, XGBoost, ViT)

**Metrics:** MAE, RMSE, MAPE, R²

> Multimodal fusion showed better accuracy than using only structured data.
---

## Tech Stack
Python, PyTorch/TensorFlow, Pandas, Selenium, Google Earth Engine

---
##  Future Scope
- Larger dataset coverage across India
- Better land-use features (NDVI, road networks)
- Deploy as a location-based prediction web app

---
##  Authors
**Shweta Rana**
**Aaditya R Trivedi**
---

*If you like this project, please star the repo!*
