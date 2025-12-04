"""File upload router for Azure Blob Storage."""
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from typing import List
from pydantic import BaseModel

from blob_storage import (
    upload_file, delete_file, list_files, 
    get_file_url, is_blob_storage_configured
)
from auth import get_current_user
from models import User

router = APIRouter(prefix="/uploads", tags=["uploads"])


class UploadResponse(BaseModel):
    """Response model for file upload."""
    filename: str
    url: str
    content_type: str


class FileListResponse(BaseModel):
    """Response model for file listing."""
    files: List[str]
    count: int


class StorageStatusResponse(BaseModel):
    """Response model for storage status."""
    configured: bool
    message: str


@router.get("/status", response_model=StorageStatusResponse)
def get_storage_status():
    """Check if Azure Blob Storage is configured."""
    configured = is_blob_storage_configured()
    return StorageStatusResponse(
        configured=configured,
        message="Azure Blob Storage is configured" if configured 
                else "Azure Blob Storage is not configured. Set AZURE_STORAGE_CONNECTION_STRING environment variable."
    )


@router.post("/", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file to Azure Blob Storage.
    
    Requires authentication. Supports images and common file types.
    """
    if not is_blob_storage_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage is not configured"
        )
    
    # Validate file type (allow common image types)
    allowed_types = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf", "text/plain"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed. Allowed: {', '.join(allowed_types)}"
        )
    
    # Generate unique filename to prevent collisions
    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
    
    # Upload to Azure Blob
    url = upload_file(
        file_data=file.file,
        filename=unique_filename,
        content_type=file.content_type
    )
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage"
        )
    
    return UploadResponse(
        filename=unique_filename,
        url=url,
        content_type=file.content_type
    )


@router.get("/", response_model=FileListResponse)
def list_uploaded_files(current_user: User = Depends(get_current_user)):
    """List all uploaded files. Requires authentication."""
    if not is_blob_storage_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage is not configured"
        )
    
    files = list_files()
    return FileListResponse(files=files, count=len(files))


@router.delete("/{filename}")
def delete_uploaded_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a file from storage. Requires authentication."""
    if not is_blob_storage_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage is not configured"
        )
    
    success = delete_file(filename)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or could not be deleted"
        )
    
    return {"message": f"File {filename} deleted successfully"}


@router.get("/{filename}/url")
def get_uploaded_file_url(filename: str):
    """Get the URL for a specific file."""
    if not is_blob_storage_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure Blob Storage is not configured"
        )
    
    url = get_file_url(filename)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return {"filename": filename, "url": url}
