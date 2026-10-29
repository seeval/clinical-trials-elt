{{
    config(
        materialized='table'
    )
}}

with intermediate as (

    select * from {{ ref('int_clinical_studies_summary') }}

),

final as (

    select
        nct_id,
        brief_title,
        overall_status,
        study_type,
        
        -- Eligibility dimensions
        minimum_age,
        maximum_age,
        sex,
        case 
            when healthy_volunteers = 'true' then true 
            else false 
        end as accepts_healthy_volunteers,

        last_update_date,
        ingested_at,

        -- Analytical flags
        case
            when overall_status = 'COMPLETED' then true
            else false
        end as is_completed

    from intermediate

)

select * from final
