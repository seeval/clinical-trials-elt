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

        -- Conditions Module (Raw JSON Array)
        payload->'protocolSection'->'conditionsModule'->'conditions' as conditions_array,

        -- Eligibility Module fields
        payload->'protocolSection'->'eligibilityModule'->>'minimumAge' as minimum_age,
        payload->'protocolSection'->'eligibilityModule'->>'maximumAge' as maximum_age,
        payload->'protocolSection'->'eligibilityModule'->>'sex' as sex,
        payload->'protocolSection'->'eligibilityModule'->>'healthyVolunteers' as healthy_volunteers,

        -- Audit tracking
        payload_hash,
        ingested_at

    from source

)

select * from extracted
