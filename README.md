# Clinical Trials ELT Pipeline

Containerized ELT data engineering pipeline designed to ingest, model, transform, and orchestrate clinical trial data from the ClinicalTrials.gov API into a normalized star-schema data warehouse. Built to learn Dagster orchestration, Postgres, DuckDB, and data modeling practices for data/analytics engineering.

---

## Architecture & Tech Stack

* **Ingestion Engine:** Custom Python extraction scripts parsing REST payloads and landing raw records into PostgreSQL.
* **Transformation Engine:** `dbt` (Data Build Tool) utilizing a DuckDB adapter with zero-copy PostgreSQL bridge attachments (`postgres_db`).
* **Orchestration:** `Dagster` with custom `DagsterDbtTranslator` bindings linking Python source assets directly to dbt staging, intermediate, and fact models.
* **Infrastructure:** Containerized via Docker Compose (`postgres`, `dagster_webserver`, `dagster_daemon`).

---

## Project Structure

```text
clinical-trials-elt/
├── ingestion_engine/      # Python extraction logic & API clients
├── transform_engine/      # dbt project (models, sources, profiles)
│   ├── models/            # Staging, intermediate, and fact models
│   ├── profiles.yml       # DuckDB & PostgreSQL connection profiles
│   └── dbt_project.yml    # dbt project configurations
├── orchestration/         # Dagster definitions, assets, and schedules
├── docker-compose.yml     # Multi-container service definitions
├── workspace.yaml         # Dagster code location workspace configuration
└── README.md
```

---

## Data Modeling (Star Schema)

1. **Staging (`stg_`):** Flattens incoming JSON payloads from raw PostgreSQL tables.
2. **Intermediate (`int_`):** Handles complex grain expansions and unnesting relationships (e.g., 1:N study conditions mapping in `int_clinical_conditions`).
3. **Marts (`fct_`):** Core fact tables (`fct_clinical_trials`) keyed by `nct_id` containing study metrics, status dimensions, and enrollment figures.

---

## Quickstart & Local Development

### 1. Environment Setup
Clone the repository and ensure Docker and Docker Compose are installed on your host system.

### 2. Spin Up Infrastructure Stack
Launch the containerized data warehouse, webserver, and execution daemon:
```bash
docker compose up -d --build
```

### 3. Access Dagster UI
Open your browser and navigate to:
```text
http://localhost:3000
```
From the UI, you can inspect asset lineage, monitor run queues, or manually trigger the end-to-end pipeline materialization.

### 4. Running dbt Commands In-Container
To execute or debug transformations inside the containerized environment:
```bash
docker compose exec dagster_webserver dbt build --project-dir /app/transform_engine --profiles-dir /app/transform_engine
```
