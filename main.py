import requests
from pyti.stochrsi import stochrsi
import operator
import datetime
import time
from client import Client

interval = "30m"
limit = "30"
altAraay = ["POWRBTC", "LENDBTC", "ICXBTC", "SCBTC", "LSKBTC", "WPRBTC", "FUNBTC", "NEOBTC","AIONBTC","XRPBTC","MCOBTC","BATBTC","ZILBTC","XEMBTC","FUELBTC"]
coinsInOrder = []
profitIndex = 1.0125
orderSum = 0
apikey = "hBxWrXHB0mgWtYpkAhrkvZmjvbYlQyqBpLfjsk6v2l50dvsEbcWajfTY7TYcTdls"
secret = "LSRN4A08bUfAB3iQE9eVCCN6IGGupa0ntYol9OCPzyuegMis2tUqQyyQ2mGKpg5k"
client = Client(apikey, secret)

def main():
    global orderSum
    print("running")
    orderSum =  float(client.getBtcBalance()) / (3 - client.getOpenBuyOrderCount())
    print(orderSum)
    counter = 0
    while True:
        counter = counter + 1
        orderSum = float(client.getBtcBalance()) / (3 - client.getOpenBuyOrderCount())
        if counter%10 == 0:
            pl = open("priceLogs.txt", "w")
        else:
            pl = open("priceLogs.txt", "a")
        pl.write(f"{datetime.datetime.now()}------------------------------------\n")
        alts = determineLowest()
        for a in alts:
            pl.write(f"{a['name']} - {a['ema7']/a['lastClose']*100-100}\n")
            if (a['ema7']/a['lastClose']*100-100) >= 3 and a['rsiNow'] < 20:
                buySequence(a)
        pl.write("\n")
        pl.close()


def ema(period, close):
    multiplier = (2 / (period+1))
    emaArray = []
    for idx, val in enumerate(close):
        if idx != 0:
            emaArray.append((val*multiplier) + (emaArray[idx-1]*(1-multiplier)))
        else:
            emaArray.append(val)
    return emaArray[len(emaArray)-1]


def getCoinData(name, interval, limit):
    while True:
        try:
            rqst = requests.get(f'https://api.binance.com/api/v1/klines?symbol={name}&interval={interval}&limit={limit}')
            break
        except requests.exceptions.RequestException as e:
            print('connection error')
    a = rqst.json()
    close = []

    for item in a:
        close.append(float(item[4]))

    rsi = stochrsi(close, 14)

    lastClose = close[len(close)-1]
    rsiNow = rsi[len(rsi)-1]
    ema7 = ema(7, close)
    ema25 = ema(25, close)
    return ema7, ema25, rsiNow, lastClose


def determineLowest():
    diffArray = []
    for i in altAraay:
        ema7, ema25, rsiNow, lastClose = getCoinData(i, interval, limit)
        dictionary = {
            "name": i,
            "value": ema25/lastClose*100-100,
            "rsiNow": rsiNow,
            "ema7": ema7,
            "ema25": ema25,
            "lastClose": lastClose
        }
        diffArray.append(dictionary)
    return diffArray


def buySequence(alt):
    if client.checkIfBuyIsPossible(orderSum, alt['name']):
        res = client.marketBuy(alt['name'], orderSum)
        sellSum = float(res['fills'][0]['price'])*profitIndex
        while not client.isSellPossible(alt['name'][:-3]):
            time.sleep(5)
        s = client.getSymbolLotSize(alt['name']).strip('0')
        count = len(s) - 1
        sellSum = format(float(sellSum), f'.{count}f')
        client.sellLimit(alt['name'], sellSum)


if __name__ == "__main__":
    main()
