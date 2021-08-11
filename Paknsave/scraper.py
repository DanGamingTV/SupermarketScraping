import requests
from bs4 import BeautifulSoup as bs
import re
import json
import time
import os.path

storeURL = "https://www.paknsave.co.nz"
productPrefix = "pns"

dollars_pattern = '>([0-9][0-9]?)'
cents_pattern = '>([0-9][0-9])'

def getStoreIDs():
    storeIDs = []
    storeListEndpoint = storeURL+"/CommonApi/Store/GetStoreList"
    with requests.session() as s:
        r = s.get(storeListEndpoint)
        # print(r.content)
        stores = json.loads(r.content)['stores']
        # print(stores)
        for x in stores:
            storeIDs.append(x['id'])
        return storeIDs

def getStores():
    stores_list = []
    storeListEndpoint = storeURL+"/CommonApi/Store/GetStoreList"
    with requests.session() as s:
        r = s.get(storeListEndpoint)
        # print(r.content)
        stores = json.loads(r.content)['stores']
        # print(stores)
        for x in stores:
            stores_list.append(x)
        return stores_list


def getProductPrice(productId, storeId):

    url = f"{storeURL}/CommonApi/Store/ChangeStore?storeId={storeId}"
    baseurl=f"{storeURL}/shop/product/{productId}"
    header = {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest"
    }

    with requests.session() as s:
      #I assume this url changes the store (200 response)
      s.get(baseurl)
      s.get(url)
      #use the same session to return broccoli price
      r = s.get(baseurl)
      soup = bs(r.content,'html.parser')
      cents =  str(soup.find_all('span', {'class': "fs-price-lockup__cents"}))
      dollars =  str(soup.find_all('span', {'class': "fs-price-lockup__dollars"}))
      productName = str(soup.find_all('h1', {'class': "u-h4 u-color-dark-grey"})[0].contents[0])
      productImageURL = "https://a.fsimg.co.nz/product/retail/fan/image/master/" + productId.replace("ea_000", "") + ".png"
      productDescription = soup.find_all('div', {'class': "fs-product-detail__description"})[0].text.strip()
      ppl = soup.find_all('div', {'class': 'fs-product-card__price-by-weight'})
      pplValid = False
      if (len(ppl) > 0):
          ppl = str(ppl[0].contents[0]).replace('$', '')
          pplValid = True
          if (ppl.endswith(' per 100ml')):
            ppl = ppl.replace(' per 100ml', '')
            ppl = float(ppl)*10
          elif (ppl.endswith(' per 1l')):
            ppl = ppl.replace(' per 1l', '')
            ppl = float(ppl)
      else:
          ppl = 0
          pplValid = False
      centsprice =re.findall(cents_pattern, cents)
      dollarsprice = re.findall(dollars_pattern, dollars)
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
        
      price = {'productData': {'name': productName, 'productId': productId, 'productShopPage': 'https://www.paknsave.co.nz/shop/product/'+productId+productPrefix,'productImageURL': productImageURL, 'productDescription': productDescription}, 'bestPrice': salePrice ,'price': salePrice}
      if (ppl > 0):
          price['pricePerLitre'] = ppl
          price['bestPricePerLitre'] = ppl
      internalProductId = productId.replace(productPrefix, '')
      mbR = s.get(storeURL+"/CommonApi/PromoGroup/GetPromoGroup?productId="+productId)
      mbData = json.loads(mbR.content)
      if (mbData['success'] == True):
        multibuyQuantity = mbData['promoGroup']['multiBuyQuantity']
        multibuyPrice = mbData['promoGroup']['multiBuyPrice']
        if (multibuyQuantity > 1):
            price['multiBuy'] = {'quantity': multibuyQuantity, 'value': multibuyPrice, 'perUnit': multibuyPrice/multibuyQuantity}
            price['bestPrice'] = multibuyPrice/multibuyQuantity
            if (pplValid == True):
                price['bestPricePerLitre'] = price['bestPrice'] / (price['price'] / price['pricePerLitre'])
      
      return price


# print(getProductPrice("5011153_ea_000pns?name=energy-drink-can", "3bb30799-82ce-4648-8c02-5113228963ed"))
#productsToCheck = ["5011153_ea_000"]
productsToCheck = ["5011153_ea_000", "5009490_ea_000", "5007647_ea_000", "5107264_ea_000", "5004703_ea_000", "5210048_ea_000", "5210061_ea_000", "5007441_ea_000", "5011173_ea_000"]
dataList = []
stores_stuff = getStores()

for a in productsToCheck:
    for x in stores_stuff:
        currentPrice = getProductPrice(a, x['id'])
        storeModified = {'id': x['id'], 'name': x['name'], 'address': x['address']}
        productData = currentPrice['productData']
        del currentPrice['productData']
        dataList.append({'productData': productData, 'priceData': currentPrice, 'store': storeModified})
        print(currentPrice, x['name'])
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