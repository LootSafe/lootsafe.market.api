import json
import web3
import configparser

from web3 import Web3, HTTPProvider, TestRPCProvider
from solc import compile_source

config = configparser.ConfigParser()
config.read('market/config.ini')

# TODO: add this to a config
w3 = Web3(HTTPProvider(config.get('NETWORK', 'RPC_ADDRESS')))


class MarketModel:
    def __init__(self, contract_address):
        with open("market/contracts/build/contracts/Market.json", "r") as abi_definition:
            info_json = json.load(abi_definition)
            abi = info_json["abi"]
        self.contract = w3.eth.contract(address=contract_address, abi=abi)

    def get_base_pair(self):
        return self.contract.call().base()

    def get_vault(self, merchant):
        return self.contract.call().vaults(merchant)

    def watch_listings(self):
        event_filter = self.contract.events.ListingCreated.createFilter()
