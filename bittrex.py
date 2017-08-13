import hashlib
import hmac
import time
import requests
from pprint import pprint
from uuid import uuid4
import datetime

try:
    from urllib import urlencode
    from urlparse import urljoin

except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin

import secrets

__version__ = 'v1.1'
__version2__ = 'v2.0'

BASE = 'https://bittrex.com/api/{version}/{group}/{request_type}'
BASE_2 = 'https://bittrex.com/api/{version}/{domain}/{group}/{method}'

# domain = ['pub', 'auth']
# group = ['currencies', 'markets', 'market', 'orders']

"""
{	'pub': ['currencies', 'currency', 'markets', 'market'],
	'auth': ['orders', 'market']
}

Endpoints:
https://socket.bittrex.com/signalr/ping[?_=timestamp (int)]
https://bittrex.com/Content/version.txt
https://bittrex.com/Api/v2.0/pub/currencies/GetBTCPrice
https://bittrex.com/api/v2.0/pub/Markets/GetMarketSummaries[?_=timestamp (int)]
https://bittrex.com/Api/v2.0/pub/market/GetMarketSummary?marketName=BTC-ETH[?_=timestamp (int)]

https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=BTC-CVC&tickInterval=thirtyMin[?_=timestamp (int)]
	Options: ["oneMin", "fiveMin", "thirtyMin", "hour", "day"]

https://bittrex.com/Api/v2.0/pub/market/GetLatestTick?marketName=BTC-CVC&tickInterval=thirtyMin[?_=timestamp (int)]
	Options: ["oneMin", "fiveMin", "thirtyMin", "hour", "day"]

https://bittrex.com/Api/v2.0/auth/orders/GetOrderHistory with data { __RequestVerificationToken:"HIDDEN_FOR_PRIVACY" }
https://bittrex.com/api/v2.0/auth/market/TradeBuy with data { MarketName: "BTC-DGB, OrderType:"LIMIT", Quantity: 10000.02, Rate: 0.0000004, TimeInEffect:"GOOD_TIL_CANCELED", ConditionType: "NONE", Target: 0, __RequestVerificationToken: "HIDDEN_FOR_PRIVACY"}
https://bittrex.com/api/v2.0/auth/market/TradeSell with data { MarketName: "BTC-DGB, OrderType:"LIMIT", Quantity: 10000.02, Rate: 0.0000004, TimeInEffect:"GOOD_TIL_CANCELED", ConditionType: "NONE", Target: 0, __RequestVerificationToken: "HIDDEN_FOR_PRIVACY"}
https://bittrex.com/api/v2.0/auth/market/TradeCancel with data { MarketName: "BTC-DGB", orderId:"HIDDEN_FOR_PRIVACY", `__RequestVerificationToken:"HIDDEN_FOR_PRIVACY"}
https://bittrex.com/api/v2.0/pub/Currency/GetCurrencyInfo with data : { currencyName: "CVC", __RequestVerificationToken: "HIDDEN_FOR_PRIVACY"}

"""



ACCOUNT = [	'getbalance',
			'getbalances',
			'getdepositaddress',
			'getorder',
			'getorderhistory',
			'withdraw',
			'getwithdrawalhistory',
			'getdeposithistory']

MARKET = [	'buylimit',
			'buymarket',
			'cancel',
			'getopenorders',
			'selllimit',
			'sellmarket']

PARAMETERS = {	'getopenorders': None,
				'cancel': None,
				'sellmarket': None,
				'selllimit': None,
				'buymarket': None,
				'buylimit': None,
				'getbalances': None,
				'getbalance': None,
				'getdepositaddress': None,
				'withdraw': None,
				'getorderhistory': None,
				'getmarkets': None
			}

class RequestError(Exception):
	def __init__(self, error_code, url):
		super(RequestError, self).__init__('Bittrex server responded with returncode %d. Url: %s' % (error_code, url))
		self.url = url

class ResponseError(Exception):
	def __init__(self, url, message):
		super(ResponseError, self).__init__('Unsuccesful request: %s. Url: %s' % (message, url))
		self.message = message
		self.url = url


class Bittrex(object):

	def __init__(self, key=None, secret=None):
		self.key = key or ''
		self.secret = secret or ''

		if not (isinstance(self.key, str) and isinstance(self.secret, str)):
			raise TypeError('key and secret is should be a string. '
				'Recieved %s, %s instead' % (type(key), type(secret)))

	def get(self, request_type, **kwargs):
		parameters = self.check_parameters(kwargs, request_type)

		if request_type in ACCOUNT:
			group = 'account'
		elif request_type in MARKET:
			group = 'market'
		else:
			group = 'public'

		if group != 'public' and not (self.key and self.secret):
			raise Exception('To do a {} request, you have to set a key and secret.'.format(group))

		if group in ['account', 'market']:
			auth = 'apikey={}&nonce={}'.format(self.key, str(uuid4()))

			parameters = auth + parameters

		if parameters:
			parameters = '?' + parameters

		url = BASE.format(	version=__version__,
							request_type=request_type,
							group=group) + parameters

		print('GET %s' % url)

		r = requests.get(url,
			headers={"apisign": hmac.new(self.secret.encode(),
									url.encode(),
									hashlib.sha512).hexdigest()})

		if not r.status_code == 200:
			raise RequestError(r.status_code, url)

		data = r.json()
		if not data['success']:
			raise ResponseError(url, data['message'])

		return data['result']

	def get2(self, domain, group, method, **kwargs):
		parameters = self.check_parameters(kwargs, group)

		if parameters:
			parameters = '?' + parameters

		url = BASE_2.format(version=__version2__,
							domain=domain,
							group=group,
							method=method) + parameters

		print('GET %s' % url)

		r = requests.get(url,
			headers={"apisign": hmac.new(self.secret.encode(),
									url.encode(),
									hashlib.sha512).hexdigest()})

		if not r.status_code == 200:
			raise RequestError(r.status_code, url)

		data = r.json()
		if not data['success']:
			raise ResponseError(url, data['message'])

		return data['result']


	def check_parameters(self, parameters, request_type):
		"""Verify the parameters, raise error if incorrect"""
		return urlencode(parameters)

	def markets(self):
		return self.get('getmarkets')

	def currencies(self):
		return self.get('getcurrencies')

	def ticker(self, market):
		return self.get('getticker', market=market)

	def market_summaries(self):
		return self.get('getmarketsummaries')

	def market_summary(self, market):
		return self.get('getmarketsummary', market=market)

	def order_book(self, market, book_type, depth=20):
		return self.get('getorderbook', market=market, type=book_type, depth=depth)

	def market_history(self, market):
		return self.get('getmarkethistory', market=market)

	def buy_limit(self, market, quantity, rate):
		return self.get('buylimit', market=market, quantity=quantity, rate=rate)

	def sell_limit(self, market, quantity, rate):
		return self.get('selllimit', market=market, quantity=quantity, rate=rate)

	def cancel(self, uuid):
		return self.get('cancel', uuid=uuid)

	def open_orders(self, market=None):
		if market is not None:
			return self.get('getopenorders', market=market)
		else:
			return self.get('getopenorders')

	def balances(self):
		return self.get('getbalances')

	def deposit_address(self, currency):
		return self.get('getdepositaddress', currency=currency)

	def withdraw(self, currency, quantity, address, paymentid=None):
		args = {'currency': currency,
				'quantity': quantity,
				'address': address}

		if paymentid is not None:
			args['paymentid'] = paymentid

		return self.get('withdraw', **args)

	def order(self, uuid):
		return self.get('getorder', uuid=uuid)

	def order_history(self, market=None):
		if market is not None:
			return self.get('getorderhistory', market=market)
		else:
			return self.get('getorderhistory')

	def withdrawl_history(self, currency=None):
		if currency is not None:
			return self.get('getwithdrawalhistory', currency=currency)
		else:
			return self.get('getwithdrawalhistory')

	def deposit_history(self, currency=None):
		if currency is not None:
			return self.get('getdeposithistory', currency=currency)
		else:
			return self.get('getdeposithistory')

	def timestamp_to_datetime(self, timestamp):
		return datetime.datetime.strptime(timestamp.split('.')[0], '%Y-%m-%dT%H:%M:%S')

	def GetBTCPrice(self):
		return self.get2('pub', 'currencies', 'GetBTCPrice')

	def GetTicks(self, marketName, tickInterval, timeStamp=None, convertDatetime=False):
		# 	Options: ["oneMin", "fiveMin", "thirtyMin", "hour", "day"]

		translation = {	'BV': 'BaseVolume',
						'C': 'Close',
						'H': 'High',
						'L': 'Low',
						'O': 'Open',
						'T': 'TimeStamp',
						'V': 'Volume'}

		if timeStamp is None:
			timeStamp = int(time.time() * 1000)

		data = self.get2('pub', 'market', 'GetTicks',
						marketName=marketName, tickInterval=tickInterval, _=str(timeStamp))

		for d in data:
			if convertDatetime:
				d['T'] = self.timestamp_to_datetime(d['T'])
			for k, v in translation.items():
				d[v] = d.pop(k)


		return data


if __name__ == '__main__':
	b = Bittrex()
	pprint(b.GetTicks('BTC-NEO', 'day'))

			# "MarketName" : "BTC-888",
			# "High" : 0.00000919,
			# "Low" : 0.00000820,
			# "Volume" : 74339.61396015,
			# "Last" : 0.00000820,
			# "BaseVolume" : 0.64966963,
			# "TimeStamp" : "2014-07-09T07:19:30.15",
			# "Bid" : 0.00000820,
			# "Ask" : 0.00000831,
			# "OpenBuyOrders" : 15,
			# "OpenSellOrders" : 15,
			# "PrevDay" : 0.00000821,
			# "Created" : "2014-03-20T06:00:00",
			# "DisplayMarketName" : null





