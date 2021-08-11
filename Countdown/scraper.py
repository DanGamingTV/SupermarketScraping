import requests
from bs4 import BeautifulSoup as bs
import re
import json
import time

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
      price = {'name': data['name'],'bestPrice': data['price']['salePrice'] ,'price': data['price']['salePrice'], 'pricePerLitre': data['size']['cupPrice']*10, 'bestPricePerLitre': data['size']['cupPrice']*10}
      for x in data['productTags']:
        if(x['tagType'] == "IsGreatPriceMultiBuy"):
            price['multiBuy'] = {'quantity': x['multiBuy']['quantity'], 'value': x['multiBuy']['value'], 'perUnit': x['multiBuy']['value']/x['multiBuy']['quantity']}
            price['bestPrice'] = x['multiBuy']['value']/x['multiBuy']['quantity']
            price['bestPricePerLitre'] = price['bestPrice'] / (price['price'] / price['pricePerLitre'])
      
      return price


# print(getProductPrice("5011153_ea_000pns?name=energy-drink-can", "3bb30799-82ce-4648-8c02-5113228963ed"))
# print(getProductPrice("315125"))

productsToCheck = ["315125", "764892", "361734", "329812", "315692", "139864", "384544", "132815", "117141"]
dataList = []

for a in productsToCheck:
      currentPrice = getProductPrice(a)
      dataList.append({'priceData': currentPrice})
      print(currentPrice)
with open('./data/' + str(int(time.time())) + '.json', 'w', encoding='utf-8') as f:
    json.dump(dataList, f, ensure_ascii=False, indent=4)
with open('./data/' + 'latest' + '.json', 'w', encoding='utf-8') as f:
    json.dump(dataList, f, ensure_ascii=False, indent=4)