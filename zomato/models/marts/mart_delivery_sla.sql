SELECT city, 
    hour(order_timestamp) AS order_hour, 
    count_if(is_delivered) AS delivered_orders,
    round(median(delivery_time_min),1) AS p50, 
    round(percentile_cont(0.9) WITHIN group (ORDER BY delivery_time_min),1) AS p90
    FROM {{ ref('fct_orders') }} 
WHERE is_delivered 
GROUP BY 1,2