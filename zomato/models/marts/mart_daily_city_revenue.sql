SELECT 
    order_date, 
    city, 
    count(*) AS orders, 
    count_if(is_delivered) AS delivered_orders,
    round(div0(count_if(order_status='Cancelled'), count(*)),4) AS cancel_rate,
    sum(iff(is_delivered, sales_amount, 0)) AS gmv,
    round(div0(sum(iff(is_delivered, sales_amount,0)), count_if(is_delivered)),2) AS aov
FROM {{ ref('fct_orders') }} GROUP BY 1,2