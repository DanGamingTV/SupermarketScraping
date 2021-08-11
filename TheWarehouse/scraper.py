import requests
from bs4 import BeautifulSoup as bs
import re
import json
import time
import os.path

storeURL = "https://www.thewarehouse.co.nz"
productPrefix = ""

dollars_pattern = '>([0-9][0-9]?)'
cents_pattern = '>([0-9][0-9])'

def getProductPrice(productId):

    baseurl=f"{storeURL}/p/product/{productId}.html"
    header = {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest"
    }

    with requests.session() as s:
      r = s.get(baseurl)
      soup = bs(r.content,'html.parser')
      cents =  str(soup.find_all('span', {'class': "now-price-fraction"}))
      dollars =  str(soup.find_all('span', {'class': "now-price-integer"}))
      productName = str(soup.find_all('h1', {'class': "h4 product-name"})[0].contents[0])
      centsprice =re.findall(cents_pattern, cents)
      dollarsprice = re.findall(dollars_pattern, dollars)
      multipack_detect = re.match("(.{1,})(\d{3,}ml).(\d{1,}) Pack", productName)
      volume_detect = re.match("(.{1,})(\d{3,}ml)", productName)
      if (len(dollarsprice) > 0):
          if (len(centsprice) > 0):
              salePrice = f"{dollarsprice[0]}.{centsprice[0]}"
              # return price
          else:
            salePrice = f"{dollarsprice[0]}.00"
            # return price
      else:
          if (len(centsprice) > 0):
              salePrice = f"0.{centsprice[0]}"
              # return price
          else:
            salePrice = "0.00"
        
      price = {'productData': {'name': productName}, 'bestPrice': salePrice ,'price': salePrice}
      if (multipack_detect):
          price['productData']['multipack'] = {'quantity': multipack_detect.groups()[2]}
          price['productData']['volume'] = multipack_detect.groups()[1]
      elif (volume_detect):
          price['productData']['volume'] = volume_detect.groups()[1]
      return price
      

# print(getProductPrice("5011153_ea_000pns?name=energy-drink-can", "3bb30799-82ce-4648-8c02-5113228963ed"))
productsToCheck = ["R2229714", "R2229714", "R1648759", "R2607462", "R2391372", "R2426919", "R2481578", "R2456984", "R2456983", "R2560028", "R1573117", "R1539597", "R2739987", "R1573116", "R151415", "R500135", "R2226500", "R671491", "R2657178", "R1445715", "R671492", "R1233239", "R2739986", "R2657177", "R2391373", "R2457274", "R2197289", "R2457276"]
dataList = []

for a in productsToCheck:
      currentPrice = getProductPrice(a)
      productData = currentPrice['productData']
      del currentPrice['productData']
      dataList.append({'productData': productData, 'priceData': currentPrice})
      print({'productData': productData, 'priceData': currentPrice})

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