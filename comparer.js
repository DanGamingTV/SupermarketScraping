const fs = require('fs');

var theRootThing = "./data/"

var supermarket_foldernames = ['paknsave', 'countdown', 'mightyape', 'thewarehouse', 'freshchoice', 'supervalue']

var paths = []

for (var supermarketname of supermarket_foldernames) {
  console.log(supermarketname)
  var files = fs.readdirSync(`${theRootThing}${supermarketname}/archive`)
  var previousCheckFile = files[files.length - 2]
  var currentCheckFile = 'latest.json'
  paths.push({
    "shorthand": `${supermarketname} Earlier`,
    "path": `${theRootThing}${supermarketname}/archive/${previousCheckFile}`
  })
  paths.push({
    "shorthand": `${supermarketname} Now`,
    "path": `${theRootThing}${supermarketname}/${currentCheckFile}`
  })
}

var rawData;
var jsonData = {};

var objectsPushed = {}

for (var path of paths) {
  rawdata = fs.readFileSync(path.path);
  var tempData = JSON.parse(rawdata)
  for (var key of tempData.slice(1)) {
    var objectToPush = {
      'fileMeta': path,
      'entry': key
    }
    var uniqueObjectKey = key.store ? `${key.productData.productId}_${key.store.id}` : key.productData.productId
    if (jsonData[uniqueObjectKey]) {
      jsonData[uniqueObjectKey].push(objectToPush)
      objectsPushed[uniqueObjectKey].count += 1;
    } else {
      jsonData[uniqueObjectKey] = [objectToPush]
      objectsPushed[uniqueObjectKey] = {
        'count': 1
      }
    }
  }
}

function compare(a, b) {
  if (a.bestPricePerLitre < b.bestPricePerLitre) {
    return -1;
  }
  if (a.bestPricePerLitre > b.bestPricePerLitre) {
    return 1;
  }
  return 0;
}

var newArray = [];

function percIncrease(a, b) {
  let percent;
  if (b !== 0) {
    if (a !== 0) {
      percent = (b - a) / a * 100;
    } else {
      percent = b * 100;
    }
  } else {
    percent = -a * 100;
  }
  return Math.floor(percent);
}

for (var objectKey of Object.keys(jsonData)) {
  var content_entry = jsonData[objectKey];
  if (content_entry.length > 1) {
    var price_a = content_entry[0].entry.priceData.bestPrice;
    var price_b = content_entry[1].entry.priceData.bestPrice;
    var change_string = "no change";
    var percentageChange = percIncrease(price_a, price_b);
    if (percentageChange != 0 && (price_a > 0 && price_b > 0)) {
      change_string = percentageChange > 0 ? `${percentageChange}% more` : `${percentageChange}% less`
      var prodName = content_entry[0].entry.productData.name;
      var storeName = content_entry[0].entry.store ? content_entry[0].entry.store.name : content_entry[0].fileMeta.shorthand;
      var terminalColor = percentageChange < 0 ? "\x1b[32m" : "\x1b[31m"
      terminalColor = percentageChange == 0 ? "\x1b[36m" : terminalColor
      console.log()
      console.log(`${prodName}`)
      console.log(`Old price: ${price_a}, New Price: ${price_b}`)
      console.log(`${terminalColor}%s\x1b[0m`, `(${change_string}) at ${storeName} - ${content_entry[0].fileMeta.shorthand}`)
      console.log()
      newArray.push({
        'name': prodName,
        'previousPrice': price_a,
        'currentPrice': price_b,
        'percentageChange': percentageChange,
        'store': `${storeName} - ${content_entry[0].fileMeta.shorthand}`,
        'oldPricePerLitre': content_entry[0].entry.priceData.bestPricePerLitre,
        'currentPricePerLitre': content_entry[1].entry.priceData.bestPricePerLitre
      })
    }
  }
}

fs.writeFileSync('./data_changes/latest.json', JSON.stringify(newArray));
fs.writeFileSync(`./data_changes/archive/${new Date().getTime()}.json`, JSON.stringify(newArray));