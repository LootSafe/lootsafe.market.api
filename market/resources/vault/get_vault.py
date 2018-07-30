import falcon
import json

from market.models.Market import MarketModel


class GetVaultResource(object):
    def on_post(self, req, resp):
        body = json.loads(req.stream.read())
        merchant_address = body['merchant']
        market = MarketModel()
        base = market.get_vault(merchant_address)

        doc = {
            'message': 'Merchant vault fetched.',
            'data': base
        }

        resp.body = json.dumps(doc)
        resp.status = falcon.HTTP_200
