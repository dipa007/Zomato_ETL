WITH spine AS (
    SELECT dateadd(day, seq4(), '2024-01-01'::date) AS date_day 
    FROM
    table(generator(rowcount=>1200)))
SELECT date_day, year(date_day) AS year, month(date_day) AS month, monthname(date_day) AS month_name,
       dayname(date_day) AS day_name, (dayofweekiso(date_day)>=6) AS is_weekend
FROM spine WHERE date_day <= '2026-12-31'