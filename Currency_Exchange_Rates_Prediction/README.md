# Currency Exchange Rates Prediction

A machine learning project for foreign exchange rate prediction using historical data and scikit-learn.

## Features

- **Data Processing**: Historical FX rate data preprocessing and feature engineering
- **Model Training**: Machine learning model training with scikit-learn
- **API Server**: REST API for serving predictions via Flask
- **Model Persistence**: Trained models saved using joblib for reuse

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Train the model:
```bash
python train-fx-model.py
```

4. Start the API server:
```bash
python serve_fx_model.py
```

## Project Structure

```
Currency-Exchange-Rates-Prediction/
├── train-fx-model.py          # Model training script
├── serve_fx_model.py          # Flask API server
├── fx_model.joblib            # Trained model (generated)
├── requirements.txt           # Python dependencies
├── venv/                      # Virtual environment (not tracked in git)
└── README.md                  # This file (user guide)
```

## Usage

### Training
The `train-fx-model.py` script processes historical data and trains a machine learning model for FX rate prediction.

### API Server
The `serve_fx_model.py` script starts a Flask server that serves predictions via REST API endpoints.

## Technologies

- **Python 3.x**
- **scikit-learn** - Machine learning library
- **Flask** - Web framework for API
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **joblib** - Model serialization