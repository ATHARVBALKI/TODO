from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import secrets
import uvicorn
 
# Create FastAPI application
app = FastAPI()
 
# Mock client database
CLIENTS = {
    "service1": "secret123",
    "service2": "secret456"
}
 
# Valid tokens
VALID_TOKENS = set()
 
# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
 
def verify_client_credentials(client_id: str, client_secret: str):
    """Verify client credentials"""
    return CLIENTS.get(client_id) == client_secret
 
def verify_token(token: str = Depends(oauth2_scheme)):
    """Verify access token"""
    if token not in VALID_TOKENS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return {"client_id": "authenticated-client"}
 
# Token endpoint
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = 
Depends()):
    """Issue access token for valid client credentials"""
    client_id = form_data.username
    client_secret = form_data.password
    
    if not verify_client_credentials(client_id, client_secret):
        raise HTTPException(
            status_code=401,
            detail="Incorrect client credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Generate a simple token
    access_token = secrets.token_urlsafe(32)
    VALID_TOKENS.add(access_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600
    }
 
# Protected endpoint
@app.get("/api/service-data")
def get_service_data(current_user: dict = Depends(verify_token)):
    return {
        "message": "Access granted",
        "client": current_user["client_id"]
         }
 
# Public endpoint
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
 
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)