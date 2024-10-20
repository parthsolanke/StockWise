import httpx
from datetime import datetime, timedelta
from django.conf import settings
from app.api.serializers import StockPriceSerializer
import logging

logger = logging.getLogger(__name__)

def fetch_stock_data(symbol):
    API_KEY = settings.ALPHA_VANTAGE_API_KEY
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}&outputsize=full'

    logger.info(f"Fetching stock data for symbol: {symbol}")
    
    with httpx.Client() as client:
        try:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            time_series = data.get('Time Series (Daily)', {})
            
            two_years_ago = datetime.now() - timedelta(days=2 * 365)
            for date, stats in time_series.items():
                if datetime.strptime(date, '%Y-%m-%d') >= two_years_ago:
                    stock_price_data = {
                        'symbol': symbol,
                        'timestamp': date,
                        'open': stats['1. open'],
                        'close': stats['4. close'],
                        'high': stats['2. high'],
                        'low': stats['3. low'],
                        'volume': stats['5. volume'],
                    }

                    serializer = StockPriceSerializer(data=stock_price_data)
                    if serializer.is_valid():
                        serializer.save()
                        logger.info(f"Stored stock data for {symbol} on {date}")
                    else:
                        logger.warning(f"Validation error for {symbol} on {date}: {serializer.errors}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error fetching data for {symbol}: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error fetching data for {symbol}: {str(e)}")
