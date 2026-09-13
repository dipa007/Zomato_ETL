SELECT
    customer_id,
    customer_name,
    email,
    age,
    gender,
    CASE WHEN age < 25 then 'Gen Z'
         WHEN age < 40 then 'Millennial'
         WHEN age < 55 then 'Gen X'
         WHEN age is null then 'Unknown'
         ELSE 'Boomer' END as age_segment,
    marital_status,
    occupation,
    income_band,
    education,
    family_size
FROM {{ ref('stg_users') }}