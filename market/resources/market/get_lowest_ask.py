import falcon
import json
import configparser

from market.models.Market import MarketModel

config = configparser.ConfigParser()
config.read('market/config.ini')


class GetLowestAskResource(object):
    def on_get(self, req, resp):
        asset = req.params.get('asset')
        market = MarketModel()
        last_sell = market.get_lowest_ask(asset)

        doc = {
            "message": "Lowest ask fetched.",
            "data": last_sell
        }

        resp.body = json.dumps(doc)
        resp.status = falcon.HTTP_200
