import falcon
import chalk
from falcon.http_status import HTTPStatus
from market.models.Cacher import CacherModel

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
from market.resources.market.get_last_sell import GetLastSellResource
from market.resources.market.get_lowest_ask import GetLowestAskResource
from market.resources.market.get_last_ten import GetLastTenResource
from market.resources.market.get_history import GetHistoryResponse
# Vault imports
from market.resources.vault.get_vault import GetVaultResource


class ResponseLoggerMiddleware(object):
    def process_response(self, req, resp, resource, req_succeeded):
        print(chalk.green(req.method) + ' ' + chalk.cyan(req.relative_uri) + ' ' + chalk.yellow(resp.status[:3]))

# Falcon api
api = application = falcon.API(middleware=[HandleCORS(), ResponseLoggerMiddleware()])

# Routes
api.add_route('/meta', MetaResource())

# Market
api.add_route('/market/base', GetBaseResource())
api.add_route('/market/listings', GetListingsResource())
api.add_route('/market/listings/filtered', GetFilteredListingsResource())
api.add_route('/market/volume', GetDailyVolumeResource())
api.add_route('/market/new', NewMarketResource())
api.add_route('/market/list', GetMarketsResource())
api.add_route('/market/lastsell', GetLastSellResource())
api.add_route('/market/lowestask', GetLowestAskResource())
api.add_route('/market/lastten', GetLastTenResource())
api.add_route('/market/history', GetHistoryResponse())
# Vault
api.add_route('/vault/get', GetVaultResource())

cacher = CacherModel()
cacher.cache()
