import falcon
import json

import configparser

config = configparser.ConfigParser()
config.read("market/config.ini")

market_address = config.get("DEFAULT", "MARKET_ADDRESS")

class MetaResource(object):
    def on_get(self, req, resp):
        user = None


        doc = {
            "addresses": {
                "market": market_address
            }
        }

        resp.body = json.dumps(doc, ensure_ascii=False)
        resp.status = falcon.HTTP_200