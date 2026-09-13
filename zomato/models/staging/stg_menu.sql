SELECT
    menu_id, 
    try_to_number(r_id) AS restaurant_id, 
    f_id, 
    cuisine, 
    try_to_decimal(price,10,2) AS price
FROM {{ source('raw', 'menu') }} WHERE try_to_number(r_id) IS NOT NULL AND try_to_decimal(price,10,2) > 0