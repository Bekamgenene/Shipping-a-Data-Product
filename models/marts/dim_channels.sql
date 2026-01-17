WITH channel_stats AS (
    SELECT
        channel,
        COUNT(message_id) AS total_posts,
        SUM(views) AS total_views,
        AVG(views) AS avg_views
    FROM {{ ref('stg_telegram_messages') }}
    GROUP BY channel
)

SELECT
    md5(channel) AS channel_key,
    channel AS channel_name,
    total_posts,
    total_views,
    avg_views
FROM channel_stats
