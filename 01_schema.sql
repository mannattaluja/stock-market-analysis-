-- ============================================================
-- Stock Market Analysis Database — 3NF Normalized Schema
-- MySQL 8.0
-- ============================================================

CREATE DATABASE IF NOT EXISTS stock_market;
USE stock_market;

-- 1. Sectors
CREATE TABLE sectors (
    sector_id   INT AUTO_INCREMENT PRIMARY KEY,
    sector_name VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Companies
CREATE TABLE companies (
    company_id     INT AUTO_INCREMENT PRIMARY KEY,
    ticker         VARCHAR(10)  NOT NULL UNIQUE,
    company_name   VARCHAR(200) NOT NULL,
    sector_id      INT NOT NULL,
    FOREIGN KEY (sector_id) REFERENCES sectors(sector_id)
);

-- 3. Trading Days
CREATE TABLE trading_days (
    trading_date DATE PRIMARY KEY
);

-- 4. Stock Prices (core fact table — 50,000+ records)
CREATE TABLE stock_prices (
    price_id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    company_id     INT  NOT NULL,
    trading_date   DATE NOT NULL,
    open_price     DECIMAL(12, 4) NOT NULL,
    close_price    DECIMAL(12, 4) NOT NULL,
    high_price     DECIMAL(12, 4) NOT NULL,
    low_price      DECIMAL(12, 4) NOT NULL,
    volume         BIGINT NOT NULL,
    FOREIGN KEY (company_id)   REFERENCES companies(company_id),
    FOREIGN KEY (trading_date) REFERENCES trading_days(trading_date),
    UNIQUE KEY uq_company_date (company_id, trading_date)
);

-- 5. Dividends
CREATE TABLE dividends (
    dividend_id    INT AUTO_INCREMENT PRIMARY KEY,
    company_id     INT NOT NULL,
    ex_date        DATE NOT NULL,
    amount         DECIMAL(10, 4) NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- 6. Analyst Ratings
CREATE TABLE analyst_ratings (
    rating_id      INT AUTO_INCREMENT PRIMARY KEY,
    company_id     INT NOT NULL,
    rating_date    DATE NOT NULL,
    analyst_firm   VARCHAR(100),
    rating         ENUM('STRONG_BUY','BUY','HOLD','SELL','STRONG_SELL') NOT NULL,
    price_target   DECIMAL(12, 4),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
