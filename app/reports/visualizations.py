import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64
import pandas as pd
import matplotlib.ticker as ticker
from matplotlib.ticker import ScalarFormatter

def generate_stock_price_history_chart(historical_data):
    plt.figure(figsize=(10, 6))
    
    dates = pd.to_datetime([data['timestamp'] for data in historical_data])
    prices = [data['close'] for data in historical_data]
    historical_df = pd.DataFrame({'date': dates, 'price': prices})
    historical_df['rolling_avg'] = historical_df['price'].rolling(window=30, min_periods=1).mean()
    
    plt.plot(historical_df['date'], historical_df['rolling_avg'], label='30-Day Rolling Avg', color='blue')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.gca().yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(nbins=8))
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.title('Historical Stock Prices (30-Day Rolling Average)', fontsize=14)
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')

    return get_image_as_base64()

def generate_prediction_vs_actual_chart(predictions, actual_prices):
    plt.figure(figsize=(10, 6))
    
    prediction_dates = pd.to_datetime([pred['prediction_date'] for pred in predictions])
    predicted_prices = [pred['predicted_price'] for pred in predictions]
    actual_dates = pd.to_datetime([actual['timestamp'] for actual in actual_prices])
    actuals = [actual['close'] for actual in actual_prices]
    actual_df = pd.DataFrame({'date': actual_dates, 'value': actuals})
    prediction_df = pd.DataFrame({'date': prediction_dates, 'value': predicted_prices})
    actual_df['rolling_avg'] = actual_df['value'].rolling(window=30, min_periods=1).mean()
    prediction_df['rolling_avg'] = prediction_df['value'].rolling(window=30, min_periods=1).mean()

    plt.plot(actual_df['date'], actual_df['rolling_avg'], label='Actual Prices (30-Day Avg)', color='blue')
    plt.plot(prediction_df['date'], prediction_df['rolling_avg'], label='Predicted Prices (30-Day Avg)', linestyle='--', color='orange')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.gca().yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(nbins=8))
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.title('Predicted vs Actual Stock Prices', fontsize=14)
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')

    return get_image_as_base64()

def get_image_as_base64():
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.clf()
    return base64.b64encode(image_png).decode('utf-8')
