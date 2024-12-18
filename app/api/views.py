import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework import status
from .serializers import StockPriceSerializer, BacktestSerializer, PredictionSerializer
from app.core.models import StockPrice, StockPrediction, StockReport
from app.core.services import fetch_stock_data, backtest_strategy, predict_stock_prices
from app.core.utils import fetch_stock_data_from_api, fetch_stock_prediction_from_api, fetch_backtest_data_from_api
from app.reports.report_generator import generate_report
from django.core.cache import cache
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
                return Response({"error": "Invalid stock symbol."}, status=status.HTTP_400_BAD_REQUEST)
            
            cache_key = f"stock_prices_{symbol}"
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Retrieved cached data for: {symbol}")
                return Response(cached_data, status=status.HTTP_200_OK)

            stock_prices = StockPrice.objects.filter(symbol=symbol)
            if not stock_prices.exists():
                logger.info(f"No stock prices found for symbol: {symbol}")
                return Response({"error": "No stock prices found for this symbol."}, status=status.HTTP_404_NOT_FOUND)
        else:
            stock_prices = StockPrice.objects.all()

        serializer = StockPriceSerializer(stock_prices, many=True)
        cache.set(cache_key, serializer.data, timeout=60 * 60)
        logger.info(f"Retrieved {len(serializer.data)} stock prices (symbol: {symbol})")
        return Response(serializer.data, status=status.HTTP_200_OK)

class StockDataFetchView(APIView):
    """
    Fetch and store stock data for a specific symbol.

    POST /api/v1/stock-prices/fetch/<symbol>/ - Fetch and store stock data for a specific symbol.
    """

    def post(self, request, symbol):
        if not symbol.isalpha() or len(symbol) > 10:
            return Response({"error": "Invalid stock symbol."}, status=status.HTTP_400_BAD_REQUEST)
        
        existing_data = StockPrice.objects.filter(symbol=symbol).exists()
        if existing_data:
            logger.info(f"Stock data for symbol {symbol} already exists in the database.")
            return Response({"message": f"Stock data for {symbol} already exists."}, status=status.HTTP_200_OK)

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
        serializer = BacktestSerializer(data=request.data)
        if serializer.is_valid():
            symbol = serializer.validated_data['symbol']
            initial_investment = serializer.validated_data['initial_investment']
            logger.info(f"Starting backtest for symbol: {symbol}.")

            stock_data = StockPrice.objects.filter(symbol=symbol).order_by('timestamp')
            if not stock_data.exists():
                return Response({'error': 'Stock data not found'}, status=status.HTTP_404_NOT_FOUND)

            df = pd.DataFrame(list(stock_data.values('timestamp', 'close')))
            df.set_index('timestamp', inplace=True)

            results = backtest_strategy(df, initial_investment)

            logger.info(f"Backtest completed for symbol: {symbol}.")
            return Response(results, status=status.HTTP_200_OK)

        logger.error(f"Invalid data provided for backtesting: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StockPricePredictionView(APIView):
    """
    Predict future stock prices.

    POST /api/v1/prediction/<symbol>/ # Stock symbol to predict prices for

    Returns:
    {
        "predictions": [
            {"date": "YYYY-MM-DD", "predicted_price": float},
            ...
        ]
    }
    """

    def post(self, request, symbol):
        if not symbol or not symbol.isalpha() or len(symbol) > 10:
            return Response({"error": "Invalid stock symbol."}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f"prediction_{symbol}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Retrieved cached prediction for: {symbol}")
            return Response(cached_data, status=status.HTTP_200_OK)
        
        stock_data = StockPrice.objects.filter(symbol=symbol).order_by('timestamp')
        if not stock_data.exists():
            return Response({"error": "No historical data found for this symbol."}, status=status.HTTP_404_NOT_FOUND)

        df = pd.DataFrame(list(stock_data.values('timestamp', 'close')))
        df.set_index('timestamp', inplace=True)

        try:
            predictions = predict_stock_prices(df)
            logger.info(f"Predictions generated for symbol: {symbol}")
            
            for _, row in predictions.iterrows():
                prediction_date = row['date'].date()
                predicted_price = row['predicted_price']

                StockPrediction.objects.update_or_create(
                    symbol=symbol,
                    prediction_date=prediction_date,
                    defaults={
                        'predicted_price': predicted_price
                    }
                )

            logger.info(f"Predictions for {symbol} stored/updated in the database")
            latest_predictions = StockPrediction.objects.filter(symbol=symbol).order_by('prediction_date')
            prediction_serializer = PredictionSerializer(latest_predictions, many=True)
            cache.set(cache_key, prediction_serializer.data, timeout=60 * 60)
            return Response({"predictions": prediction_serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error occurred during prediction for {symbol}: {str(e)}")
            return Response({"error": "Prediction failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateStockReportView(APIView):
    """
    Generate a report for a stock symbol.

    POST /api/v1/report/

    Request Body:
    {
        "symbol": <symbol>,             # Stock Symbol
        "format": "json" or "pdf",       # Specifies the format of the report
        "initial_investment": 10000.00   # Initial investment amount
    }

    Returns:
    - JSON response with the report data if 'json' is selected.
    - PDF file if 'pdf' is selected.
    """

    def post(self, request):
        symbol = request.data.get("symbol")
        report_format = request.data.get('format', 'json').lower()
        initial_investment = request.data.get("initial_investment", 10000)

        if not symbol.isalpha() or len(symbol) > 10:
            logger.warning(f"Invalid stock symbol: {symbol}")
            return Response({"error": "Invalid stock symbol."}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f'report_{symbol}_{initial_investment}_{report_format}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            if report_format == 'pdf':
                logger.info(f"PDF report fetched from cache for symbol: {symbol}")
                return FileResponse(cached_data, as_attachment=True, filename=f"{symbol}_report.pdf")
            logger.info(f"json report fetched from cache for symbol: {symbol}")
            return Response(cached_data, status=status.HTTP_200_OK)

        try:
            stock_data = fetch_stock_data_from_api(symbol)
            stock_prediction = fetch_stock_prediction_from_api(symbol)
            backtest_data = fetch_backtest_data_from_api(symbol, initial_investment)

            if not stock_data or not stock_prediction:
                logger.warning(f"Missing data for symbol: {symbol}")
                return Response({"error": "Stock data or predictions not found."}, status=status.HTTP_404_NOT_FOUND)
            
            report_data, html_report, pdf_output = generate_report(
                symbol=symbol,
                historical_data=stock_data,
                predictions=stock_prediction,
                backtest_data=backtest_data
            )

            report, created = StockReport.objects.update_or_create(
                symbol=symbol,
                defaults={'report_data': report_data}
            )
            logger.info(f"Report for {symbol} {'created' if created else 'updated'} in the database")

            cache.set(cache_key, report_data if report_format == 'json' else pdf_output, timeout=60 * 60)
            
            if report_format == 'pdf':
                logger.info(f"PDF report generated for symbol: {symbol}")
                return FileResponse(pdf_output, as_attachment=True, filename=f"{symbol}_report.pdf")

            logger.info(f"JSON report generated for symbol: {symbol}")
            return Response(report_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error generating report for {symbol}: {str(e)}")
            return Response({"error": "Failed to generate report."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    