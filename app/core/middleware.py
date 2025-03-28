from fastapi import Request, HTTPException, status
from app.core.config import settings
from app.core.security import validate_timestamp, verify_signature
from app.db.crud import get_public_key_by_id

async def authenticate_request(request:Request):
    api_key = request.headers.get(settings.api_key_header)
    timestamp = request.headers.get(settings.timestamp_header)
    signature = request.headers.get(settings.signature_header)

    if not all([api_key, timestamp, signature]):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication headers",
        )
    if not validate_timestamp(timestamp):
         raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Expired request",
         )
    
    public_key = await get_public_key_by_id(api_key)
    if not public_key:
         raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Invalid API key"
         )
    
    canonical_request = f"{request.method}{request.url.path}{timestamp}{await request.body()}"
    if not verify_signature(public_key, signature, canonical_request):
         raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Invalid signature",
         )