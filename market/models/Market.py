import json
import configparser
import pymongo
import time
from web3 import Web3, HTTPProvider

config = configparser.ConfigParser()
config.read('market/config.ini')

client = pymongo.MongoClient(config.get('DB', 'DB_URI'))
db = client[config.get('DB', 'DB')]

w3 = Web3(HTTPProvider(config.get('NETWORK', 'RPC_ADDRESS')))


class MarketModel:
    def __init__(self, contract_address=config.get('NETWORK', 'MARKET_ADDRESS')):
        self.contract_address = contract_address
        with open('market/core_contracts/build/contracts/Market.json', 'r') as abi_definition:
            info_json = json.load(abi_definition)
            abi = info_json["abi"]
        self.contract = w3.eth.contract(address=contract_address, abi=abi)

    @staticmethod
    def register_market(name, address, token_type):
        """ Register a market in the system

        Keyword Arguments:
        name - Name of the marketplace
        address - Address of the marketplace
        token_type - Type of tokens traded on the system (e.g. ERC20)
        """
        markets_table = db['markets']
        market = markets_table.find_one({'address': address})
        if market is not None:
            return "Error creating market, market already exists"
        else:
            markets_table.insert_one({
                "name": name,
                "address": address,
                "token_type": token_type
            })
            return None

    @staticmethod
    def clean(lst):
        c = []
        for item in lst:
            i = item
            i['_id'] = str(item.get('_id'))
            c.append(i)
        return c

    def get_markets(self):
        """ Get all markets """
        markets_table = db['markets']
        markets = markets_table.find()
        return self.clean(markets)

    def get_listings(self):
        """ Get all listings """
        # Falcon doesn't like the bson id, stringify it first
        listings_table = db['listings']
        listings = listings_table.find({'market': self.contract_address}).limit(int(config.get('DB', 'LIMIT')))
        return self.clean(listings)

    def get_listings_filtered(self, filter_obj, skip=0, limit=config.get('DB', 'LIMIT'), sort_by='date', order='ascending'):
        """ Get all listings by a specific filter """

        filter_obj['market'] = self.contract_address

        if limit > config.get('DB', 'LIMIT'):
            limit = config.get('DB', 'LIMIT')

        listings_table = db['listings']
        pymongo_order = pymongo.DESCENDING if order == 'DESCENDING' else pymongo.ASCENDING
        listings = listings_table.find(filter_obj).sort( '_id', -1).skip(skip).limit(int(limit))
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

    @staticmethod
    def get_daily_volume():
        """ Get 24 hour transaction volume """
        listings_table = db['listings']
        listings = listings_table.find({
            'fulfilled_at': {
                '$gte': time.time() - 86400
            },
            'status': 1
        })

        volume = 0
        for listing in listings:
            volume += int(listing.get('value'))

        return volume
