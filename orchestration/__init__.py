from pathlib import Path
from dagster import Definitions, define_asset_job, ScheduleDefinition
from dagster_dbt import DbtCliResource

from . import assets

DBT_PROJECT_DIR = Path(__file__).parent.parent / "transform_engine"

daily_clinical_job = define_asset_job(
    name="daily_clinical_etl_job",
    selection="*"
)

daily_schedule = ScheduleDefinition(
    job=daily_clinical_job,
    cron_schedule="0 6 * * *",  # Scheduled for 6:00 AM daily
    execution_timezone="America/New_York",
)

defs = Definitions(
    assets=[assets.raw_clinical_studies, assets.clinical_dbt_models],
    resources={
        "dbt": DbtCliResource(project_dir=str(DBT_PROJECT_DIR)),
    },
    schedules=[daily_schedule],
)
