from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import time

app = FastAPI(title="FX Rate Prediction API")

model = joblib.load("fx_model.joblib")

class FXInput(BaseModel):
    lag_1: float
    lag_2: float
    lag_3: float
    lag_4: float
    lag_5: float

'''
Predicts the FX rate for the given input (5 days' closing prices before the input day).

Example usage:
    curl -X POST "http://127.0.0.1:8000/predict" \
    -H "Content-Type: application/json" \
    -d '{"lag_1":1.075,"lag_2":1.076,"lag_3":1.074,"lag_4":1.073,"lag_5":1.072}'
'''
@app.post("/predict")
def predict_fx(input: FXInput):
    start = time.time()
    X = np.array([[input.lag_1, input.lag_2, input.lag_3, input.lag_4, input.lag_5]])
    pred = model.predict(X)[0]
    latency = round(time.time() - start, 4)
    return {"predicted_fx_rate": round(float(pred), 5), "latency_seconds": latency}
    
# TODO[Optional]: Ideas to improve this further: 
#  - Log every prediction to predictions.log
#  - Add batch job to evaluate against requested predictions over night 
#    & improve the model by checking the error diff against false predictions.
#  - Read about possible use cases for this model & if its viable to predict this accurately
#    or if its not realistic to predict exchange rates due to market volatility.
#  - See if other asset tickers e.g. stocks or real estate prices can be more accurately predicted
#    using various different features like historical data, news, economic data, etc.
#
