import joblib
import requests
import logging
from django.conf import settings
from .models import StockPrice, StockPrediction
from app.api.serializers import StockPriceSerializer, PredictionSerializer

logger = logging.getLogger(__name__)

def fetch_from_api(endpoint, data=None, method="GET"):
    url = f"{settings.API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from {url}: {str(e)}")
        raise Exception(f"API request failed: {str(e)}")

def fetch_stock_data_from_api(symbol):
    stock_data = StockPrice.objects.filter(symbol=symbol).order_by('timestamp')
    if stock_data.exists():
        logger.info(f"Stock data found in the database for symbol: {symbol}")
        stock_data_serialized = StockPriceSerializer(stock_data, many=True)
        return stock_data_serialized.data
    
    logger.info(f"Fetching stock data via API for symbol: {symbol}")
    endpoint = f"/stock-prices/fetch/{symbol}/"
    response_data = fetch_from_api(endpoint, method="POST")

    stock_data = StockPrice.objects.filter(symbol=symbol).order_by('timestamp')
    if stock_data.exists():
        stock_data_serialized = StockPriceSerializer(stock_data, many=True)
        return stock_data_serialized.data
    else:
        logger.error(f"Failed to fetch stock data for {symbol}")
        raise Exception(f"Failed to fetch stock data for {symbol}")
    
def fetch_stock_prediction_from_api(symbol):
    stock_prediction = StockPrediction.objects.filter(symbol=symbol).order_by('prediction_date')
    if stock_prediction.exists():
        logger.info(f"Stock prediction found in the database for symbol: {symbol}")
        stock_prediction_serialized = PredictionSerializer(stock_prediction, many=True)
        return stock_prediction_serialized.data

    logger.info(f"Fetching stock predictions via API for symbol: {symbol}")
    endpoint = f"/prediction/{symbol}/"
    response_data = fetch_from_api(endpoint, method="POST")

    stock_prediction = StockPrediction.objects.filter(symbol=symbol).order_by('prediction_date')
    if stock_prediction.exists():
        stock_prediction_serialized = PredictionSerializer(stock_prediction, many=True)
        return stock_prediction_serialized.data
    else:
        logger.error(f"Failed to fetch predictions for {symbol}")
        raise Exception(f"Failed to fetch predictions for {symbol}")
    
def fetch_backtest_data_from_api(symbol, initial_investment):
    endpoint = "/backtest/"
    data = {'symbol': symbol, 'initial_investment': initial_investment}
    return fetch_from_api(endpoint, data, method="POST")

def load_model(model_path):
    """Load the pre-trained machine learning model."""
    return joblib.load(model_path)
