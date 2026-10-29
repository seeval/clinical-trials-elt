{{
    config(
        materialized='table'
    )
}}

with summary as (

    select 
        nct_id,
        conditions_array
    from {{ ref('int_clinical_studies_summary') }}
    where conditions_array is not null

),

unnested as (
    -- Cast the JSON array field directly to a Postgres/DuckDB text array
    select
        nct_id,
        conditions_array::VARCHAR[] as condition_list
    from summary
)

select
    nct_id,
    trim(lower(unnest(condition_list))) as condition_name
from unnested
