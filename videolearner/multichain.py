from django.conf import settings
from django.utils import timezone
from savoir import Savoir


class MultichainException(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code

    def __str__(self):
        args = (self.message, self.code)
        return "Multichain RPC returned with error: %s, code: %d" % args


class InsufficientCreditsException(MultichainException):
    def __init__(self, message):
        MultichainException.__init__(self, message, -4)


class MultichainRPC(object):

    api = Savoir(
        settings.MULTICHAIN_RPC_USER,
        settings.MULTICHAIN_RPC_PASSWORD,
        settings.MULTICHAIN_RPC_HOST,
        settings.MULTICHAIN_RPC_PORT,
        settings.MULTICHAIN_CHAINNAME
    )

    def create_chain_address(self):
        chain_address = self.api.getnewaddress()
        self.api.grant(chain_address, "receive")
        return chain_address

    def refresh_credits(self):
        self.api.issuemore(
            settings.MULTICHAIN_ISSUEADDRESS,
            settings.MULTICHAIN_ASSETNAME,
            settings.MULTICHAIN_ISSUEQTY)

    def award_credits(self, address, amount):
        response = self.api.sendassetfrom(
                settings.MULTICHAIN_ISSUEADDRESS, address,
                settings.MULTICHAIN_ASSETNAME, amount)
        if 'error' in response and response['error']['code'] == -4:
            raise InsufficientCreditsException(response['error']['message'])
        elif 'error' in response:
            raise MultichainException(
                response['error']['message'],
                response['error']['code']
            )
        return response

    def get_credits(self, address, startdate=None, enddate=None):
        asset_name = settings.MULTICHAIN_ASSETNAME
        if startdate is None and enddate is None:
            result = self.api.getmultibalances(address, [asset_name])
            return int(result['total'][0]['qty'])

        transactions = self.api.listaddresstransactions(address)
        total_credits = 0
        for transaction in transactions:
            timestamp = transaction['timereceived']
            tx_time = timezone.datetime.fromtimestamp(timestamp)
            tx_time = timezone.make_aware(tx_time)
            if tx_time >= startdate and tx_time <= enddate:
                assets = transaction['balance']['assets']
                for asset in assets:
                    if asset['name'] == asset_name:
                        total_credits += int(assets[0]['qty'])
                        break
        return total_credits
