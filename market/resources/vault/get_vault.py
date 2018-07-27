import falcon
import json

from market.models.Market import MarketModel


class GetVaultResource(object):
    def on_post(self, req, resp):
        body = json.loads(req.stream.read())
        market_address = body["market_address"]
        merchant_address = body["merchant_address"]
        market = MarketModel(market_address)
        base = market.get_vault(merchant_address)

        doc = {
            "message": "Merchant vault fetched.",
            "data": base
        }

        resp.body = json.dumps(doc)
        resp.status = falcon.HTTP_200