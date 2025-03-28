from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64
from datetime import datetime
from fastapi import HTTPException, status
from app.core.config import settings

def verify_signature(public_key_pem: str, signature: str, canonical_request: str) -> bool:
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        public_key.verify(
            base64.b64decode(signature),
            canonical_request.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    
def validate_timestamp(request_timestamp: str) -> bool:
    try:
        timestamp = int(request_timestamp)
        current_time = int(datetime.utcnow().timestamp())
        return abs(current_time - timestamp) <= settings.timestamp_window
    except ValueError:
        return False