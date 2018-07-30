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