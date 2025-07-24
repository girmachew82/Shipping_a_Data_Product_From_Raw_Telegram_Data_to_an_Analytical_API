{{ config(materialized='table') }}

select
    channel,
    max(message_text) filter (where message_text is not null) as sample_message
from {{ ref('fct_messages') }}
group by channel_id