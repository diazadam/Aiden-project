from typing import Optional
import os, mimetypes, datetime
from google.cloud import storage
from skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

class Inputs(SkillInputs):
    local_path: str
    bucket: str
    object_name: Optional[str] = None
    cache_control: Optional[str] = "public, max-age=300"
    signed_url_minutes: int = 15  # default signed link
    make_public: bool = False     # discouraged when Uniform Bucket-Level Access is on

class Outputs(SkillOutputs): pass

class SkillImpl(Skill):
    name = "gcs_upload"
    version = "0.2.0"
    caps = {"net","fs_write"}
    Inputs = Inputs
    Outputs = Outputs

    def run(self, ctx: SkillContext, args: Inputs) -> Outputs:
        if not os.path.exists(args.local_path):
            return Outputs(ok=False, message="local_path not found")
        client = storage.Client(project=os.environ.get("GCP_PROJECT_ID"))
        bucket = client.bucket(args.bucket)
        obj = args.object_name or os.path.basename(args.local_path)
        blob = bucket.blob(obj)
        ctype, _ = mimetypes.guess_type(args.local_path)
        blob.cache_control = args.cache_control or None
        blob.upload_from_filename(args.local_path, content_type=ctype or "application/octet-stream")

        data = {"gcs_uri": f"gs://{args.bucket}/{obj}"}

        if args.make_public:
            try:
                blob.make_public()
                data["public_url"] = blob.public_url
            except Exception as e:
                data["public_url_error"] = str(e)[:200]

        if args.signed_url_minutes and args.signed_url_minutes > 0:
            try:
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=datetime.timedelta(minutes=int(args.signed_url_minutes)),
                    method="GET"
                )
                data["signed_url"] = url
            except Exception as e:
                data["signed_url_error"] = str(e)[:200]

        return Outputs(ok=True, data=data, message="uploaded")