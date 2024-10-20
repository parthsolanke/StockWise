import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import StockPriceSerializer, BacktestSerializer
from app.core.models import StockPrice
from app.core.services import fetch_stock_data, backtest_strategy
import pandas as pd

logger = logging.getLogger(__name__)

class StockPriceListView(APIView):
    """
    Retrieve stock prices.

    GET /api/v1/stock-prices/ - Retrieve all stock prices.
    GET /api/v1/stock-prices/<symbol>/ - Retrieve stock prices for a specific symbol.
    """

    def get(self, request, symbol=None):
        if symbol:
            if not symbol.isalpha() or len(symbol) > 10:
                logger.warning(f"Invalid stock symbol: {symbol}")
                return Response({"error": "Invalid stock symbol."}, status=status.HTTP_400_BAD_REQUEST)

            stock_prices = StockPrice.objects.filter(symbol=symbol)
            if not stock_prices.exists():
                logger.info(f"No stock prices found for symbol: {symbol}")
                return Response({"error": "No stock prices found for this symbol."}, status=status.HTTP_404_NOT_FOUND)
        else:
            stock_prices = StockPrice.objects.all()

        serializer = StockPriceSerializer(stock_prices, many=True)
        logger.info(f"Retrieved {len(serializer.data)} stock prices (symbol: {symbol})")
        return Response(serializer.data, status=status.HTTP_200_OK)

class StockDataFetchView(APIView):
    """
    Fetch and store stock data for a specific symbol.

    POST /api/v1/stock-prices/fetch/<symbol>/ - Fetch and store stock data for a specific symbol.
    """

    def post(self, request, symbol):
        if not symbol.isalpha() or len(symbol) > 10:
            logger.warning(f"Invalid stock symbol for fetching data: {symbol}")
            return Response({"error": "Invalid stock symbol."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            fetch_stock_data(symbol)
            logger.info(f"Successfully fetched and stored stock data for symbol: {symbol}")
            return Response({"message": f"Stock data for {symbol} has been fetched and stored."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return Response({"error": "Failed to fetch stock data."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BacktestView(APIView):
    """
    Backtesting Strategy Endpoint.

    POST /api/v1/backtest/ - Run a backtest on historical stock prices.
    
    Request Body:
    {
        "symbol": "AAPL",              # Stock symbol to backtest
        "initial_investment": 10000.00  # Initial investment amount
    }

    Returns:
    {
        "total_return": float,          # Total return on investment
        "max_drawdown": float,          # Maximum drawdown during the backtest
        "number_of_trades": int,        # Number of trades executed
        "final_cash": float             # Final cash value after trades
    }
    """

    def post(self, request):
        print(request.data)
        serializer = BacktestSerializer(data=request.data)
        if serializer.is_valid():
            symbol = serializer.validated_data['symbol']
            initial_investment = serializer.validated_data['initial_investment']
            logger.info(f"Starting backtest for symbol: {symbol} with initial investment: {initial_investment}")

            stock_data = StockPrice.objects.filter(symbol=symbol).order_by('timestamp')
            if not stock_data.exists():
                logger.warning(f"No stock data found for symbol: {symbol}")
                return Response({'error': 'Stock data not found'}, status=status.HTTP_404_NOT_FOUND)

            df = pd.DataFrame(list(stock_data.values('timestamp', 'close')))
            df.set_index('timestamp', inplace=True)

            results = backtest_strategy(df, initial_investment)

            logger.info(f"Backtest completed for symbol: {symbol}. Results: {results}")
            return Response(results, status=status.HTTP_200_OK)

        logger.error(f"Invalid data provided for backtesting: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
