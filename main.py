import talib
import numpy
import pandas as pd
from binance.client import Client
from binance.enums import *
import websocket
import json


API_KEY = "my binance key"  # key aldığında buraya yaz
API_SECRET = "my binance secret key"

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MA_PERIOD = 20  # Hareketli Ortalama periyodu
STOCHASTIC_K_PERIOD = 14  # Stokastik Osilatör K periyodu
STOCHASTIC_D_PERIOD = 3   # Stokastik Osilatör D periyodu

TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.01

closes = []
in_position = False



def binance_order(symbol, side, quantity, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending binance order")
        order = Client.create_order(symbol=symbol, side=side, quantity=quantity, type=order_type)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False


def check_sell_or_buy(last_rsi, macd, signal, hist, ma, stoch_k, stoch_d,closeVal):
    global in_position
    if last_rsi > RSI_OVERBOUGHT:
        if in_position:
            print("Overbought! SELL!")
            order_status = binance_order(TRADE_SYMBOL, SIDE_SELL, TRADE_QUANTITY)
            if order_status:
                in_position = False
        else:
            print("It is overbought but we don't have any")
    if last_rsi < RSI_OVERSOLD and closeVal < ma and stoch_k < 20 and stoch_d < 20:  # Stokastik Osilatör kontrolü
        if in_position:
            print("It is oversold but we already have it")
        else:
            if macd > signal and hist > 0:
                print("Oversold, MACD indicates bullish momentum, and below MA! BUY!")
                order_status = binance_order(TRADE_SYMBOL, SIDE_BUY, TRADE_QUANTITY)
                if order_status:
                    in_position = True
            else:
                print("Oversold but conditions not met, wait.")
                # You can add more conditions or indicators here


def on_open(ws):
    print("opened connection")


def on_close(ws):
    print("closed connection")


def on_message(ws, message):
    json_message = json.loads(message)
    candle = json_message['k']
    close = candle['c']
    is_candle_closed = candle['x']
    if is_candle_closed:
        print('candle closed at: ', close)
        closes.append(float(close))
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all RSI's calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi value is: ", last_rsi)

            macd, signal, hist = talib.MACD(np_closes, fastperiod=12, slowperiod=26, signalperiod=9)
            print("MACD: ", macd[-1], " Signal: ", signal[-1], " Histogram: ", hist[-1])

            ma = talib.SMA(np_closes, timeperiod=MA_PERIOD)[-1]  # Hareketli Ortalama hesapla
            print("MA: ", ma)

            stoch_k, stoch_d = talib.STOCH(np_closes, np_closes, np_closes, fastk_period=STOCHASTIC_K_PERIOD,
                                          slowk_period=STOCHASTIC_D_PERIOD, slowd_period=STOCHASTIC_D_PERIOD)
            print("Stoch K: ", stoch_k[-1], " Stoch D: ", stoch_d[-1])

            check_sell_or_buy(last_rsi, macd[-1], signal[-1], hist[-1], ma, stoch_k[-1], stoch_d[-1],closes[-1])


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
