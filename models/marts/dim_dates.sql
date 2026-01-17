SELECT DISTINCT
    TO_CHAR(DATE(date), 'YYYYMMDD') AS date_key,
    DATE(date) AS date,
    EXTRACT(DOW FROM date) AS weekday,
    EXTRACT(WEEK FROM date) AS week,
    EXTRACT(MONTH FROM date) AS month,
    EXTRACT(QUARTER FROM date) AS quarter,
    EXTRACT(YEAR FROM date) AS year,
    CASE 
        WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN TRUE 
        ELSE FALSE 
    END AS is_weekend
FROM {{ ref('stg_telegram_messages') }}
