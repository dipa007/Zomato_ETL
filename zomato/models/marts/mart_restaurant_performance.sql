SELECT
    f.restaurant_id, 
    r.restaurant_name, 
    r.city, 
    r.cuisine, 
    count(*) AS orders,
    sum(iff(f.is_delivered, f.sales_amount, 0)) AS revenue, 
    round(avg(f.customer_rating),2) AS avg_customer_rating,
    round(avg(f.delivery_time_min),1) AS avg_delivery_min
FROM {{ ref('fct_orders') }} f 
LEFT JOIN {{ ref('dim_restaurant') }} r USING (restaurant_id) 
GROUP BY 1,2,3,4