import yfinance as yf
import pandas as _pd
from sklearn.linear_model import LinearRegression
import joblib

# Download 2 years of Euro to US Dollar daily conversion rates
data: _pd.DataFrame = yf.download("EURUSD=X", period="2y", interval="1d")
data = data.dropna()

# Simple supervised ML setup: 
# Predict today's closing price from last 5 days' closing prices

# Each row in data will contain the conversion rate for the current day & the 5 days prior
for i in range(1, 6):
    data[f"lag_{i}"] = data["Close"].shift(i)
data = data.dropna()

# X is the 5 days prior closing prices and Y is the current day's closing price
X = data[[f"lag_{i}" for i in range(1, 6)]]
y = data["Close"]

# Train the model to predict Y from X, using linear regression
# i.e. find the best fit line through the training data
# todo: validate comment^
model = LinearRegression().fit(X, y)
print("R^2:", model.score(X, y))

joblib.dump(model, "fx_model.joblib")
print("✅ Model saved.")
