import falcon

# Meta imports
from market.resources.meta.meta import MetaResource

# Market imports
from market.resources.market.get_base import GetBaseResource
from market.resources.market.get_listings import GetListingsResource
from market.resources.market.get_filtered_listings import GetFilteredListingsResource
from market.resources.market.get_daily_volume import GetDailyVolumeResource

# Vault imports
from market.resources.vault.get_vault import GetVaultResource

# Falcon api
api = application = falcon.API()

# Routes
api.add_route('/meta', MetaResource())

# Market
api.add_route('/market/base', GetBaseResource())
api.add_route('/market/listings', GetListingsResource())
api.add_route('/market/listings/filtered', GetFilteredListingsResource())
api.add_route('/market/volume', GetDailyVolumeResource())
# Vault
api.add_route('/vault/get', GetVaultResource())

