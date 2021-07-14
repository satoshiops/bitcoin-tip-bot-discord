import logging
import lnpay as LNPay
import qrcode
import io

lnpay_api_key = open('./private_data/lnpay_api_key.txt',
                     'r').read().split('\n')[0]
LNPay.initialize(lnpay_api_key)


def log(msg, type='info'):
    print(msg)
    if type == 'info':
        logging.info(msg)
    elif type == 'error':
        logging.error(msg)
    elif type == 'debug':
        logging.debug(msg)
    elif type == 'critical':
        logging.critical(msg)


def create_wallet(name):
    wallet_params = {
        'user_label': name
    }
    new_wallet = LNPay.create_wallet(wallet_params)
    log("new wallet created: ")
    print(new_wallet)

    example_value_of_new_wallet = {
        'id': 'wal_', 'created_at': 1611472924, 'updated_at': 1611472924,
        'user_label': 'test-wallet-created-from-lnpay-py', 'balance': 0,
        'statusType': {
            'type': 'wallet',
            'name': 'active',
            'display_name': 'Active'
        },
        'access_keys': {
            'Wallet Admin': ['waka_'],
            'Wallet Invoice': ['waki_'],
            'Wallet Read': ['wakr_']
        }
    }

    return new_wallet

# Converts a Lightning Invoice String to a QR code for easier depositing
# @param   { String } invoice 	The Lightning Invoice String
# @returns { Array }  arr 	    The raw image data 
def invoice_to_qrcode(invoice):
	q = qrcode.make(invoice)
	arr = io.BytesIO()
	q.save(arr, format="PNG")
	arr.seek(0)
	return arr
