const fs = require("fs")
const ini = require('ini')
const config = ini.parse(fs.readFileSync('market/config.ini', 'utf-8'))

const mongoose = require('mongoose');
mongoose.connect(config.DB.DB_URI + config.DB.DB);

const ListingSchema = new mongoose.Schema({
    id: Number,
    date: Number,
    merchant: String,
    asset: String,
    amount: Number,
    value: Number,
    status: Number,
    fulfilled_at: Number
});
const ListingModel = mongoose.model('Listing', ListingSchema);

const Web3 = require('web3')

const abi = require('../market/contracts/build/contracts/Market.json').abi
const provider = new Web3.providers.WebsocketProvider(config.NETWORK.WS_RPC_ADDRESS)
const web3 = new Web3(provider)
const Market = new web3.eth.Contract(abi, config.NETWORK.MARKET_ADDRESS)

// TODO: save this somewhere to persist restarts
let scan_height = 0

const scan = () => {
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
                    scan_height = await web3.eth.getBlock('latest').height

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
                            status: parseInt(Listing.status)
                        }
                        if (Listing.status == 1) {
                            const block = await web3.eth.getBlock(events[index].blockNumber)
                            listing.fulfilled_at = block.timestamp
                        }

                        ListingModel.findOne({ id: listing.id }, (err, ls) => {
                            if (ls) {
                                ls.status = listing.status
                                ls.fulfilled_at = listing.fulfilled_at
                                ls.save()
                            } else {
                                const listing_save = new ListingModel(listing)
                                listing_save.save()
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
                        scan()
                        subscription.unsubscribe()
                    });
                }
            }

            iterator(0)

        }
    )
}


scan()