const fs = require('fs');

var theRootThing = "G:\\Work\\Projects\\Hobbies\\SupermarketScraping\\data\\"

var paths = [`${theRootThing}mightyape\\latest.json`, `${theRootThing}paknsave\\latest.json`, `${theRootThing}countdown\\latest.json`, `${theRootThing}freshchoice\\latest.json`, `${theRootThing}supervalue\\latest.json`, `${theRootThing}thewarehouse\\latest.json`]
var rawData;
var jsonData = [];

for (var path of paths) {
  rawdata = fs.readFileSync(path);
  jsonData = jsonData.concat(JSON.parse(rawdata))
}

function compare( a, b ) {
  if ( a.bestPricePerLitre < b.bestPricePerLitre ){
    return -1;
  }
  if ( a.bestPricePerLitre > b.bestPricePerLitre ){
    return 1;
  }
  return 0;
}

var newArray = [];

for (var price of jsonData) {
  if (price.priceData.bestPricePerLitre && (price.productData.name.toLowerCase()).includes('mother')) {
  //var price = {'productData': {'name': price_old['productData']['name']}, 'priceData': price_old['priceData']}
  var tempOb = price.priceData
  tempOb['name'] = price.productData.name
  tempOb['productShopPage'] = price.productData.productShopPage
  if (price.store) {
    tempOb['store'] = price.store.name
  }
  newArray.push(tempOb)
  }
}

newArray.sort(compare);
console.log('==============')
console.log(newArray)
