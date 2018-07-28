# coding=utf-8

import binascii
import codecs
import re
import requests
import time

from decimal import Decimal
from ethereum.utils import sha3, ecsign, encode_int32

class Client(object):

    API_URL = 'https://api.idex.market'

    _wallet_address = None
    _private_key = None
    _contract_address = None
    _currency_addresses = {}

    def __init__(self, address=None, private_key=None):
        """IDEX API Client constructor
        Takes an optional wallet address parameter which enables helper functions
        https://github.com/AuroraDAO/idex-api-docs
        :param address: optional - Wallet address
        :type address: address string
        :param private_key: optional - The private key for the address
        :type private_key: string
        .. code:: python
            client = Client()
            # with wallet address and private key
            address = '0x925cfc20de3fcbdba2d6e7c75dbb1d0a3f93b8a3'
            private_key = 'priv_key...'
            client = Client(address, private_key)
        """

        self._start_nonce = None
        self._client_started = int(time.time() * 1000)

        self.session = self._init_session()

        if address:
            self.set_wallet_address(address, private_key)

    def _init_session(self):

        session = requests.session()
        headers = {'Accept': 'application/json',
                   'User-Agent': 'python-idex'}
        session.headers.update(headers)
        return session

    def _get_nonce(self):
        """Get a unique nonce for request
        """
        return self._start_nonce + int(time.time() * 1000) - self._client_started

    def _generate_signature(self, data):
        """Generate v, r, s values from payload
        """

        # pack parameters based on type
        sig_str = b''
        for d in data:
            val = d[1]
            if d[2] == 'address':
                # remove 0x prefix and convert to bytes
                val = val[2:].encode('utf-8')
            elif d[2] == 'uint256':
                # encode, pad and convert to bytes
                val = binascii.b2a_hex(encode_int32(int(d[1])))
            sig_str += val

        # hash the packed string
        rawhash = sha3(codecs.decode(sig_str, 'hex_codec'))

        # salt the hashed packed string
        salted = sha3(u"\x19Ethereum Signed Message:\n32".encode('utf-8') + rawhash)

        # sign string
        v, r, s = ecsign(salted, codecs.decode(self._private_key[2:], 'hex_codec'))

        # pad r and s with 0 to 64 places
        return {'v': v, 'r': "{0:#0{1}x}".format(r, 66), 's': "{0:#0{1}x}".format(s, 66)}

    def _create_uri(self, path):
        return '{}/{}'.format(self.API_URL, path)

    def _request(self, method, path, signed, **kwargs):

        kwargs['json'] = kwargs.get('json', {})
        kwargs['headers'] = kwargs.get('headers', {})

        uri = self._create_uri(path)

        if signed:
            # generate signature e.g. {'v': 28 (or 27), 'r': '0x...', 's': '0x...'}
            kwargs['json'].update(self._generate_signature(kwargs['hash_data']))

            # put hash_data into json param
            for name, value, _param_type in kwargs['hash_data']:
                kwargs['json'][name] = value

            # filter out contract address, not required
            if 'contract_address' in kwargs['json']:
                del(kwargs['json']['contract_address'])

            # remove the passed hash data
            del(kwargs['hash_data'])

        response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(response)

    def _handle_response(self, response):
        """Internal helper for handling API responses from the Quoine server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not str(response.status_code).startswith('2'):
            raise IdexAPIException(response)
        try:
            res = response.json()
            if 'error' in res:
                raise IdexAPIException(response)
            return res
        except ValueError:
            raise IdexRequestException('Invalid Response: %s' % response.text)

    def _get(self, path, signed=False, **kwargs):
        return self._request('get', path, signed, **kwargs)

    def _post(self, path, signed=False, **kwargs):
        return self._request('post', path, signed, **kwargs)

    def _put(self, path, signed=False, **kwargs):
        return self._request('put', path, signed, **kwargs)

    def _delete(self, path, signed=False, **kwargs):
        return self._request('delete', path, signed, **kwargs)

    def set_wallet_address(self, address, private_key=None):
        """Set the wallet address. Optionally add the private_key, this is only required for trading.
        :param address: Address of the wallet to use
        :type address: address string
        :param private_key: optional - The private key for the address
        :type private_key: string
        .. code:: python
            client.set_wallet_address('0x925cfc20de3fcbdba2d6e7c75dbb1d0a3f93b8a3', 'priv_key...')
        :returns: nothing
        """
        self._wallet_address = address.lower()
        nonce_res = self.get_my_next_nonce()
        self._start_nonce = nonce_res['nonce']
        if private_key:
            if re.match(r"^0x[0-9a-zA-Z]{64}$", private_key) is None:
                raise(IdexException("Private key in invalid format must satisfy 0x[0-9a-zA-Z]{64}"))
            self._private_key = private_key

    def get_wallet_address(self):
        """Get the wallet address
        .. code:: python
            address = client.get_wallet_address()
        :returns: address string
        """
        return self._wallet_address

    # Market Endpoints

    def get_tickers(self):
        """Get all market tickers
        Please note: If any field is unavailable due to a lack of trade history or a lack of 24hr data, the field will be set to 'N/A'. percentChange, baseVolume, and quoteVolume will never be 'N/A' but may be 0.
        https://github.com/AuroraDAO/idex-api-docs#returnticker
        .. code:: python
            tickers = client.get_tickers()
        :returns: API Response
        .. code-block:: python
            {
                ETH_SAN:  {
                    last: '0.000981',
                    high: '0.0010763',
                    low: '0.0009777',
                    lowestAsk: '0.00098151',
                    highestBid: '0.0007853',
                    percentChange: '-1.83619353',
                    baseVolume: '7.3922603247161',
                    quoteVolume: '7462.998433'
                },
                ETH_LINK: {
                    last: '0.001',
                    high: '0.0014',
                    low: '0.001',
                    lowestAsk: '0.002',
                    highestBid: '0.001',
                    percentChange: '-28.57142857',
                    baseVolume: '13.651606265667369466',
                    quoteVolume: '9765.891979953083752189'
                }
                # all possible markets follow ...
            }
        :raises:  IdexResponseException,  IdexAPIException
        """

        return self._post('returnTicker')

    def get_ticker(self, market):
        """Get ticker for selected market
        Please note: If any field is unavailable due to a lack of trade history or a lack of 24hr data, the field will be set to 'N/A'. percentChange, baseVolume, and quoteVolume will never be 'N/A' but may be 0.
        https://github.com/AuroraDAO/idex-api-docs#returnticker
        :param market: Name of market e.g. ETH_SAN
        :type market: string
        .. code:: python
            ticker = client.get_ticker('ETH_SAN')
        :returns: API Response
        .. code-block:: python
            {
                last: '0.000981',
                high: '0.0010763',
                low: '0.0009777',
                lowestAsk: '0.00098151',
                highestBid: '0.0007853',
                percentChange: '-1.83619353',
                baseVolume: '7.3922603247161',
                quoteVolume: '7462.998433'
            }
        :raises:  IdexResponseException,  IdexAPIException
        """

        data = {
            'market': market
        }

        return self._post('returnTicker', False, json=data)
