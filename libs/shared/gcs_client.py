"""
Google Cloud Storage Client for Aiden/Jarvis
===========================================

Simple GCS client for file operations with automatic service account handling.

Usage:
    from libs.shared.gcs_client import upload_bytes, upload_file, download_file
    
    # Upload data
    url = upload_bytes("my-bucket", "logs/execution.json", json_data, "application/json")
    
    # Upload file  
    url = upload_file("my-bucket", "backups/config.yaml", "/local/path/config.yaml")
    
    # Download file
    success = download_file("my-bucket", "data/model.pkl", "/local/cache/model.pkl")
"""
import os
import json
from pathlib import Path
from base64 import b64decode
from typing import Optional, Union

# Lazy imports to avoid dependency issues
_storage_client = None
_project_id = None

def _ensure_credentials():
    """Ensure GCP credentials are available"""
    global _storage_client, _project_id
    
    if _storage_client is not None:
        return _storage_client
    
    # Try to materialize service account file from base64 env var
    gcp_sa_b64 = os.getenv("GCP_SA_JSON_BASE64")
    gcp_sa_path = os.getenv("GCP_SA_PATH", "/tmp/gcp_sa.json")
    _project_id = os.getenv("GCP_PROJECT_ID")
    
    if gcp_sa_b64:
        try:
            sa_json = b64decode(gcp_sa_b64).decode('utf-8')
            Path(gcp_sa_path).write_text(sa_json)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_sa_path
            print(f"✓ Materialized GCP service account to {gcp_sa_path}")
        except Exception as e:
            print(f"⚠️  Could not materialize GCP service account: {e}")
    
    # Check if credentials file exists
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", gcp_sa_path)
    if not Path(creds_path).exists():
        raise RuntimeError(
            f"GCP service account not found at {creds_path}. "
            f"Set GCP_SA_JSON_BASE64 or ensure {creds_path} exists."
        )
    
    try:
        from google.cloud import storage
        _storage_client = storage.Client(project=_project_id)
        print(f"✓ GCS client initialized for project {_project_id}")
        return _storage_client
    except ImportError:
        raise RuntimeError("google-cloud-storage not installed. Run: pip install google-cloud-storage")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize GCS client: {e}")

def upload_bytes(bucket_name: str, destination_path: str, data: Union[bytes, str], 
                content_type: str = "application/octet-stream") -> str:
    """
    Upload bytes/string data to GCS
    
    Args:
        bucket_name: GCS bucket name
        destination_path: Path within bucket (e.g., "logs/file.json")
        data: Data to upload (bytes or string)
        content_type: MIME type
    
    Returns:
        gs:// URL of uploaded object
    """
    client = _ensure_credentials()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_path)
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    try:
        blob.upload_from_string(data, content_type=content_type)
        return f"gs://{bucket_name}/{destination_path}"
    except Exception as e:
        raise RuntimeError(f"Failed to upload to gs://{bucket_name}/{destination_path}: {e}")

def upload_file(bucket_name: str, destination_path: str, local_path: Union[str, Path]) -> str:
    """
    Upload a local file to GCS
    
    Args:
        bucket_name: GCS bucket name
        destination_path: Path within bucket
        local_path: Local file path
    
    Returns:
        gs:// URL of uploaded object
    """
    client = _ensure_credentials()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_path)
    
    local_file = Path(local_path)
    if not local_file.exists():
        raise FileNotFoundError(f"Local file not found: {local_file}")
    
    try:
        blob.upload_from_filename(str(local_file))
        return f"gs://{bucket_name}/{destination_path}"
    except Exception as e:
        raise RuntimeError(f"Failed to upload {local_file} to gs://{bucket_name}/{destination_path}: {e}")

def download_file(bucket_name: str, source_path: str, local_path: Union[str, Path]) -> bool:
    """
    Download a file from GCS to local storage
    
    Args:
        bucket_name: GCS bucket name
        source_path: Path within bucket
        local_path: Local destination path
    
    Returns:
        True if download successful
    """
    client = _ensure_credentials()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_path)
    
    local_file = Path(local_path)
    local_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        blob.download_to_filename(str(local_file))
        return True
    except Exception as e:
        print(f"Failed to download gs://{bucket_name}/{source_path} to {local_file}: {e}")
        return False

def download_bytes(bucket_name: str, source_path: str) -> Optional[bytes]:
    """
    Download file content as bytes
    
    Args:
        bucket_name: GCS bucket name
        source_path: Path within bucket
    
    Returns:
        File content as bytes, or None if failed
    """
    client = _ensure_credentials()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_path)
    
    try:
        return blob.download_as_bytes()
    except Exception as e:
        print(f"Failed to download gs://{bucket_name}/{source_path}: {e}")
        return None

def list_objects(bucket_name: str, prefix: str = "") -> list[str]:
    """
    List objects in a GCS bucket with optional prefix
    
    Args:
        bucket_name: GCS bucket name
        prefix: Optional path prefix to filter results
    
    Returns:
        List of object paths
    """
    client = _ensure_credentials()
    bucket = client.bucket(bucket_name)
    
    try:
        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]
    except Exception as e:
        print(f"Failed to list objects in gs://{bucket_name}/{prefix}: {e}")
        return []

def delete_object(bucket_name: str, object_path: str) -> bool:
    """
    Delete an object from GCS
    
    Args:
        bucket_name: GCS bucket name
        object_path: Path within bucket
    
    Returns:
        True if deletion successful
    """
    client = _ensure_credentials()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_path)
    
    try:
        blob.delete()
        return True
    except Exception as e:
        print(f"Failed to delete gs://{bucket_name}/{object_path}: {e}")
        return False

def object_exists(bucket_name: str, object_path: str) -> bool:
    """
    Check if an object exists in GCS
    
    Args:
        bucket_name: GCS bucket name
        object_path: Path within bucket
    
    Returns:
        True if object exists
    """
    client = _ensure_credentials()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_path)
    
    try:
        return blob.exists()
    except Exception as e:
        print(f"Failed to check existence of gs://{bucket_name}/{object_path}: {e}")
        return False

# Convenience functions for common operations
def backup_logs_to_gcs(bucket_name: str, local_logs_dir: Union[str, Path] = "logs") -> list[str]:
    """
    Backup all log files to GCS
    
    Args:
        bucket_name: GCS bucket name
        local_logs_dir: Local logs directory
    
    Returns:
        List of uploaded gs:// URLs
    """
    logs_path = Path(local_logs_dir)
    if not logs_path.exists():
        return []
    
    uploaded = []
    for log_file in logs_path.glob("*.log"):
        try:
            destination = f"backups/logs/{log_file.name}"
            url = upload_file(bucket_name, destination, log_file)
            uploaded.append(url)
            print(f"✓ Backed up {log_file.name} to {url}")
        except Exception as e:
            print(f"✗ Failed to backup {log_file.name}: {e}")
    
    return uploaded

def upload_json_data(bucket_name: str, destination_path: str, data: dict) -> str:
    """
    Upload JSON data to GCS
    
    Args:
        bucket_name: GCS bucket name
        destination_path: Path within bucket
        data: Dictionary to serialize as JSON
    
    Returns:
        gs:// URL of uploaded object
    """
    json_bytes = json.dumps(data, indent=2).encode('utf-8')
    return upload_bytes(bucket_name, destination_path, json_bytes, "application/json")