Detections ↔ Messages joining

Overview:
- Image detections are stored in the analytics schema table `analytics.fct_image_detections`.
- Messages are stored in `analytics.fct_messages` (the core message fact used by downstream models).

Primary join keys:
- `fct_image_detections.message_id` → `fct_messages.message_id` (primary join).
- `channel` may also be available in `fct_messages` and can be used as an additional filter to narrow joins.

How the dbt model exposes the mapping:
- dbt model `marts.fct_image_detection` (dbt/medical_warehouse/models/marts/fct_image_detection.sql) performs a LEFT JOIN to the seeded `image_categories` mapping to expose `image_category`.
- The seed file is `dbt/medical_warehouse/seeds/image_categories.csv` and maps raw `object_class` values to higher-level `image_category` values.

Usage patterns:
- To include message context with detections, LEFT JOIN `fct_image_detection` to `fct_messages` ON `message_id`.
- Use additional filters such as `channel` or `date` to restrict results.

Extensibility:
- Add new `object_class` → `image_category` mappings to the seed CSV and run `dbt seed` + `dbt build`.
- If new detection fields are added (for example bounding boxes or source image path), include them in `analytics.fct_image_detections` and update `marts.fct_image_detection` accordingly.

API support:
- The FastAPI endpoint `/api/reports/visual-content` (fastapi_app/main.py) returns detections joined to messages and supports `?csv=true` to download results as CSV.

Notes:
- Message IDs are assumed globally unique. If your ingestion assigns non-unique message IDs across channels, include `channel` in the join condition.
