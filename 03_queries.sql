-- ============================================================
-- Advanced SQL Queries — Window Functions, CTEs, Analytics
-- MySQL 8.0
-- ============================================================
USE stock_market;

-- ── 1. Moving Averages (MA5, MA20, MA50) using window functions ──
SELECT
    c.ticker,
    sp.trading_date,
    sp.close_price,
    ROUND(AVG(sp.close_price) OVER (
        PARTITION BY sp.company_id ORDER BY sp.trading_date
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW), 4) AS ma5,
    ROUND(AVG(sp.close_price) OVER (
        PARTITION BY sp.company_id ORDER BY sp.trading_date
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 4) AS ma20,
    ROUND(AVG(sp.close_price) OVER (
        PARTITION BY sp.company_id ORDER BY sp.trading_date
        ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 4) AS ma50
FROM stock_prices sp
JOIN companies c USING (company_id)
WHERE c.ticker = 'AAPL'
ORDER BY sp.trading_date;


-- ── 2. Daily Returns using LAG ──
SELECT
    c.ticker,
    sp.trading_date,
    sp.close_price,
    LAG(sp.close_price) OVER (
        PARTITION BY sp.company_id ORDER BY sp.trading_date) AS prev_close,
    ROUND(
        (sp.close_price - LAG(sp.close_price) OVER (
            PARTITION BY sp.company_id ORDER BY sp.trading_date))
        / LAG(sp.close_price) OVER (
            PARTITION BY sp.company_id ORDER BY sp.trading_date) * 100,
    4) AS daily_return_pct
FROM stock_prices sp
JOIN companies c USING (company_id)
ORDER BY c.ticker, sp.trading_date;


-- ── 3. 52-Week High/Low using FIRST_VALUE ──
SELECT DISTINCT
    c.ticker,
    FIRST_VALUE(sp.high_price) OVER (
        PARTITION BY sp.company_id ORDER BY sp.high_price DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS week52_high,
    FIRST_VALUE(sp.low_price) OVER (
        PARTITION BY sp.company_id ORDER BY sp.low_price ASC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS week52_low
FROM stock_prices sp
JOIN companies c USING (company_id)
WHERE sp.trading_date >= DATE_SUB(CURDATE(), INTERVAL 52 WEEK);


-- ── 4. Volatility (STDDEV of daily returns) per company ──
WITH daily_returns AS (
    SELECT
        company_id,
        trading_date,
        (close_price - LAG(close_price) OVER (
            PARTITION BY company_id ORDER BY trading_date))
        / LAG(close_price) OVER (
            PARTITION BY company_id ORDER BY trading_date) AS ret
    FROM stock_prices
)
SELECT
    c.ticker,
    c.company_name,
    ROUND(STDDEV(dr.ret) * 100, 4) AS daily_volatility_pct,
    ROUND(STDDEV(dr.ret) * SQRT(252) * 100, 4) AS annualised_volatility_pct
FROM daily_returns dr
JOIN companies c USING (company_id)
GROUP BY c.company_id, c.ticker, c.company_name
ORDER BY annualised_volatility_pct DESC;


-- ── 5. Top volume days per company ──
WITH ranked_vol AS (
    SELECT
        company_id,
        trading_date,
        volume,
        RANK() OVER (PARTITION BY company_id ORDER BY volume DESC) AS vol_rank
    FROM stock_prices
)
SELECT c.ticker, rv.trading_date, rv.volume
FROM ranked_vol rv
JOIN companies c USING (company_id)
WHERE rv.vol_rank <= 5
ORDER BY c.ticker, rv.vol_rank;


-- ── 6. Stored Procedure: price range query ──
DELIMITER $$

CREATE PROCEDURE GetPriceRange(
    IN  p_ticker     VARCHAR(10),
    IN  p_start_date DATE,
    IN  p_end_date   DATE
)
BEGIN
    SELECT
        c.ticker,
        sp.trading_date,
        sp.open_price,
        sp.close_price,
        sp.high_price,
        sp.low_price,
        sp.volume
    FROM stock_prices sp
    JOIN companies c USING (company_id)
    WHERE c.ticker = p_ticker
      AND sp.trading_date BETWEEN p_start_date AND p_end_date
    ORDER BY sp.trading_date;
END$$

DELIMITER ;

-- Usage:
-- CALL GetPriceRange('AAPL', '2024-01-01', '2024-03-31');
