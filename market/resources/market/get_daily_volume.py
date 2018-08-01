import falcon
import json

from market.models.Market import MarketModel


class GetDailyVolumeResource(object):
    def on_get(self, req, resp):

        market = MarketModel()
        volume = market.get_daily_volume()

        doc = {
            "message": "Daily volume fetched.",
            "data": volume
        }

        resp.body = json.dumps(doc)
        resp.status = falcon.HTTP_200
