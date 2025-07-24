-- {{ config(materialized='table') }}

-- with dates as (
--     select generate_series(
--         date '2023-01-01',
--         date '2030-12-31',
--         interval '1 day'
--     )::date as calendar_date
-- )

-- select
--     calendar_date,
--     extract(year from calendar_date) as year,
--     extract(month from calendar_date) as month,
--     extract(day from calendar_date) as day,
--     to_char(calendar_date, 'Day') as day_of_week
-- from dates
with date_data as (
  select
    distinct date as date_id,
    extract(day from date) as day,
    extract(dayofweek from date) as day_of_week,
    extract(month from date) as month,
    extract(year from date) as year
  from {{ ref('fct_messages') }}
)

select * from date_data