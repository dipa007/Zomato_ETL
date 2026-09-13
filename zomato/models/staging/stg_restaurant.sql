--parse the messy dimensions : (-- →null, 50+ ratings→50, ₹ 200→200, city after last comma)

SELECT
    id::number AS restaurant_id,
    name AS restaurant_name,
    trim(coalesce(regexp_substr(city, '[^,]+$'), city)) AS city,
    try_to_decimal(nullif(rating, '--'), 3, 1) AS rating,
    try_to_number(regexp_substr(rating_count, '[0-9]+')) AS rating_count,
    try_to_number(regexp_substr(cost, '[0-9]+')) AS cost_for_two,
    cuisine, 
    lic_no AS license_no
FROM {{ source('raw', 'restaurants') }} WHERE try_to_number(id) IS NOT NULL