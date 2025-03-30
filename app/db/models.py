from pydantic import BaseModel, Field, HttpUrl, validator
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base
from datetime import datetime
from typing import Optional
from enum import Enum
from uuid import UUID

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())

class PublicKey(Base):
    __tablename__ = "public_keys"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), index=True)
    public_key = Column(String, nullable=False)
    private_key = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class UploadStatus(str, Enum):
    PENDING="pending"
    UPLOADING="uploading"
    UPLOADED="uploaded"
    PROCESSING="processing"
    COMPLETE="complete"
    FAILED="failed"

class UploadResponse(BaseModel()):
    id: str = Field(..., description="Unique identifier for the upload")
    filename: str = Field(..., description="The filename used in storage (S3 key)")
    original_filename: str = Field(..., description="Original filename as uploaded by user")
    status: UploadStatus = Field(
        default=UploadStatus.UPLOADED,
        description="Current status of the upload"
    )
    url: Optional[HttpUrl] = Field(None, description="URL to access the file (may be temporary or access-controlled)")
    content_type: str = Field(..., description="MIME type of the uploaded file")
    size_byte: int = Field(..., description="Size of the file in bytes")
    transcode_ready: bool = Field(default=False, description="Whether the file is ready for transcoding")
    transcode_job_id: Optional[str] = Field(None, description="ID of associated transcoding job, if any")
    user_id: str = Field(..., description="ID of the user who uploaded the file")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcfromtimestamp)
    metadata: Optional[dict] = Field(default={}, description="Additional metadata associated with the upload")

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "videos/550e8400-e29b-41d4-a716-446655440000.mp4",
                "original_filename": "my_vacation_video.mp4",
                "status": "uploaded",
                "url": "https://example-bucket.s3.amazonaws.com/videos/550e8400-e29b-41d4-a716-446655440000.mp4",
                "content_type": "video/mp4",
                "size_bytes": 15728640,
                "transcode_ready": False,
                "transcode_job_id": None,
                "user_id": "user_123456",
                "created_at": "2025-03-30T14:30:00Z",
                "updated_at": "2025-03-30T14:30:00Z",
                "metadata": {
                    "duration_seconds": 120,
                    "resolution": "1920x1080"
                }
            }
        }

    @validator('url', pre=True)
    def ensure_https(cls, v):
        """Ensure all URLs are HTTPS."""
        if v and isinstance(v, str) and v.startswith('http://'):
            return v.replace('http://', 'https://', 1)
        return v
    
    class UploadRequest(BaseModel):
        title: Optional[str] = Field(None, description="Title for the uploaded file")
        description: Optional[str] = Field(None, description="Description of the uploaded file")
        is_public: bool = Field(
            default=False, 
            description="Whether the uploaded file should be publicly accessible"
        )
        tags: list[str] = Field(
            default_factory=list, 
            description="Tags associated with the uploaded file"
        )
        folder_path: Optional[str] = Field(
            None, 
            description="Virtual folder path for organizing uploads"
        )
        
        class Config:
            schema_extra = {
                "example": {
                    "title": "My Vacation Video",
                    "description": "Video from our trip to the mountains",
                    "is_public": False,
                    "tags": ["vacation", "mountains", "family"],
                    "folder_path": "personal/vacations/2025"
                }
            }

    class UploadProgressResponse(BaseModel):
        id: str
        status: UploadStatus
        progress_percentage: float = Field(..., ge=0, le=100)
        bytes_uploaded: int
        total_bytes: int
        started_at: datetime
        estimated_completion_time: Optional[datetime] = None
        
        class Config:
            schema_extra = {
                "example": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "uploading",
                    "progress_percentage": 45.5,
                    "bytes_uploaded": 7000000,
                    "total_bytes": 15728640,
                    "started_at": "2025-03-30T14:28:30Z",
                    "estimated_completion_time": "2025-03-30T14:32:15Z"
                }
            }