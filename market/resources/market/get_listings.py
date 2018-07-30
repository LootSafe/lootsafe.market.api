import falcon
import json

from market.models.Market import MarketModel


class GetListingsResource(object):
    def on_get(self, req, resp):

        market = MarketModel()
        listings = market.get_listings()

        doc = {
            "message": "Listings fetched.",
            "data": listings
        }

        resp.body = json.dumps(doc)
        resp.status = falcon.HTTP_200