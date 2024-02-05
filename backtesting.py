import talib
import numpy
import pandas as pd

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MA_PERIOD = 20  # Hareketli Ortalama periyodu
STOCHASTIC_K_PERIOD = 14  #    K periyodu
STOCHASTIC_D_PERIOD = 3   # Stokastik Osilatör D periyodu

closes = []
highs = []
lows = []
indexLine = 0
in_position = False
budget = 1000
coin_amount = 0

df = pd.read_csv('../tradebotProject/BTC-2021min.csv')
print(len(df))

for x in range(1, len(df) - 1, 15):
    indexLine += 1
    csv_line = df[x:x+1]
    closeVal = float(csv_line['close'])
    highVal = float(csv_line['high'])
    lowVal = float(csv_line['low'])
    closes.append(closeVal)
    highs.append(highVal)
    lows.append(lowVal)

    if indexLine > RSI_PERIOD:
        np_closes = numpy.array(closes)
        np_highs = numpy.array(highs)
        np_lows = numpy.array(lows)

        rsi = talib.RSI(np_closes, RSI_PERIOD)
        ma = talib.SMA(np_closes, timeperiod=MA_PERIOD)[-1]  # Hareketli Ortalama hesapla
        stoch_k, stoch_d = talib.STOCH(np_highs, np_lows, np_closes, fastk_period=STOCHASTIC_K_PERIOD,
                                       slowk_period=STOCHASTIC_D_PERIOD, slowd_period=STOCHASTIC_D_PERIOD)

        last_rsi = rsi[-1]

        if last_rsi < RSI_OVERSOLD and closeVal < ma and any(stoch_k < 20) and any(stoch_d < 20):
            if in_position:
                continue
            else:
                print("Oversold and below MA! BUY!", closeVal)
                budget = budget - budget * 0.001
                coin_amount = budget / closeVal
                budget = 0
                in_position = True

        if last_rsi > RSI_OVERBOUGHT:
            if in_position:
                print("Overbought! SELL!", closeVal)
                coin_amount = coin_amount - coin_amount * 0.001
                budget = coin_amount * closeVal
                coin_amount = 0
                print("Budget = ", budget)
                print("-------------------------------------------------")
                in_position = False
