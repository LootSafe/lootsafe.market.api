const fs = require("fs")
const ini = require('ini')
const config = ini.parse(fs.readFileSync('market/config.ini', 'utf-8'))

const mongoose = require('mongoose');
mongoose.connect(config.DB.DB_URI + config.DB.DB);

const MarketSchema = new mongoose.Schema({
    name: String,
    address: String,
    type: String
});
const MarketModel = mongoose.model('Market', MarketSchema);

const ListingSchema = new mongoose.Schema({
    id: Number,
    date: Number,
    merchant: String,
    asset: String,
    amount: Number,
    value: Number,
    status: Number,
    fulfilled_at: Number,
    market: String
});
const ListingModel = mongoose.model('Listing', ListingSchema);

const TokenSchema = new mongoose.Schema({
    type: String,
    address: String,
    name: String,
    symbol: String
});
const TokenModel = mongoose.model('Token', TokenSchema);

const BlocksScannedSchema = new mongoose.Schema({
    blockheight: String
});
const BlocksScannedModel = mongoose.model('BlocksScanned', BlocksScannedSchema);

const Web3 = require('web3')

const abi = require('../market/core_contracts/build/contracts/Market.json').abi
const token_abi = require('../market/core_contracts/build/contracts/EIP20').abi
const provider = new Web3.providers.WebsocketProvider(config.NETWORK.WS_RPC_ADDRESS)
const web3 = new Web3(provider)

// TODO: save this somewhere to persist restarts
let scan_height = 0

const findBlocksScannedAndUpdate = (height) => {
    BlocksScannedModel.findOne({}, (err, block) => {
        if (block) {
            block.blockheight = height
            block.save()
        } else {
            const blockheight_save = new BlocksScannedModel({
                blockheight: height
            })
            blockheight_save.save()
        }
    })
}


const whatTokenType = () => {
    return new Promise((resolve, reject) => {

    })
}

module.exports = whatTokenType

const scan = (address, type) => {
    const Market = new web3.eth.Contract(abi, address)

    console.log('Scanning for listing events')
    let start = Date.now()

    Market.getPastEvents(
        'allEvents',
        {
            filter: {},
            fromBlock: scan_height,
            toBlock: 'latest'
        },
        function (error, events) {
            b = false

            const iterator = async (index) => {
                if (!b)
                    b = true
                    block = await web3.eth.getBlock('latest')
                    scan_height = block.number
                    findBlocksScannedAndUpdate(scan_height)


                if (index < events.length) {
                    if (events[index].event == 'ListingCreated' || events[index].event == 'ListingCancelled' || events[index].event == 'ListingFulfilled') {
                        const ListingEvent = events[index].returnValues
                        const Listing = await Market.methods.listings(ListingEvent.id).call()
                        const listing = {
                            id: parseInt(Listing.id),
                            date: Listing.date,
                            merchant: Listing.merchant,
                            asset: Listing.asset,
                            amount: parseFloat(Listing.amount),
                            value: parseFloat(Listing.value),
                            status: parseInt(Listing.status),
                            market: address
                        }
                        if (Listing.status == 1) {
                            const block = await web3.eth.getBlock(events[index].blockNumber)
                            listing.fulfilled_at = block.timestamp
                        }

                        ListingModel.findOne({ id: listing.id, market: address }, (err, ls) => {
                            if (ls) {
                                ls.status = listing.status
                                ls.fulfilled_at = listing.fulfilled_at
                                ls.save()
                            } else {
                                const listing_save = new ListingModel(listing)
                                listing_save.save()
                            }
                        })

                        TokenModel.findOne({ 'address': listing.asset }, async (err, token) => {
                            if (!token) {
                                const token_contract = new web3.eth.Contract(token_abi, listing.asset)

                                const new_token = new TokenModel({
                                    type,
                                    address: listing.asset,
                                    name: await token_contract.methods.name().call(),
                                    symbol: await token_contract.methods.symbol().call()
                                })

                                new_token.save()
                            }
                        })
                        console.log(events[index].event + ' event for listing ' + listing.id)
                    }
                    iterator(index + 1)
                } else {
                    console.log('Scan complete in ' + (Date.now() - start) + '(ms), waiting for new block...')
                    var subscription = web3.eth.subscribe('newBlockHeaders', function(error, result) {
                        if (error)
                            console.log(error);
                    }).on("data", function(blockHeader){
                        scan(address, type)
                        subscription.unsubscribe()
                    });
                }
            }

            iterator(0)

        }
    )
}

BlocksScannedModel.findOne({}, (err, block) => {
    if (block) {
        scan_height = block.blockheight
    }

    MarketModel.find({}, (err, markets) => {
        markets.map(market => {
            scan(market.address, market.type)
        })
    })
})
