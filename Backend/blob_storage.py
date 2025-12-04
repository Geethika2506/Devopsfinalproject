"""Azure Blob Storage utility for file uploads."""
import os
from typing import Optional, BinaryIO
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv

load_dotenv()

# Azure Blob Storage configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "uploads")


def get_blob_service_client() -> Optional[BlobServiceClient]:
    """Get Azure Blob Service client."""
    if not AZURE_STORAGE_CONNECTION_STRING:
        return None
    try:
        return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    except Exception as e:
        print(f"Error connecting to Azure Blob Storage: {e}")
        return None


def get_container_client(container_name: str = None):
    """Get container client, create container if it doesn't exist."""
    blob_service = get_blob_service_client()
    if not blob_service:
        return None
    
    container = container_name or AZURE_STORAGE_CONTAINER_NAME
    container_client = blob_service.get_container_client(container)
    
    # Create container if it doesn't exist
    try:
        container_client.get_container_properties()
    except Exception:
        container_client.create_container(public_access="blob")
    
    return container_client


def upload_file(
    file_data: BinaryIO,
    filename: str,
    content_type: str = "application/octet-stream",
    container_name: str = None
) -> Optional[str]:
    """
    Upload a file to Azure Blob Storage.
    
    Args:
        file_data: File-like object to upload
        filename: Name to save the file as
        content_type: MIME type of the file
        container_name: Optional container name (uses default if not provided)
    
    Returns:
        URL of the uploaded file, or None if upload failed
    """
    container_client = get_container_client(container_name)
    if not container_client:
        return None
    
    try:
        # Set content settings for proper file serving
        content_settings = ContentSettings(content_type=content_type)
        
        # Upload the blob
        blob_client = container_client.get_blob_client(filename)
        blob_client.upload_blob(
            file_data,
            overwrite=True,
            content_settings=content_settings
        )
        
        # Return the URL
        return blob_client.url
    except Exception as e:
        print(f"Error uploading file to Azure Blob: {e}")
        return None


def delete_file(filename: str, container_name: str = None) -> bool:
    """
    Delete a file from Azure Blob Storage.
    
    Args:
        filename: Name of the file to delete
        container_name: Optional container name
    
    Returns:
        True if deleted, False otherwise
    """
    container_client = get_container_client(container_name)
    if not container_client:
        return False
    
    try:
        blob_client = container_client.get_blob_client(filename)
        blob_client.delete_blob()
        return True
    except Exception as e:
        print(f"Error deleting file from Azure Blob: {e}")
        return False


def list_files(container_name: str = None) -> list:
    """
    List all files in a container.
    
    Args:
        container_name: Optional container name
    
    Returns:
        List of blob names
    """
    container_client = get_container_client(container_name)
    if not container_client:
        return []
    
    try:
        return [blob.name for blob in container_client.list_blobs()]
    except Exception as e:
        print(f"Error listing files from Azure Blob: {e}")
        return []


def get_file_url(filename: str, container_name: str = None) -> Optional[str]:
    """
    Get the URL for a file in Azure Blob Storage.
    
    Args:
        filename: Name of the file
        container_name: Optional container name
    
    Returns:
        URL of the file, or None if not found
    """
    container_client = get_container_client(container_name)
    if not container_client:
        return None
    
    try:
        blob_client = container_client.get_blob_client(filename)
        return blob_client.url
    except Exception as e:
        print(f"Error getting file URL: {e}")
        return None


def is_blob_storage_configured() -> bool:
    """Check if Azure Blob Storage is configured."""
    return bool(AZURE_STORAGE_CONNECTION_STRING)
