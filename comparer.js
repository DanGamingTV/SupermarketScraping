const fs = require('fs');

var theRootThing = "G:\\Work\\Projects\\Hobbies\\SupermarketScraping\\data\\"

var supermarket_foldernames = ['paknsave', 'countdown', 'mightyape', 'thewarehouse', 'freshchoice', 'supervalue']

var paths = []

for (var supermarketname of supermarket_foldernames) {
var files = fs.readdirSync(`${theRootThing}${supermarketname}`)
//fs.readdir(`${theRootThing}${supermarketname}`, (err, files) => {
  var fileNumToCheck = 6 //1 = the latest, 2 = the previous one, and so on
  files.splice(-fileNumToCheck)
  var previousCheckFile = files[files.length-1]
  var currentCheckFile = 'latest.json'
  paths.push({
  "shorthand": `${supermarketname} Earlier`,
  "path": `${theRootThing}${supermarketname}\\${previousCheckFile}`
})
paths.push({
  "shorthand": `${supermarketname} Now`,
  "path": `${theRootThing}${supermarketname}\\${currentCheckFile}`
})
//});
}

//console.log(paths)

/* var paths = [{
  "shorthand": "Paknsave Earlier",
  "path": `${theRootThing}paknsave\\1629521198.json`
}, {
  "shorthand": "Paknsave Now",
  "path": `${theRootThing}paknsave\\latest.json`
},
{
  "shorthand": "Countdown Earlier",
  "path": `${theRootThing}countdown\\1629255357.json`
}, {
  "shorthand": "Countdown Now",
  "path": `${theRootThing}countdown\\latest.json`
},
{
  "shorthand": "Mighty Ape Earlier",
  "path": `${theRootThing}mightyape\\1629255052.json`
}, {
  "shorthand": "Mighty Ape Now",
  "path": `${theRootThing}mightyape\\latest.json`
},
{
  "shorthand": "The Warehouse Earlier",
  "path": `${theRootThing}thewarehouse\\1629254810.json`
}, {
  "shorthand": "The Warehouse Now",
  "path": `${theRootThing}thewarehouse\\latest.json`
},
{
  "shorthand": "Fresh Choice Earlier",
  "path": `${theRootThing}freshchoice\\1629261586.json`
}, {
  "shorthand": "Fresh Choice Now",
  "path": `${theRootThing}freshchoice\\latest.json`
},
{
  "shorthand": "SuperValue Earlier",
  "path": `${theRootThing}supervalue\\1629264788.json`
}, {
  "shorthand": "SuperValue Now",
  "path": `${theRootThing}supervalue\\latest.json`
}] */
var rawData;
var jsonData = {};

var objectsPushed = {}

for (var path of paths) {
  rawdata = fs.readFileSync(path.path);
  var tempData = JSON.parse(rawdata)
  for (var key of tempData.slice(1)) {
    var objectToPush = {'fileMeta': path, 'entry': key}
    var uniqueObjectKey = key.store ? `${key.productData.productId}_${key.store.id}` : key.productData.productId
    if (jsonData[uniqueObjectKey]) {
      //console.log(`ADD ${uniqueObjectKey} (p)`)
      jsonData[uniqueObjectKey].push(objectToPush)
      objectsPushed[uniqueObjectKey].count+=1;
    } else {
      //console.log(`ADD ${uniqueObjectKey} (a)`)
      jsonData[uniqueObjectKey] = [objectToPush]
      objectsPushed[uniqueObjectKey] = {'count': 1}
    }
  }
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

// console.log(jsonData[Object.keys(jsonData)[1]])
//console.log(objectsPushed)

function percIncrease(a, b) {
  let percent;
  if(b !== 0) {
      if(a !== 0) {
          percent = (b - a) / a * 100;
      } else {
          percent = b * 100;
      }
  } else {
      percent = - a * 100;            
  }       
  return Math.floor(percent);
}

for (var objectKey of Object.keys(jsonData)) {
  // console.log(objectKey)
  var content_entry = jsonData[objectKey];
  //console.log(content_entry)
  // for (i=0;i<content_entry.length;i++) {
  //   var current = content_entry[i];
  //   console.log(`Price ${i+1}: ${current.entry.priceData.bestPrice}`)
  // }
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
      newArray.push({'name': prodName, 'previousPrice': price_a, 'currentPrice': price_b, 'percentageChange': percentageChange, 'store': `${storeName} - ${content_entry[0].fileMeta.shorthand}`, 'oldPricePerLitre': content_entry[0].entry.priceData.bestPricePerLitre, 'currentPricePerLitre': content_entry[1].entry.priceData.bestPricePerLitre})
    }
  }
  // 
  // if (price.priceData.bestPricePerLitre && (price.productData.name.toLowerCase()).includes('mother')) {
  // //var price = {'productData': {'name': price_old['productData']['name']}, 'priceData': price_old['priceData']}
  // var tempOb = price.priceData
  // tempOb['name'] = price.productData.name
  // tempOb['productShopPage'] = price.productData.productShopPage
  // if (price.store) {
  //   tempOb['store'] = price.store.name
  // }
  // newArray.push(tempOb)
  // }
}

// newArray.sort(compare);
// console.log('==============')
// console.log(newArray)
fs.writeFileSync('./data_changes/latest.json', JSON.stringify(newArray));
fs.writeFileSync(`./data_changes/${new Date().getTime()}.json`, JSON.stringify(newArray));