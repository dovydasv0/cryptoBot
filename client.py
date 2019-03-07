import requests, json, time, hashlib, hmac

class Client:
    def __init__(self, apiKey, secret):
        self.API_KEY = apiKey
        self.SECRET = secret

    def getTime(self):
        while True:
            try:
                res = requests.get('https://api.binance.com/api/v1/time')
                break
            except requests.exceptions.RequestException as e:
                err = open("errorLog.txt", "a")
                err.write(str(res.json()))
                err.close()
        return res.json()['serverTime']

    def getBtcBalance(self):
        timeStamp = self.getTime()
        params = f"timestamp={timeStamp}"
        h = hmac.new(self.SECRET.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()
        while True:
            try:
                res = requests.get(f'https://api.binance.com/api/v3/account?timestamp={timeStamp}&signature={h}', headers = {"X-MBX-APIKEY" : self.API_KEY })
                break
            except requests.exceptions.RequestException as e:
                err = open("errorLog.txt", "a")
                err.write(str(res.json()))
                err.close()
        return res.json()['balances'][0]['free']

    def marketBuy(self, coinName, balance):
        timestamp = self.getTime()
        paramLine = f"symbol={coinName}&side=BUY&type=MARKET&quantity={round(self.getAmountToBuy(coinName, balance),0)}&timestamp={timestamp}"
        h = hmac.new(self.SECRET.encode('utf-8'), paramLine.encode('utf-8'), hashlib.sha256).hexdigest()
        url = f'https://api.binance.com/api/v3/order/test?{paramLine}&signature={h}'
        while True:
            try:
                res = requests.post(url, headers = {"X-MBX-APIKEY" : self.API_KEY })
                break
            except requests.exceptions.RequestException as e:
                err = open("errorLog.txt", "a")
                err.write(str(res.json()))
                err.close()
        return res.json()

    def sellLimit(self, coinName, sellPrice):
        timestamp = self.getTime()
        paramLine = f"symbol={coinName}&side=SELL&type=LIMIT&timeInForce=GTC&quantity={round(float(self.getBalance(coinName[:-3])),0)}&price={sellPrice}&timestamp={timestamp}"
        h = hmac.new(self.SECRET.encode('utf-8'), paramLine.encode('utf-8'), hashlib.sha256).hexdigest()
        url = f'https://api.binance.com/api/v3/order/test?{paramLine}&signature={h}'
        while True:
            try:
                res = requests.post(url, headers = {"X-MBX-APIKEY" : self.API_KEY })
                sellLogs = open('sellLogs.txt','a')
                sellLogs.write(f"{url}\n{res.json()}\n\n")
                sellLogs.close()
                break
            except requests.exceptions.RequestException as e:
                err = open("errorLog.txt", "a")
                err.write(str(res.json()))
                err.close()
        return res.json()


    def getAmountToBuy(self, coinName, balance):
        while True:
            try:
                res = requests.get(f'https://api.binance.com/api/v1/klines?symbol={coinName}&interval=1m&limit=1')
                break
            except requests.exceptions.RequestException as e:
                err = open("errorLog.txt", "a")
                err.write(str(res.json()))
                err.close()
        return balance/float(res.json()[0][4])

    def getBalance(self, coinName):
        timeStamp = self.getTime()
        params = f"timestamp={timeStamp}"
        h = hmac.new(self.SECRET.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()
        while True:
            try:
                res = requests.get(f'https://api.binance.com/api/v3/account?timestamp={timeStamp}&signature={h}', headers = {"X-MBX-APIKEY" : self.API_KEY })
                break
            except requests.exceptions.RequestException as e:
                err = open("errorLog.txt", "a")
                err.write(str(res.json()))
                err.close()
        for b in res.json()['balances']:
            if b['asset'] == coinName:
                return b['free']

    def getOpenBuyOrderCount(self):
        timeStamp = self.getTime()
        params = f"timestamp={timeStamp}"
        h = hmac.new(self.SECRET.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()
        while True:
            try:
                res = requests.get(f'https://api.binance.com/api/v3/openOrders?timestamp={timeStamp}&signature={h}', headers = {"X-MBX-APIKEY" : self.API_KEY })
                break
            except requests.exceptions.RequestException as e:
                err = open("errorLog.txt", "a")
                err.write(str(res.json()))
                err.close()
        return len(res.json())

    def isCoinInBuyOrder(self, pair):
        timeStamp = self.getTime()
        params = f"symbol={pair}&timestamp={timeStamp}"
        h = hmac.new(self.SECRET.encode('utf-8'), params.encode('utf-8'), hashlib.sha256).hexdigest()
        while True:
            try:
                res = requests.get(f'https://api.binance.com/api/v3/openOrders?{params}&signature={h}', headers = {"X-MBX-APIKEY" : self.API_KEY })
                break
            except requests.exceptions.RequestException as e:
                err = open("errorLog.txt", "a")
                err.write(str(res.json()))
                err.close()
        for i in res.json():
            if i['side'] == 'SELL':
                return True
        return False

    def checkIfBuyIsPossible(self, expectedBalance, pair):
        if float(self.getBtcBalance()) >= expectedBalance and self.getOpenBuyOrderCount() < 3 and not self.isCoinInBuyOrder(pair):
            return True
        else:
            return False

    def isSellPossible(self, coin):
        if float(self.getBalance(coin)) > 0:
            return True
        else:
            return False

    def getSymbolLotSize(self, searchSymbol):
        res = requests.get(f'https://api.binance.com/api/v1/exchangeInfo')
        for symbol in res.json()["symbols"]:
            if symbol["symbol"] == searchSymbol:
                return(symbol["filters"][0]["tickSize"])

# apikey = "hBxWrXHB0mgWtYpkAhrkvZmjvbYlQyqBpLfjsk6v2l50dvsEbcWajfTY7TYcTdls"
# secret = "LSRN4A08bUfAB3iQE9eVCCN6IGGupa0ntYol9OCPzyuegMis2tUqQyyQ2mGKpg5k"
# client = Client(apikey, secret)
# buysum = 0.00004067
# sellSum = buysum*1.0125
# # s = str(buysum)
# # count = len(s) - s.index('.') - 1
# # sellSum = format(float(sellSum), f'.{count}f')
# # print(sellSum)
# s = client.getSymbolLotSize("BATBTC").strip('0')
# count = len(s) - 1
# sellSum = format(float(sellSum), f'.{count}f')
# print(sellSum)
# client.sellLimit("LENDBTC", sellSum)