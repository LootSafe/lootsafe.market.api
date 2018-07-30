import falcon
import json

import configparser

config = configparser.ConfigParser()
config.read("market/config.ini")

rpc_address = config.get("NETWORK", "RPC_ADDRESS")


class MetaResource(object):
    def on_get(self, req, resp):
        user = None

        doc = {
            "network": {
                "rpc_address": rpc_address
            }
        }

        resp.body = json.dumps(doc, ensure_ascii=False)
        resp.status = falcon.HTTP_200
