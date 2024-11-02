import pandas as pd
import numpy as np
import talib
import yfinance as yf
import streamlit as st

# Load stock data
def get_stock_data(ticker, period='1mo', interval='1d'):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty:
            raise ValueError("No data found for the given ticker.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None
    return data

# Define indicators
def add_indicators(data):
    if data is None:
        return None

    # Moving Averages
    data['EMA_9'] = talib.EMA(data['Close'], timeperiod=9)
    data['EMA_50'] = talib.EMA(data['Close'], timeperiod=50)

    # Relative Strength Index (RSI)
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)

    # Bollinger Bands
    data['Upper_Band'], data['Middle_Band'], data['Lower_Band'] = talib.BBANDS(data['Close'], timeperiod=20)

    # MACD
    data['MACD'], data['Signal_Line'], _ = talib.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

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

# Main function for Streamlit
def main():
    st.title("Stock Buy/Hold/Sell Signal Analyzer")

    # Input for stock ticker
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL):", "AAPL")

    if st.button("Analyze"):
        data = get_stock_data(ticker)
        data = add_indicators(data)
        data = generate_signals(data)

        if data is not None:
            st.write("### Stock Price with Indicators and Signals")
            st.write(data[['Close', 'EMA_9', 'EMA_50', 'RSI', 'Upper_Band', 'Lower_Band', 'MACD', 'Signal_Line', 'Signal']].tail())

            # Display line charts for the data
            st.line_chart(data[['Close', 'EMA_9', 'EMA_50']])
            st.line_chart(data[['RSI']])
            st.line_chart(data[['MACD', 'Signal_Line']])

if __name__ == "__main__":
    main()
