import ccxt
import pandas as pd
import ta
import time
import ta.trend

# Configurar exchange (Binance en este caso)
exchange = ccxt.binance()

timeframes = ["5m", "15m", "30m", "1h", "4h", "1d","1M"]


# Obtener datos históricos de BTC/USD   
def get_data(timeframe):
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe=timeframe, limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Calcular indicadores
def calculate_indicators(df):
    df['EMA9'] = ta.trend.ema_indicator(df['close'], window=9).round(2)
    df['EMA21'] = ta.trend.ema_indicator(df['close'], window=21).round(2)
    df["Cross"] = (df["EMA9"] - df["EMA21"]).round(2)
    df['EMA100'] = ta.trend.ema_indicator(df['close'], window=150).round(2)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14).round(2)
    macd = ta.trend.macd(df['close'])
    df['MACD'] = macd.round(2)
    df['MACD_signal'] = ta.trend.macd_signal(df['close']).round(2)
    bollinger = ta.volatility.BollingerBands(df['close'])
    df['Bollinger_low'] = bollinger.bollinger_lband().round(2)
    df['Bollinger_high'] = bollinger.bollinger_hband().round(2)
    df["RVOL"] = df["volume"].rolling(20).mean().round(2)/df["volume"].rolling(50).mean().round(2)
    
    
    
    
    return df

# Generar señales de compra/venta
def generate_signals(df):
    last_row = df.iloc[-1]
    #Revisar las señales porque no son correctas, son cosas que nunca pasaran
    if (

        last_row['RSI'] < 30 and
        last_row['MACD'] > last_row['MACD_signal'] and
        last_row["EMA9"] > last_row["EMA21"] and
        last_row["Bollinger_low"] > last_row["close"] and
        last_row["RVOL"] > 1
    ):
        return 'BUY +'
    
    
    if (
        last_row['RSI'] > 52 and
        last_row['RSI'] < 60 and
        last_row['MACD'] > last_row['MACD_signal'] and
        last_row["EMA9"] > last_row["EMA21"] and
        0.7 < last_row["RVOL"] < 1.2 and
        last_row["Bollinger_low"] > last_row["close"]

        
    ):
        return 'BUY'
        
    
    if (
        40 < last_row['RSI'] < 52 and
        last_row['MACD'] < last_row['MACD_signal'] and
        last_row["EMA9"] < last_row["EMA21"] and
        last_row["Bollinger_high"] < last_row["close"] 
    ):
        return 'SELL'
    
    if (
        last_row['RSI'] < 40 and
        last_row['MACD'] < last_row['MACD_signal'] and
        last_row["EMA9"] < last_row["EMA21"] and
        last_row["RVOL"] > 1.1
    ):
        return 'SELL +'
          
    else:
        return 'HOLD'

# Loop para ejecutar en tiempo real
while True:
    results ={}
    
    for timeframe in timeframes:
        df = get_data(timeframe)
        df = calculate_indicators(df)
        signal = generate_signals(df)
        results[timeframe] = {
            "signal": signal,
            "price": df['close'].iloc[-1],
            "Cross": df["Cross"].iloc[-1],
            "RSI": df["RSI"].iloc[-1],
            "MACD": df["MACD"].iloc[-1],
            "Bollinger_Low": df["Bollinger_low"].iloc[-1],
            "Bollinger_High": df["Bollinger_high"].iloc[-1],
            "Tendencia": df["EMA150"].iloc[-1],
            "RVOL": round(df["RVOL"].iloc[-1],2)
        }
            

    #Imprimir resultados

    print("\n 🔹 Señales de Trading por Temporalidad 🔹")
    for tf, data in results.items():
        print(f"[{tf}] -> Señal: {data['signal']} | Precio: {data['price']} | Volume: {data['RVOL']} | Cross: {data['Cross']} | RSI: {data['RSI']} | MACD: {data['MACD']} | Bollinger Low: {data['Bollinger_Low']} | Bollinger High: {data['Bollinger_High']} | Tendencia: {data['Tendencia']}")  
    
    time.sleep(60)
