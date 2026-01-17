SELECT
    message_id,
    md5(channel) AS channel_key,
    TO_CHAR(DATE(date), 'YYYYMMDD') AS date_key,
    views AS view_count,
    forwards AS forward_count,
    has_photo AS has_image,
    LENGTH(message) AS message_length
FROM {{ ref('stg_telegram_messages') }}
