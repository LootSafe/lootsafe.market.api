import falcon
import json

from market.models.Market import MarketModel


class GetFilteredListingsResource(object):
    def on_post(self, req, resp):
        body = json.loads(req.json())

        find_filter = {}

        if 'market_address' in body:
            market = MarketModel(contract_address=body.get('market_address'))

            if 'merchant' in body:
                find_filter['merchant'] = body.get('merchant')

            if 'asset' in body:
                find_filter['asset'] = body.get('asset')

            if 'amount' in body:
                find_filter['amount'] = body.get('amount')

            if 'status' in body:
                find_filter['status'] = body.get('status')

            if 'value' in body:
                find_filter['value'] = body.get('value')

            sort_by = 'date'
            order = 'ascending'

            if 'sort_by' in body and 'order' in body:
                sort_by = body.get('sort_by')
                order = body.get('order')

            if 'limit' in body:
                listings = market.get_listings_filtered(find_filter, body.get('limit'), sort_by, order)
            else:
                listings = market.get_listings_filtered(find_filter)

            doc = {
                'message': 'Listings fetched.',
                'data': listings
            }

            resp.body = json.dumps(doc)
            resp.status = falcon.HTTP_200

        else:
            doc = {
                'message': 'Missing market address!'
            }
            resp.body = json.dumps(doc)
            resp.status = falcon.HTTP_404
