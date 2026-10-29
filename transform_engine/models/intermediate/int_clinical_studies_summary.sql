with staging as (

    select * from {{ ref('stg_clinical_studies') }}

),

transformed as (

    select
        nct_id,
        brief_title,
        official_title,
        acronym,
        
        -- Standardize status text
        coalesce(overall_status, 'UNKNOWN') as overall_status,
        coalesce(study_type, 'UNKNOWN') as study_type,
        
        -- Date handling & audit
        last_update_date,
        ingested_at,
        payload_hash

    from staging

)

select * from transformed
