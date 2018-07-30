import json
import configparser
import pymongo

from web3 import Web3, HTTPProvider

config = configparser.ConfigParser()
config.read('market/config.ini')

client = pymongo.MongoClient(config.get('DB', 'DB_URI'))
db = client[config.get('DB', 'DB')]

# Connect to HTTPProvider (NOTE: wss broken)
w3 = Web3(HTTPProvider(config.get('NETWORK', 'RPC_ADDRESS')))


class MarketModel:
    def __init__(self, contract_address=config.get('NETWORK', 'MARKET_ADDRESS')):
        with open('market/contracts/build/contracts/Market.json', 'r') as abi_definition:
            info_json = json.load(abi_definition)
            abi = info_json["abi"]
        self.contract = w3.eth.contract(address=contract_address, abi=abi)

    @staticmethod
    def clean(lst):
        c = []
        for item in lst:
            i = item
            i['_id'] = str(item.get('_id'))
            c.append(i)
        return c

    def get_listings(self):
        """ Get all listings """
        # Falcon doesn't like the bson id, stringify it first
        listings_table = db['listings']
        listings = listings_table.find().limit(config.get('DB', 'LIMIT'))
        return self.clean(listings)

    def get_listings_filtered(self, filter_obj, limit=config.get('DB', 'LIMIT'), sort_by='date', order='ascending'):
        """ Get all listings by a specific filter """

        if limit > config.get('DB', 'LIMIT'):
            limit = config.get('DB', 'LIMIT')

        listings_table = db['listings']
        pymongo_order = pymongo.ASCENDING if order == 'ascending' else pymongo.DESCENDING
        listings = listings_table.find(filter_obj).sort(sort_by, pymongo_order).limit(limit)
        return self.clean(listings)

    def get_base_pair(self):
        """ Get base pair of market """
        return self.contract.call().base()

    def get_vault(self, merchant):
        """ Get a vault by merchant address

        Keyword Arguments:
        merchant - address of the merchant to search on
        """
        return self.contract.call().vaults(merchant)
