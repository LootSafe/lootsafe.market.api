import falcon
import json
import configparser
from bson.json_util import dumps

from market.models.Market import MarketModel

config = configparser.ConfigParser()
config.read('market/config.ini')


class GetHistoryResponse(object):
    def on_get(self, req, resp):
        address = req.params.get('address')
        market = MarketModel()
        history = market.get_history(address)

        doc = {
            "message": "History fetched.",
            "data": history
        }

        resp.body = dumps(doc)
        resp.status = falcon.HTTP_200
