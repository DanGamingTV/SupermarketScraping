const fs = require('fs');

var paths = ["G:\\Work\\Projects\\Hobbies\\SupermarketScraping\\Paknsave\\data\\latest.json"]
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
  if (price.priceData.bestPricePerLitre && price.productData.name.includes('V') && !price.productData.name.includes('G-Force')) {
  //var price = {'productData': {'name': price_old['productData']['name']}, 'priceData': price_old['priceData']}
  var tempOb = price.priceData
  tempOb['name'] = price.productData.name
  if (price.store) {
    tempOb['store'] = price.store.name
  }
  newArray.push(tempOb)
  }
}

newArray.sort(compare);
console.log('==============')
console.log(newArray)
