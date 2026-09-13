SELECT 
    order_item_id, 
    order_id, 
    r_id AS restaurant_id, 
    f_id, 
    price::decimal(10,2) AS price, 
    quantity::number AS quantity, 
    line_amount::decimal(10,2) AS  line_amount
FROM {{ source('raw', 'order_items') }}