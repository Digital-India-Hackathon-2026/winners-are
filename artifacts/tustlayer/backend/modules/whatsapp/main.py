# DEPRECATED AND DUPLICATE
# This file is deprecated. The active main.py is located at artifacts/tustlayer/backend/main.py.

from fastapi import FastAPI, HTTPException

app = FastAPI(title="DEPRECATED - TrustLayer AI API", version="0.0.0-deprecated")

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(path_name: str):
    raise HTTPException(
        status_code=410,
        detail="This service is deprecated. Please use the real API at artifacts/tustlayer/backend/main.py."
    )
