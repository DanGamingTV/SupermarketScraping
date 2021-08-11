import requests
from bs4 import BeautifulSoup as bs
import re
import json
import time
import os.path

dollars_pattern = '>([0-9][0-9]?)'
cents_pattern = '>([0-9][0-9])'



def getProductPrice(productId):
    baseurl=f"https://shop.countdown.co.nz/api/v1/products/{productId}"
    header = {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
      "X-Requested-With": "OnlineShopping.WebApp"
    }

    with requests.session() as s:
      #I assume this url changes the store (200 response)
      s.get(baseurl)
      #use the same session to return broccoli price
      r = s.get(baseurl, headers=header)
      # print(r.content)
      data = json.loads(r.content)
      # print(data)
      price = {'productData': {'name': data['name'], 'productShopPage': "https://shop.countdown.co.nz/shop/productdetails?stockcode="+data['sku']},'bestPrice': data['price']['salePrice'] ,'price': data['price']['salePrice'], 'pricePerLitre': data['size']['cupPrice']*10, 'bestPricePerLitre': data['size']['cupPrice']*10}
      for x in data['productTags']:
        if(x['tagType'] == "IsGreatPriceMultiBuy"):
            price['multiBuy'] = {'quantity': x['multiBuy']['quantity'], 'value': x['multiBuy']['value'], 'perUnit': x['multiBuy']['value']/x['multiBuy']['quantity']}
            price['bestPrice'] = x['multiBuy']['value']/x['multiBuy']['quantity']
            price['bestPricePerLitre'] = price['bestPrice'] / (price['price'] / price['pricePerLitre'])
      if (data['size']['packageType'] != "single can"):
        matchMultipack = re.match("(\d{1,})pk", data['size']['volumeSize'])
        if(matchMultipack):
          price['productData']['multiPack'] = {'quantity': list(matchMultipack.groups())[0]}
          matchPackageType = re.match("(.{1,}ml) cans", data['size']['packageType'])
          if (matchPackageType):
            price['productData']['volume'] = list(matchPackageType.groups())[0]
      matchVolumeSize = re.match("(.{1,}ml)", data['size']['volumeSize'])
      if (matchVolumeSize != None):
        price['productData']['volume'] = list(matchVolumeSize.groups())[0]
      price['productData']['productId'] = data['sku']
      price['productData']['productDescription'] = data['description']
      productImageURL = data['images']
      if (len(productImageURL) > 0):
        productImageURL = productImageURL[0]['big']
      else:
        productImageURL = ''
      price['productData']['productImageURL'] = productImageURL
      matchVolumeFromProductName = re.findall(". (\d{1,}ml)", data['name'])
      if (len(matchVolumeFromProductName) > 0):
        price['productData']['volume'] = matchVolumeFromProductName[0]
      return price


# print(getProductPrice("5011153_ea_000pns?name=energy-drink-can", "3bb30799-82ce-4648-8c02-5113228963ed"))
# print(getProductPrice("315125"))

productsToCheck = ["315125", "764892", "361734", "329812", "315692", "139864", "384544", "132815", "117141"]
dataList = []

for a in productsToCheck:
      currentPrice = getProductPrice(a)
      productData = currentPrice['productData']
      del currentPrice['productData']
      dataList.append({'productData': productData, 'priceData': currentPrice})
      print(currentPrice)
if (os.path.isfile('./data/latest.json')):
    with open('./data/latest.json') as json_file:
        data = json.load(json_file)
        if (dataList == data):
            print("latest data saved is the same as the data just gathered. not going to write new file.")
        else:
            with open('./data/' + str(int(time.time())) + '.json', 'w', encoding='utf-8') as f:
                json.dump(dataList, f, ensure_ascii=False, indent=4)
            with open('./data/' + 'latest' + '.json', 'w', encoding='utf-8') as f:
                json.dump(dataList, f, ensure_ascii=False, indent=4)
else:
    with open('./data/' + str(int(time.time())) + '.json', 'w', encoding='utf-8') as f:
        json.dump(dataList, f, ensure_ascii=False, indent=4)
    with open('./data/' + 'latest' + '.json', 'w', encoding='utf-8') as f:
        json.dump(dataList, f, ensure_ascii=False, indent=4)