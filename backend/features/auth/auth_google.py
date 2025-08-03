import os
from fastapi import APIRouter, Request, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv
load_dotenv()


router = APIRouter()


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

@router.post("/auth/google")
async def google_login(request: Request):
    data = await request.json()
    token = data.get("idToken")

    if not token:
        raise HTTPException(status_code=400, detail="Token missing")

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        return {
            "status": "success",
            "email": idinfo.get("email"),
            "user_id": idinfo.get("sub")
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token error: {e}")
