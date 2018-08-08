import falcon
import json

from market.models.Market import MarketModel


class GetMarketsResource(object):
    def on_get(self, req, resp):
        market = MarketModel()
        markets = market.get_markets()

        doc = {
            "message": "Markets fetched.",
            "data": markets
        }

        resp.body = json.dumps(doc)
        resp.status = falcon.HTTP_200