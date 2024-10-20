import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import StockPriceSerializer
from app.core.models import StockPrice
from app.core.services import fetch_stock_data

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
