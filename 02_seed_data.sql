-- ============================================================
-- Seed Data — Companies & Sectors
-- ============================================================
USE stock_market;

INSERT INTO sectors (sector_name) VALUES
    ('Technology'),
    ('Finance'),
    ('Healthcare'),
    ('Energy'),
    ('Consumer Goods');

INSERT INTO companies (ticker, company_name, sector_id) VALUES
    ('AAPL',  'Apple Inc.',            1),
    ('MSFT',  'Microsoft Corp.',       1),
    ('GOOGL', 'Alphabet Inc.',         1),
    ('JPM',   'JPMorgan Chase & Co.',  2),
    ('JNJ',   'Johnson & Johnson',     3),
    ('XOM',   'Exxon Mobil Corp.',     4),
    ('PG',    'Procter & Gamble Co.',  5);

-- Populate trading_days (2023-01-01 to 2024-12-31, weekdays only)
INSERT INTO trading_days (trading_date)
WITH RECURSIVE dates AS (
    SELECT DATE('2023-01-01') AS d
    UNION ALL
    SELECT DATE_ADD(d, INTERVAL 1 DAY) FROM dates WHERE d < '2024-12-31'
)
SELECT d FROM dates WHERE DAYOFWEEK(d) NOT IN (1, 7);

-- Generate ~50,000 stock price records via cross join + random values
INSERT INTO stock_prices (company_id, trading_date, open_price, close_price, high_price, low_price, volume)
SELECT
    c.company_id,
    td.trading_date,
    ROUND(100 + RAND() * 400, 4)  AS open_price,
    ROUND(100 + RAND() * 400, 4)  AS close_price,
    ROUND(110 + RAND() * 400, 4)  AS high_price,
    ROUND(90  + RAND() * 380, 4)  AS low_price,
    FLOOR(1000000 + RAND() * 9000000) AS volume
FROM companies c
CROSS JOIN trading_days td;
