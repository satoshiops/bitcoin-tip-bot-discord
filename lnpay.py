import json
import requests

__version__ = '0.1.1'

__VERSION__ = 'py' + __version__
__ENDPOINT_URL__ = 'https://api.lnpay.co/v1/'
__DEFAULT_WAK__ = ''
__PUBLIC_API_KEY__ = ''

def initialize(public_api_key, default_wak=None, params=None):
    """Initialization function for the LN Pay helper file

    Args:
        public_api_key (string): API key given from LNPay (lnpay.co)
        default_wak (string, optional): Wallet key given from LNPay. Defaults to None.
        params (Object, optional): Additional params/args. Defaults to None.
    """
    if params is None:
        params = {}

    print('initializing connection to LNPay...')

    global __VERSION__
    global __PUBLIC_API_KEY__
    global __ENDPOINT_URL__
    global __DEFAULT_WAK__

    __VERSION__ = 'py' + __version__
    __PUBLIC_API_KEY__ = public_api_key
    __ENDPOINT_URL__ = params.get('endpoint_url', __ENDPOINT_URL__)
    __DEFAULT_WAK__ = default_wak


def create_wallet(params):
    """Creates a new wallet for a Discord user

    Args:
        params (Object): Params for the wallet to be created

    Returns:
        JSON: JSON response from LNPay API
    """
    return post_request('wallet', params)


def get_request(location):
    """Get request helper that automatically adds headers, etc.

    Args:
        location (string): The URL of the GET request

    Returns:
        JSON: JSON response from LNPay
    """
    endpoint = __ENDPOINT_URL__ + location
    headers = {
        'X-Api-Key': __PUBLIC_API_KEY__,
        'X-LNPay-sdk': __VERSION__
    }

    r = requests.get(url=endpoint, headers=headers)
    return r.json()


def post_request(location, params):
    """POST request helper - same as GET request, just with parameters

    Args:
        location (string): URL of where we are sending data to
        params (Object):   Parameters required for the associated POST request

    Returns:
        JSON: JSON response from the LN Pay servers
    """
    endpoint = __ENDPOINT_URL__ + location
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': __PUBLIC_API_KEY__,
        'X-LNPay-sdk': __VERSION__
    }
    data = json.dumps(params)

    r = requests.post(url=endpoint, data=data, headers=headers)
    return r.json()


class LNPayWallet:
    """Helper class for managing wallets created via LNPay
    """

    def __init__(self, access_key_str):
        """Initialization function for loading a new wallet

        Args:
            access_key_str (string): wallet string to load into memory
        """

        if access_key_str:
            self.access_key = access_key_str
        elif __DEFAULT_WAK__ is not None:
            self.access_key = __DEFAULT_WAK__
        else:
            raise AttributeError(
                'No wallet access key specified! Set a default, or initialize LNPayWallet with one')

    def get_info(self):
        return get_request('wallet/{}'.format(self.access_key))

    def get_transactions(self):
        """
        Get a list of wallet transactions that have been SETTLED.
        This includes only transactions that have an impact on wallet balance.
        These DO NOT include unsettled/unpaid invoices.
        https://docs.lnpay.co/wallet/get-transactions
        Returns
        -------
        List of wallet transactions.
        """
        return get_request('wallet/{}/transactions'.format(self.access_key))

    def create_invoice(self, params):
        """
        Generates an invoice for this wallet.
        https://docs.lnpay.co/wallet/generate-invoice
        Parameters
        ----------
        params (Object): Object representing an invoice request. Example: `{'num_satoshis': 2,'memo': 'Tester'}`
        Returns
        -------
        LnTx Object (https://docs.lnpay.co/lntx/)
        """
        return post_request('wallet/{}/invoice'.format(self.access_key), params)

    def pay_invoice(self, params):
        """
        Pay a LN invoice from the specified wallet.
        https://docs.lnpay.co/wallet/pay-invoice
        Parameters
        ----------
        params (Object): Object representing an invoice payment request. Example: `{'payment_request': 'ln....'}`
        Returns
        -------
        Returns invoice payment information if successful or a specific error directly from the Lightning Node.
        """
        return post_request('wallet/{}/withdraw'.format(self.access_key), params)

    def internal_transfer(self, params):
        """
        Transfer sats from source wallet to destination wallet.
        https://docs.lnpay.co/wallet/transfers-between-wallets
        Parameters
        ----------
        params (Object): Object representing a transfer request. Example: `{'dest_wallet_id': 'w_XXX','num_satoshis': 1,'memo': 'Memo'}`
        Returns
        -------
        Transfer execution information.
        """
        return post_request('wallet/{}/transfer'.format(self.access_key), params)

    def get_lnurl(self, params):
        """
        Generate an LNURL-withdraw link.
        Note: These LNURLs are ONE-TIME use. This is to prevent repeated access to the wallet.
        https://docs.lnpay.co/wallet/lnurl-withdraw
        Parameters
        ----------
        params (Object): Object representing a lnurl withdraw request. Example: `{'num_satoshis': 1,'memo': 'SatsBack'}`
        Returns
        -------
        Generated lnurl object.
        """
        return get_request('wallet/{}/lnurl/withdraw?num_satoshis={}'.format(self.access_key, params['num_satoshis']))


class LNPayLnTx:
    def __init__(self, tx_id):
        self.tx_id = tx_id

    def get_info(self):
        """
        Gets the invoice information for the `tx_id` set in the `__init__` of this class.
        Returns
        -------
        LnTx (Lightning Invoice) Object
        https://docs.lnpay.co/lntx/
        """
        return get_request('lntx/{}'.format(self.tx_id))
