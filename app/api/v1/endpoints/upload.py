from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from app.services.s3.s3_config import s3_driver
from app.db.models import UploadResponse
from typing import Optional
from uuid import uuid4
import tempfile
import os

router = APIRouter(tags=["upload"])
