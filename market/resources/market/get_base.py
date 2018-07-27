import falcon
import json

from market.models.Market import MarketModel


class GetBaseResource(object):
    def on_post(self, req, resp):
        body = json.loads(req.stream.read())
        market_address = body["market_address"]
        market = MarketModel(market_address)
        base = market.get_base_pair()

        doc = {
            "message": "Base pair fetched.",
            "data": base
        }

        resp.body = json.dumps(doc)
        resp.status = falcon.HTTP_200