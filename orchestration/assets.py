import os
from pathlib import Path
from dagster import AssetExecutionContext, AssetKey, asset
from dagster_dbt import DbtCliResource, DagsterDbtTranslator, dbt_assets

from ingestion_engine.extractor import ClinicalTrialsExtractor

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "clinical_dw"),
    "user": os.getenv("DB_USER", "analytics_user"),
    "password": os.getenv("DB_PASSWORD", "analytics_password"),
}

@asset(compute_kind="python", group_name="ingestion")
def raw_clinical_studies(context: AssetExecutionContext) -> dict:
    """Extracts raw clinical trial records from ClinicalTrials.gov API and upserts into PostgreSQL."""
    extractor = ClinicalTrialsExtractor(db_config=DB_CONFIG)
    total_processed = extractor.ingest_studies_batch(query_term="oncology", max_pages=2)
    context.log.info(f"Successfully processed and landed {total_processed} records.")
    return {"records_processed": total_processed}

DBT_PROJECT_DIR = Path(__file__).parent.parent / "transform_engine"

class CustomDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props):
        # Map the dbt source 'raw_clinical.studies' to our Python asset key ['raw_clinical_studies']
        if (
            dbt_resource_props["resource_type"] == "source"
            and dbt_resource_props["source_name"] == "raw_clinical"
            and dbt_resource_props["name"] == "studies"
        ):
            return AssetKey(["raw_clinical_studies"])
        
        return super().get_asset_key(dbt_resource_props)

@dbt_assets(
    manifest=DBT_PROJECT_DIR / "target" / "manifest.json",
    dagster_dbt_translator=CustomDbtTranslator(),
)
def clinical_dbt_models(context: AssetExecutionContext, dbt: DbtCliResource):
    """Executes dbt transformation graph (staging -> intermediate -> marts) using DuckDB zero-copy bridge."""
    yield from dbt.cli(["build"], context=context).stream()
