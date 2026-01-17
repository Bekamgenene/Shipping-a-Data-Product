WITH source AS (
    SELECT *
    FROM raw.telegram_messages
)

SELECT
    id AS message_id,
    date,
    message,
    from_id,
    channel,
    has_photo,
    -- Extract views and forwards from raw_json safely
    CAST(raw_json->>'views' AS INTEGER) AS views,
    CAST(raw_json->>'forwards' AS INTEGER) AS forwards,
    raw_json
FROM source
