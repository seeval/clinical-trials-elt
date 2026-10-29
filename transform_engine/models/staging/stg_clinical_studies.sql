with source as (

    select * from {{ source('raw_clinical', 'studies') }}

),

extracted as (

    select
        nct_id,
        last_update_date,
        
        -- Identification Module fields
        payload->'protocolSection'->'identificationModule'->>'briefTitle' as brief_title,
        payload->'protocolSection'->'identificationModule'->>'officialTitle' as official_title,
        payload->'protocolSection'->'identificationModule'->>'acronym' as acronym,
        
        -- Status Module fields
        payload->'protocolSection'->'statusModule'->>'overallStatus' as overall_status,
        payload->'protocolSection'->'statusModule'->>'studyType' as study_type,
        
        -- Audit tracking
        payload_hash,
        ingested_at

    from source

)

select * from extracted
