-- Enrich image detection facts with a human-friendly `image_category` mapping
WITH detections AS (
    SELECT
        id AS detection_id,
        message_id,
        object_class,
        confidence
    FROM analytics.fct_image_detections
)

SELECT
    d.detection_id,
    d.message_id,
    d.object_class,
    ic.image_category,
    d.confidence
FROM detections d
LEFT JOIN {{ ref('image_categories') }} ic
    ON LOWER(d.object_class) = LOWER(ic.object_class)