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
      try:
        s.get(baseurl)
      except ConnectionError:
          print("shit")
      s.get(url)
      #use the same session to return broccoli price
      r = s.get(baseurl)
      soup = bs(r.content,'html.parser')
      cents =  str(soup.find_all('span', {'class': "fs-price-lockup__cents"}))
      dollars =  str(soup.find_all('span', {'class': "fs-price-lockup__dollars"}))
      productName = soup.find_all('h1', {'class': "u-h4 u-color-dark-grey"})
      if (len(productName) > 0):
          productName = str(productName[0].contents[0])
      productImageURL = "https://a.fsimg.co.nz/product/retail/fan/image/master/" + productId.replace("_ea_000", "") + ".png"
      productDescription = soup.find_all('div', {'class': "fs-product-detail__description"})
      if (len(productDescription) > 0):
          productDescription = productDescription[0].text.strip()
      else:
          productDescription = ''
      volumeText = soup.find_all('div', {'class': 'fs-accordion__accesible-panel'})
      if (len(volumeText) > 0):
          volumeText = volumeText[1].find('p').text
          volumeData = list(re.findall("Serving.pack: (\d{1,}) Serving size: (.{1,})", volumeText)[0])
      else:
          volumeData = ['', '']
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
        
      price = {'productData': {'name': productName, 'productId': productId, 'productShopPage': 'https://www.paknsave.co.nz/shop/product/'+productId+productPrefix,'productImageURL': productImageURL, 'productDescription': productDescription, 'volume': volumeData[1], 'multipack': {'quantity': volumeData[0]}}, 'bestPrice': salePrice ,'price': salePrice}
      if (ppl > 0):
          price['pricePerLitre'] = ppl
          price['bestPricePerLitre'] = ppl
      internalProductId = productId.replace(productPrefix, '')
      if (pplValid == False):
          if ('volume' in price['productData']):
            if (len(price['productData']['volume'].lower().replace('ml', '')) > 0):
                mutatedVolume = float(price['productData']['volume'].lower().replace('ml', ''))
                actualVolume = float(mutatedVolume)
                if ('multipack' in price['productData']):
                    actualVolume = mutatedVolume*int(price['productData']['multipack']['quantity'])
                calculatedPricePerLitre = float(price['price'])*(1000/actualVolume)
                calculatedBestPricePerLitre = float(price['bestPrice'])*(1000/actualVolume)
                price['pricePerLitre'] = calculatedPricePerLitre
                price['bestPricePerLitre'] = calculatedBestPricePerLitre
                pplValid = True
      mbR = s.get(storeURL+"/CommonApi/PromoGroup/GetPromoGroup?productId="+productId)
      mbData = json.loads(mbR.content)
      if (mbData['success'] == True):
        multibuyQuantity = mbData['promoGroup']['multiBuyQuantity']
        multibuyPrice = mbData['promoGroup']['multiBuyPrice']
        if (multibuyQuantity > 1):
            price['multiBuy'] = {'quantity': multibuyQuantity, 'value': multibuyPrice, 'perUnit': multibuyPrice/multibuyQuantity}
            price['bestPrice'] = multibuyPrice/multibuyQuantity
            if (pplValid == True):
                price['bestPrice'] = float(price['bestPrice'])
                price['price'] = float(price['price'])
                price['pricePerLitre'] = float(price['pricePerLitre'])
                price['bestPricePerLitre'] = price['bestPrice'] / (price['price'] / price['pricePerLitre'])
      
      return price


# print(getProductPrice("5011153_ea_000pns?name=energy-drink-can", "3bb30799-82ce-4648-8c02-5113228963ed"))
#productsToCheck = ["5011153_ea_000"]
productsToCheck = ["5290181_ea_000", "5289891_ea_000", "5289890_ea_000", "5264576_ea_000", "5272987_ea_000", "5289889_ea_000", "5283362_ea_000", "5003156_ea_000", "5228254_ea_000", "5210055_ea_000", "5007492_ea_000", "5020662_ea_000", "5007494_ea_000", "5010699_ea_000", "5005255_ea_000", "5008928_ea_000pns", "5032368_ea_000", "5003151_ea_000", "5001443_ea_000", "5030250_ea_000", "5009239_ea_000", "5237753_ea_000", "5032373_ea_000", "5009240_ea_000", "5257298_ea_000", "5237735_ea_000", "5032374_ea_000", "5095698_ea_000", "5091377_ea_000", "5215383_ea_000", "5254654_ea_000", "5289907_ea_000", "5278542_ea_000", "5278541_ea_000", "5264523_ea_000", "5272988_ea_000", "5017493_ea_000", "5030249_ea_000", "5004117_ea_000", "5242374_ea_000", "5278094_ea_000", "5269459_ea_000", "5261257_ea_000", "5002893_ea_000", "5090618_ea_000", "5284331_ea_000", "5011153_ea_000", "5284332_ea_000", "5009490_ea_000", "5242373_ea_000", "5007647_ea_000", "5213974_ea_000", "5210130_ea_000", "5107264_ea_000", "5007644_ea_000", "5004703_ea_000", "5210048_ea_000", "5210061_ea_000", "5007441_ea_000", "5011173_ea_000"]
dataList = []
stores_stuff = getStores()

for a in productsToCheck:
    for x in stores_stuff:
        if ((x and ('id' in x))):   
          currentPrice = getProductPrice(a, x['id'])
          storeModified = {'id': x['id'], 'name': x['name'], 'address': x['address']}
          productData = currentPrice['productData']
          del currentPrice['productData']
          if (currentPrice['price'] != '0.00'):
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