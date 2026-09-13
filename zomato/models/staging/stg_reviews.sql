SELECT
    r.review_id,
    r.order_id,
    r.user_id::number AS customer_id,
    r.restaurant_id::string AS restaurant_id,
    r.rating::number AS rating,
    r.comment::string AS comment,
    r.review_date::DATE AS review_date,
    res.city AS city,
FROM {{ source('raw', 'reviews') }} r
LEFT JOIN {{ ref('stg_restaurant') }} res ON r.restaurant_id = res.restaurant_id
WHERE r.comment IS NOT NULL