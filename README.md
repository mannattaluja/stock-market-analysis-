# Stock Market Analysis

A full-stack stock market analytics project combining a **3NF-normalized MySQL database** (50,000+ records) with a **Python matplotlib dashboard** showing Price, Volume, RSI, and MACD.

## Features

- **Database**: 6-table 3NF schema across Sectors, Companies, Trading Days, Stock Prices, Dividends, and Analyst Ratings
- **Advanced SQL**: Window functions (`LAG`, `FIRST_VALUE`, `RANK`), CTEs, `STDDEV`, and a stored procedure for date-range queries
- **Dashboard**: 4-panel dark-themed matplotlib chart
  - Panel 1: Closing Price + MA5 / MA20 / MA50
  - Panel 2: Volume (green/red by day direction)
  - Panel 3: RSI (14) with overbought/oversold zones
  - Panel 4: MACD (12, 26, 9) with histogram

## Project Structure

```
stock-market-analysis/
├── sql/
│   ├── 01_schema.sql        # 3NF schema creation
│   ├── 02_seed_data.sql     # Sample data (50,000+ records)
│   └── 03_queries.sql       # Window functions, CTEs, stored procedure
├── dashboard.py             # Python matplotlib dashboard
├── requirements.txt
└── README.md
```

## Setup

### 1. Database
```bash
mysql -u root -p < sql/01_schema.sql
mysql -u root -p < sql/02_seed_data.sql
```

### 2. Python
```bash
pip install -r requirements.txt
```

Update `DB_CONFIG` in `dashboard.py` with your MySQL credentials.

### 3. Run Dashboard
```bash
# With database
python dashboard.py --ticker AAPL --start 2024-01-01 --end 2024-12-31

# With generated sample data (no DB needed)
python dashboard.py --sample
```

## Requirements

- Python 3.9+
- MySQL 8.0
- See `requirements.txt`
