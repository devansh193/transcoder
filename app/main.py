from fastapi import FastAPI, Request
from app.core.middleware import authenticate_request
from app.api.v1.endpoints import auth, transcode, upload
app = FastAPI()

@app.middleware("http")
async def auth_middleware(request:Request, call_next):
    await authenticate_request(request)
    return await call_next(request)


app.include_router(auth.router, prefix="/api/v1")
app.include_router(transcode.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")