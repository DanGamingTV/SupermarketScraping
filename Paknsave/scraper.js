//var JSSoup = require('jssoup').default
const fetch = require('node-fetch')
var Xray = require('x-ray')
var xraysus = Xray()

var storeURL = "https://www.paknsave.co.nz"
var productPrefix = "pns"

var dollars_pattern = '>([0-9][0-9]?)'
var cents_pattern = '>([0-9][0-9])'

function getStoreIDs() {
    var storeIDs = []
    storeListEndpoint = storeURL + "/CommonApi/Store/GetStoreList"
    fetch(storeListEndpoint)
    .then(response => response.json())
    .then(data => {
        var stores = data['stores']
        for (store of stores) {
            storeIDs.push(store['id'])
        }
        return storeIDs
    })
}

function getStores() {
    var stores_list = []
    var storeListEndpoint = storeURL + "/CommonApi/Store/GetStoreList"
    return fetch(storeListEndpoint)
    .then(response => response.json())
    .then(data => {
        var stores = data['stores']
        for (store of stores) {
            stores_list.push(store)
        }
        return stores_list
    })
    
}

function getProductPrice(productId, storeId) {
    var url = `${storeURL}/CommonApi/Store/ChangeStore?storeId=${storeId}`
    var baseurl = `${storeURL}/shop/product/${productId}`
    fetch(baseurl)
    return fetch(url).then((ballsobama) => { 
        //ballsobama.text().then(console.log)
    var price;
    return xraysus(`${storeURL}/shop/product/${productId}`, {
  dollars: ['.fs-price-lockup__dollars'],
  cents: ['fs-price-lockup__cents'],
  name: ['.u-h4.u-color-dark-grey']
})(function (err, obj) {
        //console.log(response)
        //var soup = new JSSoup(response)
        //console.log('obj', JSON.stringify(obj))
        
    }).then(stuff => {
        var cents = stuff.cents;
        var dollars = stuff.dollars;
        var productName = stuff.name[0];
        var centsprice = cents
        var dollarsprice = dollars
        if (dollarsprice.length > 0) {
            if (centsprice.length > 0) {
                var salePrice = `${dollarsprice[0]}.${centsprice[0]}`
            } else {
                var salePrice = `${dollarsprice[0]}.00`
            }
        } else {
            if (centsprice.length > 0) {
                var salePrice = `0.${centsprice[0]}`
            } else {
                var salePrice = "0.00"
            }
        }

        var price = {'name': productName, 'bestPrice': salePrice, 'price': salePrice}
        var internalProductId = productId.replace(productPrefix, '')
        return fetch(`${storeURL}/CommonApi/PromoGroup/GetPromoGroup?productId=${productId}`).then(r => r.json()).then(response => {
            if (response['success'] == true) {
                var multibuyQuantity = response['promoGroup']['multiBuyQuantity']
                var multibuyPrice = response['promoGroup']['multiBuyPrice']
                if (multibuyQuantity > 1) {
                    price['multiBuy'] = {'quantity': multibuyQuantity, 'value': multibuyPrice, 'perUnit': multibuyPrice/multibuyQuantity}
                    price['bestPrice'] = multibuyPrice/multibuyQuantity
                }
            }
            return price
        }).then(awesome => {
            return awesome
        })
    })
})
    
}
var dataList = []
var stores = [];
function massPriceScraper_Runner(product_id, store_id, i) {
    return getProductPrice(product_id, store_id).then(dataa => {
        dataList.push({'priceData': dataa, 'store': stores[a]})
        console.log(dataa, stores[i]['name'])
    })
}

var productsToCheck = ["5011153_ea_000"]

for (a of productsToCheck) {
    getStores().then(sto => {
        stores = sto
        var currentInt = 0;
        for (i=0;i<stores.length;i++) {
            var sussyArgs = []
            massPriceScraper_Runner(a, stores[i]['id'], i)

        }
    })
}
