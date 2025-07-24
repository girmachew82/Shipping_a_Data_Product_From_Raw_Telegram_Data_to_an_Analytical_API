with source as (
    select * from raw_data.tgram_messages
),

flattened as (
    select
        ('message_id')::bigint as message_id,
        ('channel') as channel,
        ('date')::timestamp as message_date,
        ('message_text') as message_text,
        ('channel_id') as channel_id,
        ('views') as views,
        length('message_text') as message_length,
    from source
 
),
