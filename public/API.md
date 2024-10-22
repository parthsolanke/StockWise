# StockWise API Documentation

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Fetch All Stock Prices](#fetch-all-stock-prices)
  - [Fetch Stock Prices for a Specific Symbol](#fetch-stock-prices-for-a-specific-symbol)
  - [Fetch and Store Stock Prices](#fetch-and-store-stock-prices)
  - [Backtest Strategy](#backtest-strategy)
  - [Predict Stock Prices](#predict-stock-prices)
  - [Generate Report](#generate-report)
- [Example Workflows](#example-workflows)
- [Error Handling](#error-handling)

---

## Overview

The **StockWise API** provides services for:
- Fetching stock price data.
- Predicting stock prices using machine learning models.
- Backtesting stock trading strategies.
- Generating PDF reports.

---

## Base URL

All API requests should be made to the following base URL:

```
http://<Server-IP>:8000/api/v1/
```

## Endpoints

### 1. Fetch All Stock Prices

Fetch all stock prices stored in the database.

- **Endpoint**: `GET /api/v1/stock-prices/`
- **Description**: Returns all stock price records.
- **Response Format**: JSON

#### Example Request

```bash
GET http://<Server-IP>:8000/api/v1/stock-prices/
```

#### Example Response

```json
[
    {
        "symbol": "AAPL",
        "timestamp": "2024-01-20",
        "open": "145.00",
        "close": "148.50",
        "high": "150.00",
        "low": "144.00",
        "volume": "2000000"
    },
    {
        "symbol": "GOOG",
        "timestamp": "2024-01-20",
        "open": "2500.00",
        "close": "2550.50",
        "high": "2600.00",
        "low": "2450.00",
        "volume": "3000000"
    }
]
```

---

### 2. Fetch Stock Prices for a Specific Symbol

Fetch historical stock prices for a specific stock symbol.

- **Endpoint**: `GET /api/v1/stock-prices/{symbol}/`
- **Description**: Returns stock prices for a specific stock symbol (e.g., AAPL, GOOG).
- **Path Parameter**:
  - `symbol`: The stock ticker symbol (e.g., `AAPL` for Apple).
- **Response Format**: JSON

#### Example Request

```bash
GET http://<Server-IP>:8000/api/v1/stock-prices/AAPL/
```

#### Example Response

```json
[
    {
        "symbol": "AAPL",
        "timestamp": "2024-01-20",
        "open": "145.00",
        "close": "148.50",
        "high": "150.00",
        "low": "144.00",
        "volume": "2000000"
    },
    {
        "symbol": "AAPL",
        "timestamp": "2024-01-19",
        "open": "143.00",
        "close": "145.00",
        "high": "146.50",
        "low": "142.00",
        "volume": "1500000"
    }
]
```

---

### 3. Fetch and Store Stock Prices

Fetch stock prices from the Alpha Vantage API and store them in the database.

- **Endpoint**: `POST /api/v1/stock-prices/fetch/{symbol}/`
- **Description**: Fetches and stores historical data for the specified stock symbol.
- **Path Parameter**:
  - `symbol`: The stock ticker symbol (e.g., `AAPL` for Apple).
- **Response Format**: JSON
- **Note**: Ensure that you have configured your **Alpha Vantage API key** in the `.env` file.

#### Example Request

```bash
POST http://<Server-IP>:8000/api/v1/stock-prices/fetch/AAPL/
```

#### Example Response

```json
{
    "message": "Stock data for AAPL has been successfully fetched and stored."
}
```

---

### 4. Backtest Strategy

Backtest a stock trading strategy using moving averages for a given stock.

- **Endpoint**: `POST /api/v1/backtest/`
- **Description**: Backtests a trading strategy based on historical stock prices.
- **Request Body**:
  - `symbol`: The stock ticker symbol (e.g., `AAPL`).
  - `initial_investment`: The initial investment amount (e.g., `10000`).
- **Response Format**: JSON

#### Example Request

```bash
POST http://<Server-IP>:8000/api/v1/backtest/
Content-Type: application/json

{
    "symbol": "AAPL",
    "initial_investment": 10000
}
```

#### Example Response

```json
{
    "total_return_percentage": 15.5,
    "max_drawdown_percentage": 7.3,
    "number_of_trades": 12,
    "final_cash": 11550.0
}
```

---

### 5. Predict Stock Prices

Predict future stock prices for a specific stock symbol using a machine learning model.

- **Endpoint**: `POST /api/v1/prediction/{symbol}/`
- **Description**: Predicts stock prices for the next 30 days for the given symbol.
- **Path Parameter**:
  - `symbol`: The stock ticker symbol (e.g., `AAPL` for Apple).
- **Response Format**: JSON

#### Example Request

```bash
POST http://<Server-IP>:8000/api/v1/prediction/AAPL/
```

#### Example Response

```json
[
    {
        "predicted_price": 152.34,
        "date": "2024-02-01"
    },
    {
        "predicted_price": 153.20,
        "date": "2024-02-02"
    }
]
```

---

### 6. Generate Report

Generate a financial report comparing historical stock prices, predicted stock prices, and backtest results.

- **Endpoint**: `POST /api/v1/report/`
- **Description**: Generates a report in PDF format containing historical data, predictions, and backtest results for the given symbol.
- **Request Body**:
  - `symbol`: The stock ticker symbol (e.g., `AAPL`).
  - `format`: The format of the report (`pdf`).
  - `initial_investment`: The initial investment amount for backtesting.
- **Response Format**: JSON and PDF

#### Example Request

```bash
POST http://<Server-IP>:8000/api/v1/report/
Content-Type: application/json

{
    "symbol": "AAPL",
    "format": "pdf",
    "initial_investment": 10000
}
```

#### Example Response

```json
{
    "message": "Report generated successfully.",
    "report_url": "/reports/AAPL_report.pdf"
}
```

---

## Example Workflows

### 1. Fetch Stock Prices for a Symbol

1. **Request**: 
   - Send a `GET` request to `/api/v1/stock-prices/AAPL/`.
2. **Response**: 
   - Receive historical stock price data for `AAPL`.

### 2. Predict Stock Prices for a Symbol

1. **Request**: 
   - Send a `POST` request to `/api/v1/prediction/AAPL/`.
2. **Response**: 
   - Receive predicted stock prices for the next 30 days.

### 3. Generate a Report

1. **Request**: 
   - Send a `POST` request to `/api/v1/report/` with the symbol, format, and initial investment.
2. **Response**: 
   - Receive a PDF report URL.

---

## Error Handling

In case of errors, the API responds with standard HTTP status codes and error messages.

- `400 Bad Request`: If the request is malformed.
- `404 Not Found`: If the specified stock symbol is not found.
- `500 Internal Server Error`: For unexpected errors on the server side.

Example of an error response:

```json
{
    "error": "Stock symbol not found."
}
```