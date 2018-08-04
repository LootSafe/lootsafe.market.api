import falcon
import json

from market.models.Market import MarketModel


class GetBaseResource(object):
    def on_get(self, req, resp):
        market = MarketModel(contract_address=req.params.get('market_address'))
        base = market.get_base_pair()

        doc = {
            'message': 'Base pair fetched.',
            'data': base
        }

        resp.body = json.dumps(doc)
        resp.status = falcon.HTTP_200
