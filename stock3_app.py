import pandas as pd
import numpy as np
import yfinance as yf

# Load stock data
def get_stock_data(ticker, period='1mo', interval='1d'):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty:
            raise ValueError("No data found for the given ticker.")
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    return data

# Define indicators
def add_indicators(data):
    if data is None:
        return None

    # Moving Averages
    data['EMA_9'] = data['Close'].ewm(span=9, adjust=False).mean()
    data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()

    # Relative Strength Index (RSI)
    delta = data['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    data['Middle_Band'] = data['Close'].rolling(window=20).mean()
    data['Upper_Band'] = data['Middle_Band'] + (data['Close'].rolling(window=20).std() * 2)
    data['Lower_Band'] = data['Middle_Band'] - (data['Close'].rolling(window=20).std() * 2)

    # MACD
    exp12 = data['Close'].ewm(span=12, adjust=False).mean()
    exp26 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp12 - exp26
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

    return data

# Define trading strategy
def generate_signals(data):
    if data is None:
        return None

    def determine_final_signal(ma_signal, rsi_signal, bb_signal, macd_signal):
        signals = [ma_signal, rsi_signal, bb_signal, macd_signal]
        if signals.count('buy') > signals.count('sell'):
            return 'buy'
        elif signals.count('sell') > signals.count('buy'):
            return 'sell'
        else:
            return 'hold'

    def calculate_signals(row):
        # Moving Average Crossovers
        if row['EMA_9'] > row['EMA_50']:
            ma_signal = 'buy'
        elif row['EMA_9'] < row['EMA_50']:
            ma_signal = 'sell'
        else:
            ma_signal = 'hold'

        # RSI
        if row['RSI'] < 30:
            rsi_signal = 'buy'
        elif row['RSI'] > 70:
            rsi_signal = 'sell'
        else:
            rsi_signal = 'hold'

        # Bollinger Bands
        if row['Close'] < row['Lower_Band']:
            bb_signal = 'buy'
        elif row['Close'] > row['Upper_Band']:
            bb_signal = 'sell'
        else:
            bb_signal = 'hold'

        # MACD
        if row['MACD'] > row['Signal_Line']:
            macd_signal = 'buy'
        elif row['MACD'] < row['Signal_Line']:
            macd_signal = 'sell'
        else:
            macd_signal = 'hold'

        return determine_final_signal(ma_signal, rsi_signal, bb_signal, macd_signal)

    data['Signal'] = data.apply(calculate_signals, axis=1)
    return data

# Main function
def main():
    ticker = 'AAPL'  # Example stock ticker
    data = get_stock_data(ticker)
    data = add_indicators(data)
    data = generate_signals(data)

    if data is not None:
        # Display the last few rows with signals
        print(data[['Close', 'EMA_9', 'EMA_50', 'RSI', 'Upper_Band', 'Lower_Band', 'MACD', 'Signal_Line', 'Signal']].tail())

if __name__ == "__main__":
    main()