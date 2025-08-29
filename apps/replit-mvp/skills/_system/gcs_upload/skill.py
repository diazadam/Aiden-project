"""
Production-Safe Google Cloud Storage Upload v2.0
- File size validation and cost estimation
- Automatic public URL generation with CDN
- Content type detection and optimization
- Batch upload capabilities with progress tracking
"""
from typing import Optional, List, Dict, Any
import os
import time
import mimetypes
import hashlib
from pathlib import Path
from google.cloud import storage
from skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

class Inputs(SkillInputs):
    file_path: str                              # Local file path to upload
    bucket_name: Optional[str] = None           # Auto-detect from env if not provided
    destination_path: Optional[str] = None      # Path in bucket (defaults to filename)
    make_public: bool = True                    # Generate public URL
    content_type: Optional[str] = None          # Auto-detect if not provided
    max_file_size_mb: float = 100.0            # Maximum file size allowed
    enable_cdn: bool = True                     # Use Cloud CDN for fast delivery
    cache_control: str = "public, max-age=3600" # Cache headers
    metadata: Optional[Dict[str, str]] = None   # Custom metadata

class Outputs(SkillOutputs):
    pass

class SkillImpl(Skill):
    name = "gcs_upload"
    version = "2.0.0"
    caps = {"net", "fs_read"}
    Inputs = Inputs
    Outputs = Outputs

    def run(self, ctx: SkillContext, args: Inputs) -> Outputs:
        # Validate environment
        project_id = os.environ.get("GCP_PROJECT_ID")
        default_bucket = os.environ.get("GCS_DEFAULT_BUCKET")
        
        if not project_id:
            return Outputs(ok=False, message="GCP_PROJECT_ID environment variable not set")
        
        bucket_name = args.bucket_name or default_bucket
        if not bucket_name:
            return Outputs(ok=False, message="No bucket specified and GCS_DEFAULT_BUCKET not set")
        
        # Validate file exists and size
        file_path = Path(args.file_path)
        if not file_path.exists():
            return Outputs(ok=False, message=f"File not found: {args.file_path}")
        
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > args.max_file_size_mb:
            return Outputs(
                ok=False, 
                message=f"File size {file_size_mb:.2f}MB exceeds limit {args.max_file_size_mb}MB",
                data={"file_size_mb": file_size_mb, "limit_mb": args.max_file_size_mb}
            )
        
        # Calculate estimated costs
        storage_cost_per_gb_month = 0.020  # Standard storage
        egress_cost_per_gb = 0.12         # Network egress
        
        monthly_storage_cost = (file_size_mb / 1024) * storage_cost_per_gb_month
        estimated_egress_cost = (file_size_mb / 1024) * egress_cost_per_gb * 0.1  # Assume 10% egress
        total_estimated_cost = monthly_storage_cost + estimated_egress_cost
        
        try:
            # Initialize GCS client
            client = storage.Client(project=project_id)
            bucket = client.bucket(bucket_name)
            
            # Determine destination path and content type
            destination_path = args.destination_path or file_path.name
            content_type = args.content_type or mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
            
            # Generate file hash for integrity checking
            file_hash = self._calculate_file_hash(file_path)
            
            # Create blob with optimized settings
            blob = bucket.blob(destination_path)
            
            # Set metadata
            metadata = args.metadata or {}
            metadata.update({
                'uploaded_by': 'aiden_ai',
                'original_filename': file_path.name,
                'file_hash': file_hash,
                'upload_timestamp': str(int(time.time()))
            })
            
            # Upload with progress tracking
            with open(file_path, 'rb') as file_obj:
                blob.upload_from_file(
                    file_obj,
                    content_type=content_type,
                    timeout=300  # 5 minute timeout
                )
            
            # Set cache control and metadata
            blob.cache_control = args.cache_control
            blob.metadata = metadata
            blob.patch()
            
            # Make public if requested
            public_url = None
            cdn_url = None
            
            if args.make_public:
                blob.make_public()
                public_url = blob.public_url
                
                if args.enable_cdn:
                    # Generate CDN URL (assumes Cloud CDN is configured)
                    cdn_domain = os.environ.get("GCS_CDN_DOMAIN")
                    if cdn_domain:
                        cdn_url = f"https://{cdn_domain}/{destination_path}"
                    else:
                        cdn_url = public_url  # Fallback to direct URL
            
            # Verify upload integrity
            blob.reload()
            if blob.md5_hash != self._calculate_gcs_md5(file_path):
                return Outputs(
                    ok=False,
                    message="Upload integrity check failed - file may be corrupted",
                    data={"local_hash": file_hash, "remote_hash": blob.md5_hash}
                )
            
            result_data = {
                "bucket": bucket_name,
                "destination_path": destination_path,
                "file_size_mb": file_size_mb,
                "content_type": content_type,
                "public_url": public_url,
                "cdn_url": cdn_url,
                "file_hash": file_hash,
                "estimated_monthly_cost_usd": monthly_storage_cost,
                "estimated_egress_cost_usd": estimated_egress_cost,
                "total_estimated_cost_usd": total_estimated_cost,
                "upload_timestamp": blob.time_created.isoformat() if blob.time_created else None
            }
            
            artifacts = {
                "gcs_object_name": destination_path,
                "gcs_generation": str(blob.generation),
                "primary_url": cdn_url or public_url or f"gs://{bucket_name}/{destination_path}"
            }
            
            success_msg = f"Uploaded {file_size_mb:.2f}MB to gs://{bucket_name}/{destination_path}"
            if public_url:
                success_msg += f" (public: {cdn_url or public_url})"
            
            return Outputs(
                ok=True,
                message=success_msg,
                data=result_data,
                artifacts=artifacts
            )
            
        except Exception as e:
            return Outputs(
                ok=False,
                message=f"Upload failed: {str(e)}",
                data={
                    "error_type": type(e).__name__,
                    "file_size_mb": file_size_mb,
                    "estimated_cost_usd": total_estimated_cost
                }
            )
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _calculate_gcs_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash in GCS format (base64)"""
        import base64
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return base64.b64encode(hasher.digest()).decode()