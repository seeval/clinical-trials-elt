import hashlib
import json
import logging
from typing import Dict, Any, List, Optional
import psycopg2
from psycopg2.extras import execute_values
import requests
from requests.exceptions import HTTPError, RequestException
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_not_exception_type,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ClinicalTrialsExtractor:
    """Handles rate-limited extraction from ClinicalTrials.gov API v2 and lands raw JSON into Postgres."""

    BASE_URL = "https://clinicaltrials.gov/api/v2"

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config

    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RequestException) & retry_if_not_exception_type(HTTPError),
    )
    def _fetch_page(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/studies"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def ingest_studies_batch(self, query_term: str = "oncology", max_pages: int = 2) -> int:
        """Pulls studies using token-based pagination and upserts raw JSON into Postgres."""
        page_token: Optional[str] = None
        total_upserted = 0

        for page in range(max_pages):
            params: Dict[str, Any] = {"query.term": query_term, "pageSize": 100}
            if page_token:
                params["pageToken"] = page_token

            logging.info(f"Fetching ClinicalTrials.gov page {page + 1} for term '{query_term}'...")
            data = self._fetch_page(params=params)
            
            studies = data.get("studies", [])
            if not studies:
                break

            records_to_upsert = []
            for study in studies:
                protocol = study.get("protocolSection", {})
                nct_id = protocol.get("identificationModule", {}).get("nctId")
                if not nct_id:
                    continue

                payload_str = json.dumps(study)
                payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
                

                raw_date = (
                    protocol.get("statusModule", {}).get("lastUpdatePostDate")
                    or protocol.get("statusModule", {}).get("statusVerifiedDate")
                )

                # Normalize partial dates (e.g., '2026-07' -> '2026-07-01')
                normalized_date = None
                if raw_date:
                    if len(raw_date) == 7:  # YYYY-MM
                        normalized_date = f"{raw_date}-01"
                    elif len(raw_date) == 4:  # YYYY
                        normalized_date = f"{raw_date}-01-01"
                    else:
                        normalized_date = raw_date[:10]  # Take YYYY-MM-DD prefix if longer timestamp

                records_to_upsert.append((
                    nct_id,
                    normalized_date,
                    payload_str,
                    payload_hash
                ))

            if records_to_upsert:
                query = """
                    INSERT INTO raw_clinical.studies (nct_id, last_update_date, payload, payload_hash)
                    VALUES %s
                    ON CONFLICT (nct_id) DO UPDATE SET
                        last_update_date = EXCLUDED.last_update_date,
                        payload = EXCLUDED.payload,
                        payload_hash = EXCLUDED.payload_hash,
                        ingested_at = CURRENT_TIMESTAMP
                    WHERE raw_clinical.studies.payload_hash != EXCLUDED.payload_hash;
                """
                with self._get_connection() as conn:
                    with conn.cursor() as cursor:
                        execute_values(cursor, query, records_to_upsert, template="(%s, %s, %s::jsonb, %s)")
                        conn.commit()
                
                total_upserted += len(records_to_upsert)
                logging.info(f"Landed/updated {len(records_to_upsert)} studies on page {page + 1}.")

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        logging.info(f"Ingestion complete. Total studies processed: {total_upserted}")
        return total_upserted


if __name__ == "__main__":
    DB_CONFIG = {
        "host": "localhost",
        "port": 5432,
        "dbname": "clinical_dw",
        "user": "analytics_user",
        "password": "analytics_password",
    }
    extractor = ClinicalTrialsExtractor(db_config=DB_CONFIG)
    extractor.ingest_studies_batch(query_term="oncology", max_pages=2)
