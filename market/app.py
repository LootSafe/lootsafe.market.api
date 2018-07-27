import falcon

# Meta imports
from market.resources.meta.meta import MetaResource

# Market imports
from market.resources.market.get_base import GetBaseResource

# Vault imports
from market.resources.vault.get_vault import GetVaultResource

# Falcon api
api = application = falcon.API()

# Routes
api.add_route("/meta", MetaResource())

api.add_route("/market/base", GetBaseResource())
api.add_route("/vault/get", GetVaultResource())
