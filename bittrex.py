import hashlib
import hmac
import time
import requests
from pprint import pprint
from uuid import uuid4

try:
    from urllib import urlencode
    from urlparse import urljoin

except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin

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







if __name__ == '__main__':
	b = Bittrex(key='', secret='')
	# pprint(b.markets())
	order_book = b.order_book('BTC-ANS', 'both')
	pprint(order_book)
	buyers = len(order_book['buy'])
	sellers = len(order_book['sell'])
	qnt_buy = sum([i['Quantity'] for i in order_book['buy']])
	qnt_sell = sum([i['Quantity'] for i in order_book['sell']])

	max_buy_price = max([i['Rate'] for i in order_book['buy']])
	min_sel_price = min([i['Rate'] for i in order_book['sell']])

	print 'Total buyers:  %d' % buyers
	print 'Total sellers: %d' % sellers
	print '%.02f%%' % ((float(buyers) / float(sellers)) * 100.0)
	print 'Total Volume Buy:  %.08f' % qnt_buy
	print 'Total Volume Sell: %.08f' % qnt_sell
	print '%.02f%%' % ((float(qnt_buy) / float(qnt_sell)) * 100.0)
	print 'Max buy:    %.08f' % max_buy_price
	print 'Min Sell:   %.08f' % min_sel_price
	print 'Difference: %.08f' % (min_sel_price - max_buy_price)


"""
#### PUBLIC ####
/public/getmarkets
Used to get the open and available trading markets at Bittrex along with other meta data.

Parameters
None


/public/getcurrencies
Used to get all supported currencies at Bittrex along with other meta data.

Parameters
None


/public/getticker
Used to get the current tick values for a market.

Parameters
parameter	required	description
market		required	a string literal for the market (ex: BTC-LTC)



/public/getmarketsummaries
Used to get the last 24 hour summary of all active exchanges

Parameters
None


/public/getmarketsummary
Used to get the last 24 hour summary of all active exchanges

Parameters
parameter	required	description
market		required	a string literal for the market (ex: BTC-LTC)


/public/getorderbook
Used to get retrieve the orderbook for a given market

Parameters
parameter	required	description
market		required	a string literal for the market (ex: BTC-LTC)
type		required	buy, sell or both to identify the type of orderbook to return.
depth		optional	defaults to 20 - how deep of an order book to retrieve. Max is 50


/public/getmarkethistory
Used to retrieve the latest trades that have occured for a specific market.

Parameters
parameter	required	description
market		required	a string literal for the market (ex: BTC-LTC)


#### MARKET ####
/market/buylimit
Used to place a buy order in a specific market. Use buylimit to place limit orders. Make sure you have the proper permissions set on your API keys for this call to work

Parameters
parameter	required	description
market		required	a string literal for the market (ex: BTC-LTC)
quantity	required	the amount to purchase
rate		required	the rate at which to place the order.


/market/selllimit
Used to place an sell order in a specific market. Use selllimit to place limit orders. Make sure you have the proper permissions set on your API keys for this call to work

Parameters
parameter	required	description
market		required	a string literal for the market (ex: BTC-LTC)
quantity	required	the amount to purchase
rate		required	the rate at which to place the order


/market/cancel
Used to cancel a buy or sell order.

Parameters
parameter	required	description
uuid		required	uuid of buy or sell order


/market/getopenorders
Get all orders that you currently have opened. A specific market can be requested

Parameters
parameter	required	description
market		optional	a string literal for the market (ie. BTC-LTC)


#### ACCOUNT ####
/account/getbalances
Used to retrieve all balances from your account

Parameters
None


/account/getbalance
Used to retrieve the balance from your account for a specific currency.

Parameters
parameter	required	description
currency	required	a string literal for the currency (ex: LTC)


/account/getdepositaddress
Used to retrieve or generate an address for a specific currency. If one does not exist, the call will fail and return ADDRESS_GENERATING until one is available.

Parameters
parameter	required	description
currency	required	a string literal for the currency (ie. BTC)


/account/withdraw
Used to withdraw funds from your account. note: please account for txfee.

Parameters
parameter	required	description
currency	required	a string literal for the currency (ie. BTC)
quantity	required	the quantity of coins to withdraw
address	required	the address where to send the funds.
paymentid	optional	used for CryptoNotes/BitShareX/Nxt optional field (memo/paymentid)


/account/getorder
Used to retrieve a single order by uuid.

Parameters
parameter	required	description
uuid	required	the uuid of the buy or sell order


/account/getorderhistory
Used to retrieve your order history.

Parameters
parameter	required	description
market	optional	a string literal for the market (ie. BTC-LTC). If ommited, will return for all markets


/account/getwithdrawalhistory
Used to retrieve your withdrawal history.

Parameters
parameter	required	description
currency	optional	a string literal for the currecy (ie. BTC). If omitted, will return for all currencies


/account/getdeposithistory
Used to retrieve your deposit history.

Parameters
parameter	required	description
currency	optional	a string literal for the currecy (ie. BTC). If omitted, will return for all currencies

"""






