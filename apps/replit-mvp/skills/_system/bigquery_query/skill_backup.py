from typing import Optional
import os
from google.cloud import bigquery
from skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

class Inputs(SkillInputs):
    sql: str
    location: Optional[str] = None            # "US" / "EU"
    destination_table: Optional[str] = None   # "dataset.table"
    max_preview_rows: int = 50
    dry_run: bool = False
    maximum_bytes_billed: Optional[int] = 5_000_000_000  # 5 GB default safety cap
    labels: Optional[dict] = {"aiden":"true","skill":"bigquery_query"}

class Outputs(SkillOutputs): pass

class SkillImpl(Skill):
    name = "bigquery_query"
    version = "0.2.0"
    caps = {"net"}
    Inputs = Inputs
    Outputs = Outputs

    def run(self, ctx: SkillContext, args: Inputs) -> Outputs:
        project = os.environ.get("GCP_PROJECT_ID")
        if not project:
            return Outputs(ok=False, message="GCP_PROJECT_ID not set")
        client = bigquery.Client(project=project)
        job_config = bigquery.QueryJobConfig()
        if args.destination_table:
            job_config.destination = args.destination_table
            job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
        if args.maximum_bytes_billed is not None:
            job_config.maximum_bytes_billed = int(args.maximum_bytes_billed)
        if args.dry_run:
            job_config.dry_run = True
            job_config.use_query_cache = False
        if args.labels:
            job_config.labels = {str(k):str(v) for k,v in dict(args.labels).items()}

        job = client.query(args.sql, job_config=job_config, location=args.location)
        if args.dry_run:
            return Outputs(ok=True, data={"total_bytes_processed": job.total_bytes_processed}, message="dry run only")

        result = job.result(page_size=min(args.max_preview_rows, 1000))
        preview = []
        for i, row in enumerate(result):
            if i >= args.max_preview_rows: break
            preview.append(dict(row.items()))
        data = {"job_id": job.job_id, "row_count": result.total_rows, "preview_rows": preview}
        if args.destination_table:
            data["destination_table"] = args.destination_table
        return Outputs(ok=True, data=data, message="query complete")