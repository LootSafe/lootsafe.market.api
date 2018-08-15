import falcon
from falcon.http_status import HTTPStatus

class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
        if req.method == 'OPTIONS':
            raise HTTPStatus(falcon.HTTP_200, body='\n')

# Meta imports
from market.resources.meta.meta import MetaResource

# Market imports
from market.resources.market.get_base import GetBaseResource
from market.resources.market.get_listings import GetListingsResource
from market.resources.market.get_filtered_listings import GetFilteredListingsResource
from market.resources.market.get_daily_volume import GetDailyVolumeResource
from market.resources.market.new_market import NewMarketResource
from market.resources.market.get_markets import GetMarketsResource
# Vault imports
from market.resources.vault.get_vault import GetVaultResource

# Falcon api
api = application = falcon.API(middleware=[HandleCORS()])

# Routes
api.add_route('/meta', MetaResource())

# Market
api.add_route('/market/base', GetBaseResource())
api.add_route('/market/listings', GetListingsResource())
api.add_route('/market/listings/filtered', GetFilteredListingsResource())
api.add_route('/market/volume', GetDailyVolumeResource())
api.add_route('/market/new', NewMarketResource())
api.add_route('/market/list', GetMarketsResource())
# Vault
api.add_route('/vault/get', GetVaultResource())

