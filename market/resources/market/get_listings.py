import falcon
import json
from fuzzywuzzy import process
from market.models.Market import MarketModel
import pymongo
import configparser

config = configparser.ConfigParser()
config.read('market/config.ini')

client = pymongo.MongoClient(config.get('DB', 'DB_URI'))
db = client[config.get('DB', 'DB')]


def clean(lst):
    c = []
    for item in lst:
        i = item
        i['_id'] = str(item.get('_id'))
        c.append(i)
    return c

class GetListingsResource(object):
    def on_get(self, req, resp):
        keyword = req.params.get('keyword')

        tokens = db['tokens']
        listings = db['listings']

        unparsed_tokens = tokens.find()

        token_names = []
        for token in unparsed_tokens:
            token_names.append(token.get('name'))

        results = process.extract(keyword, token_names, limit=4)

        found_tokens = []
        for result in results:
            if result[1] > 80:
                found_tokens = found_tokens + list(tokens.find({'name': result[0]}))

        found_listings = []
        for token in found_tokens:
            found_listings = found_listings + list(listings.find({'asset': token.get('address'), 'status': 0}).limit(10))

        doc = {
            "message": "Listings fetched.",
            "data": clean(found_listings)
        }

        resp.body = json.dumps(doc)
        resp.status = falcon.HTTP_200
