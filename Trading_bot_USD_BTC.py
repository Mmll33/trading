import ccxt
import pandas as pd
import ta


exchange = ccxt.binance()
timeframes = ["5m", "15m", "30m", "1h", "4h", "1d", "1M"]

# Obtener datos históricos
def get_data(timeframe):
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe=timeframe, limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Calcular indicadores
def calculate_indicators(df):
    df['EMA9'] = ta.trend.ema_indicator(df['close'], window=9).round(0)
    df['EMA21'] = ta.trend.ema_indicator(df['close'], window=21).round(0)
    df["Cross"] = (df["EMA9"] - df["EMA21"]).round(0)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14).round(0)
    df['MACD'] = ta.trend.macd(df['close']).round(0)
    df['MACD_signal'] = ta.trend.macd_signal(df['close']).round(0)
    bollinger = ta.volatility.BollingerBands(df['close'])
    df['Bollinger_low'] = bollinger.bollinger_lband().round(0)
    df['Bollinger_high'] = bollinger.bollinger_hband().round(0)
    df["RVOL"] = df["volume"].rolling(20).mean().round(0) / df["volume"].rolling(50).mean().round(0)
    return df

# Generar señales de compra/venta
def generate_signals(df):
    last_row = df.iloc[-1]
    if (

        last_row['RSI'] < 30 and
        last_row['MACD'] > last_row['MACD_signal'] and
        last_row["EMA9"] > last_row["EMA21"] and
        last_row["Bollinger_low"] > last_row["close"] and
        last_row["RVOL"] > 1
    ):
        return 'STRONG BUY'
    elif (
        last_row['RSI'] > 52 and
        last_row['RSI'] < 60 and
        last_row['MACD'] > last_row['MACD_signal'] and
        last_row["EMA9"] > last_row["EMA21"] and
        0.7 < last_row["RVOL"] < 1.2 and
        last_row["Bollinger_low"] > last_row["close"]      
    ):
        return 'BUY'
    elif (
        40 < last_row['RSI'] < 52 and
        last_row['MACD'] < last_row['MACD_signal'] and
        last_row["EMA9"] < last_row["EMA21"] and
        last_row["Bollinger_high"] < last_row["close"] 
    ):
        return 'SELL'
    
    elif (
        last_row['RSI'] < 40 and
        last_row['MACD'] < last_row['MACD_signal'] and
        last_row["EMA9"] < last_row["EMA21"] and
        last_row["RVOL"] > 1.1
    ):
        return 'STRONG SELL'
          
    else:
        return 'HOLD'

# Nueva función que se puede ejecutar en Flask
def run_bot():
    results = {}
    for timeframe in timeframes:
        df = get_data(timeframe)
        df = calculate_indicators(df)
        signal = generate_signals(df)
        results[timeframe] = {
            "timeframe": timeframe,
            "signal": signal,
            "price": df['close'].iloc[-1],
            "Cross": df["Cross"].iloc[-1],
            "RSI": df["RSI"].iloc[-1],
            "MACD": df["MACD"].iloc[-1],
            "Bollinger_Low": df["Bollinger_low"].iloc[-1],
            "Bollinger_High": df["Bollinger_high"].iloc[-1],
            "RVOL": round(df["RVOL"].iloc[-1], 2)
        }
    return results

