from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional
import uvicorn
 
# Create FastAPI application
app = FastAPI()
 
# Hardcoded API key (store securely in production)
API_KEY = "my-secret-api-key"
 
# Dependency function to verify API key
def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key is None:
        raise HTTPException(
            status_code=401, 
            detail="API key missing",
            headers={"WWW-Authenticate": "API-Key"}
        )
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401, 
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"}
        )
    return x_api_key
 
# Protected endpoint
@app.get("/protected-data", dependencies=[Depends(verify_api_key)])
def get_protected_data():
    return {"message": "This is protected data"}
 
# Public endpoint
@app.get("/public-data")
def get_public_data():
    return {"message": "This is public data"}
 
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)