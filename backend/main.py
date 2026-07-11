# DEPRECATED AND ORPHANED
# This file is an orphaned numeric transaction fraud predictor stub and is NOT used by the active image-scanning pipeline.
# Do not run or configure this service. The active backend is located at artifacts/tustlayer/backend/main.py.

from fastapi import FastAPI, HTTPException

app = FastAPI(title="DEPRECATED - UPI Fraud Detector Service", version="0.0.0-deprecated")

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(path_name: str):
    raise HTTPException(
        status_code=410,
        detail="This service is deprecated and orphaned. Please use the real API at artifacts/tustlayer/backend."
    )
