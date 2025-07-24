{{ config(materialized='table') }}

select
    message_id,
    channel,
    date,
    message_text,
    channel_id,
    views,
from {{ ref('stg_telegram_messages') }} 
