-- This file contains the DDL for the /app/expenses.db database.

CREATE TABLE expenses (
    employee TEXT,
    exp_date date,
    currency TEXT,
    amount REAL,
    description TEXT
);

CREATE TABLE exchange_rate (
    currency text, 
    date text, 
    rate REAL, 
    PRIMARY KEY (currency, date)
);


-- Pre-populate exchange_rate table with CAD rate of 1.0 for each day since 2017-01-01
WITH RECURSIVE date_series AS (
    SELECT DATE('2017-01-01') AS date
    UNION ALL
    SELECT DATE(date, '+1 day')
    FROM date_series
    WHERE date < DATE('now')
)
INSERT INTO exchange_rate (currency, date, rate)
SELECT 'CAD', date, 1.0
FROM date_series;

