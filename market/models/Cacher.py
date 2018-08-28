import json
import configparser
from threading import Timer
import pymongo
import time
from web3 import Web3, WebsocketProvider
import chalk

config = configparser.ConfigParser()
config.read('market/config.ini')

client = pymongo.MongoClient(config.get('DB', 'DB_URI'))
db = client[config.get('DB', 'DB')]

# Connect to HTTPProvider (NOTE: wss broken)
w3 = Web3(WebsocketProvider(config.get('NETWORK', 'WS_RPC_ADDRESS')))


class CacherModel:
    def __init__(self, contract_address=config.get('NETWORK', 'MARKET_ADDRESS')):
        self.contract_address = contract_address
        self.scan_height = 0
        with open('market/core_contracts/build/contracts/Market.json', 'r') as abi_definition:
            info_json = json.load(abi_definition)
            abi = info_json["abi"]
        self.contract = w3.eth.contract(address=contract_address, abi=abi)

    def cache(self):
        if w3.eth.blockNumber > self.scan_height:
            self.scan()
            print(chalk.cyan('[CACHER]') + '(' + chalk.green(
                'Event: NewBlock') + ') - New block found, scanning')
        cache = Timer(3.0, self.cache)
        cache.start()

    def scan(self):
        listings_created = self.get_event_entries('ListingCreated')
        listings_fulfilled = self.get_event_entries('ListingFulfilled')
        listings_cancelled = self.get_event_entries('ListingCancelled')

        for event in listings_created:
            listing_id = event.args.id
            listings_table = db['listings']
            listings = listings_table.find({ 'id': listing_id })

            if listings.count() < 1:
                print(chalk.cyan('[CACHER]') + '(' + chalk.green(
                    'Event: ListingCreated') + ') - New listing created, listing id: ' + str(listing_id))
                listing = self.contract.call().listings(listing_id)

                local_listing = {
                    'id': listing_id,
                    'date': listing[1],
                    'merchant': listing[2],
                    'asset': listing[3],
                    'amount': str(listing[4]),
                    'value': str(listing[5]),
                    'status': listing[6],
                    'market': config.get('NETWORK', 'MARKET_ADDRESS')
                }

                listings_table.insert_one(local_listing)

                with open('market/core_contracts/build/contracts/EIP20.json', 'r') as abi_definition:
                    info_json = json.load(abi_definition)
                    abi = info_json["abi"]
                asset_contract = w3.eth.contract(address=listing[3], abi=abi)
                tokens_table = db['tokens']
                local_asset = tokens_table.find({'address': listing[3]})
                if local_asset.count() < 1:
                    print(chalk.cyan('[CACHER]') + '(' + chalk.green(
                        'Event: TokenDiscovered') + ') - New token discovered: ' + asset_contract.call().name())

                    asset = {
                        'name': asset_contract.call().name(),
                        'address': listing[3],
                        'symbol': asset_contract.call().symbol(),
                    }
                    tokens_table.insert_one(asset)

        for event in listings_fulfilled:
            listing_id = event.args.id
            listings_table = db['listings']
            listings = listings_table.find({'id': listing_id})
            if listings.count() > 0 and listings[0].get('fulfilled_at') is None:
                print(chalk.cyan('[CACHER]') + '(' + chalk.green(
                    'Event: ListingFulfilled') + ') - Listing has been fulfilled, listing id: ' + str(listing_id))
                db['listings'].update_one({
                    'id': listing_id
                },
                    {
                        '$set': {
                            'status': 1,
                            'fulfilled_at': time.time()
                        }
                    }, upsert=False)

        for event in listings_cancelled:
            listing_id = event.args.id
            listings_table = db['listings']
            listings = listings_table.find({'id': listing_id})
            if listings.count() > 0 and listings[0].get('status') is not 2:
                print(chalk.cyan('[CACHER]') + '(' + chalk.green(
                    'Event: ListingCancelled') + ') - Listing has been cancelled, listing id: ' + str(listing_id))
                db['listings'].update_one({
                    'id': listing_id
                },
                    {
                        '$set': {
                            'status': 2
                        }
                    }, upsert=False)

        self.scan_height = w3.eth.blockNumber

    def get_event_entries(self, event_name):
        myfilter = self.contract.events[event_name].createFilter(fromBlock=1, toBlock='latest')
        eventlist = myfilter.get_all_entries()
        return eventlist
