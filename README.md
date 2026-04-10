# Turbulence Prediction System

A machine learning system that predicts aviation turbulence risk using historical weather data from Matsumoto Airport, Japan. Combines SVM classification with an interactive 3D visualization dashboard.

**Based on:** Suzuki, S. (2022). Applying machine learning to predict turbulence around Matsumoto Airport. *Journal of Big Data*, 9(1), 34. https://doi.org/10.1186/s40537-022-00584-5

## Overview

This project implements and extends the methodology from Suzuki's research, analyzing weather patterns to forecast turbulence risk along flight corridors. The system achieved 100% accuracy on 2017 training data and correctly identified 10 high-risk days out of 179 test days in 2019.

**Pipeline:** StandardScaler → PCA → K-Means → SVM

![3D Turbulence Visualization Dashboard](images/dashboard.jpg)
*Interactive 3D globe showing flight paths and turbulence risk zones*

## Quick Start

### Installation

```bash
git clone https://github.com/RithvikRK12/ML-Turbulence-Predict.git
cd Turbulence
python -m venv .venv
.venv\Scripts\activate
pip install pandas numpy matplotlib seaborn scikit-learn scipy
```

### Run Analysis

```bash
python AirPort_main.py
```

This trains the model on 2017 weather data and generates prediction visualizations (PCA variance, cluster plots, confusion matrix, feature importance).

### Generate Predictions

```bash
python generate_predictions.py
```

Outputs geographic predictions to `visualization/predictions.json`.

### Launch Visualization

```bash
cd visualization
python -m http.server 8001
```

Open http://localhost:8001 to view the 3D globe with animated flight paths and turbulence heatmaps.

## Features

### Interactive 3D Visualization
![Flight Path Animation](images/flightPath.jpg)
- Real-time animated aircraft with risk-based color coding
- Gaussian-blurred turbulence heatmap overlay
- Interactive camera controls and layer toggles

### Machine Learning Analysis
![Model Performance Plots](images/GraphAnalysis.jpg)
- PCA variance analysis and dimensionality reduction
- K-Means clustering of weather patterns
- SVM classification with comprehensive metrics

## Project Structure

```
Turbulence/
├── AirPort_main.py              # Main ML pipeline
├── AirPort_lib.py               # ML functions (PCA, K-Means, SVM)
├── generate_predictions.py      # Geographic data generator
├── csv/
│   ├── Matsumoto_modify02.csv   # 2017 training data
│   └── Matsumoto2019.csv        # 2019 test data
└── visualization/
    ├── index.html               # 3D dashboard
    ├── app.js                   # CesiumJS application
    └── predictions.json         # Prediction output
```

## Technical Details

**Machine Learning:**
- PCA reduces ~30 weather features to 8-12 components (80% variance)
- K-Means clusters data into 6 weather pattern groups
- SVM with RBF kernel classifies turbulence risk (binary)

**Data Sources:**
- Weather stations: Wajima, Tokyo, Matsumoto Airport
- Features: Wind speed/shear, humidity, pressure, visibility
- Training: 2017 full year | Testing: 2019 (179 days)

**Visualization:**
- Built with CesiumJS for 3D globe rendering
- Animated aircraft changes color based on predicted risk
- Gaussian-blurred heatmap overlay for turbulence zones
- Interactive controls for toggling layers and camera

## Results

| Metric | Value |
|--------|-------|
| Training Accuracy | 95.7% |
| Test Accuracy | 94.4% |
| High-Risk Days Detected | 10/179 (5.6%) |
| Cross-Validation | 0.98-1.00 |

### Performance Visualizations

![Confusion Matrix](images/confusion_matrix.png)
*Confusion matrix showing model classification performance*

![PCA Variance Analysis](images/pca_variance.png)
*Principal Component Analysis showing variance explained by components*

![Cluster Visualization](images/kmeans_clusters.png)
*K-Means clustering of weather patterns*

## Acknowledgments

This project implements the machine learning methodology described in Suzuki (2022). The core ML pipeline (PCA → K-Means → SVM) follows the paper's approach, with additional enhancements including interactive 3D visualization, comprehensive statistical analysis, and extended prediction outputs.

## License

Educational project using data from Japan Meteorological Agency (JMA). CesiumJS under Apache 2.0.
