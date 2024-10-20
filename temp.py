import httpx
import asyncio
from datetime import datetime, timedelta

API_KEY = '03G7QFJRYZSBSDCS'

async def fetch_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={API_KEY}'
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to fetch data for {symbol}: {response.status_code}")
            return None

def filter_last_2_years(time_series):
    two_years_ago = datetime.now() - timedelta(days=2*365)
    filtered_data = {
        date: stats
        for date, stats in time_series.items()
        if datetime.strptime(date, '%Y-%m-%d') >= two_years_ago
    }
    return filtered_data

async def main():
    symbol = 'AAPL'
    stock_data = await fetch_stock_data(symbol)
    
    if stock_data is None:
        return
    
    time_series = stock_data.get('Time Series (Daily)', {})
    
    filtered_data = filter_last_2_years(time_series)

    for date, stats in filtered_data.items():
        print(f"Date: {date}")
        print(f"Open: {stats['1. open']}, Close: {stats['4. close']}")
        print(f"High: {stats['2. high']}, Low: {stats['3. low']}")
        print(f"Volume: {stats['5. volume']}")
        print('-' * 30)

if __name__ == "__main__":
    asyncio.run(main())
