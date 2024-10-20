from django.urls import path
from .views import StockPriceListView, StockDataFetchView

urlpatterns = [
    path('stock-prices/', StockPriceListView.as_view(), name='stock-prices'),
    path('stock-prices/<str:symbol>/', StockPriceListView.as_view(), name='stock-prices-symbol'),
    path('stock-prices/fetch/<str:symbol>/', StockDataFetchView.as_view(), name='fetch-stock-prices'),
]
