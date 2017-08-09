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
BASE = 'https://bittrex.com/api/{version}/{group}/{request_type}'

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












