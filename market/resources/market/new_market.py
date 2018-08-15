import falcon
import json
import configparser

from market.models.Market import MarketModel

config = configparser.ConfigParser()
config.read('market/config.ini')

class NewMarketResource(object):
    def on_post(self, req, resp):
        market = MarketModel()
        body = json.loads(req.json())

        new_market = None

        print(config.get('DEFAULT', 'APIKEY'))
        if body.get('api_key') == config.get('DEFAULT', 'APIKEY'):
            new_market = market.register_market(body.get('name'), body.get('address'), body.get('token_type'))
            if new_market:
                doc = {
                    'message': new_market
                }

                resp.body = json.dumps(doc)
                resp.status = falcon.HTTP_500
            else:
                doc = {
                    'message': 'New market has been registered!'
                }
                resp.body = json.dumps(doc)
                resp.status = falcon.HTTP_200
        else:
            doc = {
                'message': 'Invalid API key'
            }

            resp.body = json.dumps(doc)
            resp.status = falcon.HTTP_401
