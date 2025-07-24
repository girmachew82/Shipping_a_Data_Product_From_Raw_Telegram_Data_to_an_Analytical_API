select *
from {{ ref('stg_telegram_messages') }}
where message_text is null or trim(message_text) = ''