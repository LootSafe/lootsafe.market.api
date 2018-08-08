# lootsafe.market.api
This package runs a useful API service for the LootSafe marketplace which caches Listings and other core componets of the market
to aid in faster navigation and sorting/searching of the market.

## Documentation
Documentation can be found [here via Postman](https://documenter.getpostman.com/view/254497/RWMLL6aa).

## Prerequisites
Please insure the following is installed before trying to run the API.

```
NodeJS Latest
Python 3.6.0+
PIP3
MongoDB
```

## Starting the API
The API runs off [gunicorn](http://gunicorn.org/) and can be run using the following steps
```bash
pip install -r requirements.txt
gunicorn --reload market.app
```

## Cacher Script
The cacher script is under `cacher` and can be started by running `sh scripts/start_cahcer.sh` from the root directory. 
Currently the cacher is written in Javascript because web3.py seems to be having issues running wss with infrua.
Node must be installed to run the cacher.

## Audits
The code reviewed by New Alchemy is in the GitHub repository (https://github.com/LootSafe/lootsafe.marketplace.contracts) at commit hash `d87b8c89a8851971c90248e8b5415137320053d6`.

contracts/Market.sol `ac147a333fe9b08067bb41e63fd425ecaed2e92b` <br />
contracts/Migrations.sol `19a7c00c1123db1875e307e7186c323b4092434b` <br />
contracts/Vault.sol `56cde2b4bfeb365e43a9667037f39f3c56e1c0f3`<br />
contracts/lib/Cellar.sol `3479c87b345a616bd64df157520402b64ecea254`<br />
contracts/lib/EIP20.sol `f74bcd48457fa08f890beb394b3dd5009b4a026a`<br />
contracts/lib/EIP20Interface.sol `3daf1c7e479a85f6a1b3e230429f568c081e4bcd`

Full Audit [LootSafe Smart Contract Audit v1.0.pdf](https://github.com/LootSafe/lootsafe.market.api/blob/master/docs/LootSafe%20Smart%20Contract%20Audit%20v1.0.pdf)