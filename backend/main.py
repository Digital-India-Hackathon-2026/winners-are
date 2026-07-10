import os
import pickle
import time
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

app = FastAPI(title="UPI Fraud Detector Service", version="1.0.0")

# Inject CORSMiddleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load XGBoost model pipeline with safety fallback
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
model = None

if os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        print("[UPI-FRAUD] Loaded XGBoost model from model.pkl successfully.")
    except Exception as e:
        print(f"[UPI-FRAUD] Failed to load model.pkl: {e}. Using fallback heuristic.")
else:
    print("[UPI-FRAUD] model.pkl not found. Using fallback heuristic.")


class TransactionRequest(BaseModel):
    amount: float
    sender_id: str
    receiver_id: str
    timestamp: str
    location: Optional[str] = "unknown"
    device_id: Optional[str] = None
    transaction_count_1h: Optional[int] = None


def run_heuristic(amount: float, timestamp: str, transaction_count_1h: Optional[int]) -> dict:
    """Rule-based fallback heuristic for UPI fraud probability."""
    score = 0.05  # Base level risk
    
    # 1. Amount threshold rules
    if amount > 100000:
        score += 0.45
    elif amount > 50000:
        score += 0.30
    elif amount > 10000:
        score += 0.15
        
    # 2. Time-of-day heuristic (late-night transactions are higher risk)
    try:
        dt = pd.to_datetime(timestamp)
        hour = dt.hour
        if 0 <= hour <= 5:
            score += 0.20
    except Exception:
        pass
        
    # 3. Frequency heuristic
    freq = transaction_count_1h or 1
    if freq > 10:
        score += 0.35
    elif freq > 5:
        score += 0.20
        
    prob = max(0.01, min(0.99, score))
    status = "fraud_detected" if prob >= 0.5 else "safe"
    
    return {
        "status": status,
        "fraud_probability": float(prob),
        "engine": "rule_based_heuristic"
    }


@app.post("/api/predict")
async def predict_transaction(req: TransactionRequest):
    # Attempt to predict using XGBoost model
    if model is not None:
        try:
            try:
                dt = pd.to_datetime(req.timestamp)
                hour = dt.hour
            except Exception:
                hour = 12

            # Build feature frame (matching common XGBoost features)
            features_df = pd.DataFrame([{
                "amount": req.amount,
                "hour": hour,
                "transaction_count_1h": req.transaction_count_1h or 1,
            }])

            # If model supports probability outputs
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(features_df)
                prob = float(probs[0][1])
            else:
                preds = model.predict(features_df)
                prob = float(preds[0])
                if prob > 1.0:  # normalize if output is log-odds
                    prob = 1.0 / (1.0 + np.exp(-prob))

            status = "fraud_detected" if prob >= 0.5 else "safe"
            return {
                "status": status,
                "fraud_probability": float(prob),
                "engine": "xgboost_model"
            }
        except Exception as e:
            print(f"[UPI-FRAUD] Model prediction failed: {e}. Falling back to heuristic.")
            
    # Fall back to rule-based heuristic
    return run_heuristic(req.amount, req.timestamp, req.transaction_count_1h)


@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": model is not None}
