import requests
from bs4 import BeautifulSoup as bs
import re
import json

config = {'siteMeta': {'name': 'Paknsave', 'mainURL': 'https://www.paknsave.co.nz', 'productPrefix': 'pns'}, 'regex': {'dollars': '>([0-9][0-9]?)', 'cents': '>([0-9][0-9])', 'volumeData': "Serving.pack: (\d{1,}) Serving size: (.{1,})"}}

state = {}
state["currentStoreId"] = ""

def getStoreIDs():
    storeIDs = []
    with requests.session() as s:
        r = s.get(f"{config['siteMeta']['mainURL']}/CommonApi/Store/GetStoreList")
        stores = json.loads(r.content)['stores']
        for x in stores:
            storeIDs.append(x['id'])
        return storeIDs

def getStores():
    stores_list = []
    with requests.session() as s:
        r = s.get(f"{config['siteMeta']['mainURL']}/CommonApi/Store/GetStoreList")
        stores = json.loads(r.content)['stores']
        for x in stores:
            stores_list.append(x)
        return stores_list

def getProductPrice(productId, storeId):
    productId = productId.replace(config['siteMeta']['productPrefix'], '') if productId.endswith(config['siteMeta']['productPrefix']) else productId # If productId has a prefix added to it, remove it.
    url = f"{config['siteMeta']['mainURL']}/CommonApi/Store/ChangeStore?storeId={storeId}" # URL to change store
    baseurl=f"{config['siteMeta']['mainURL']}/shop/product/{productId}"
    with requests.session() as s:
      try:
        s.get(baseurl)
      except ConnectionError:
          print("shit")
      s.get(url)
      state["currentStoreId"] = storeId

      r = s.get(baseurl)
      if ('Sorry, this item is unavailable in your chosen store' in r.text):
          return {'productData': {'name': '', 'productId': '', 'productShopPage': '','productImageURL': '', 'productDescription': ''}, 'bestPrice': '0.00' ,'price': '0.00'}
      soup = bs(r.content,'html.parser')

      scrapedData = {}
      scrapedData['cents'] =  str(soup.find_all('span', {'class': "fs-price-lockup__cents"}))
      scrapedData['dollars'] =  str(soup.find_all('span', {'class': "fs-price-lockup__dollars"}))
      scrapedData['productName'] = soup.find_all('h1', {'class': "u-h4 u-color-dark-grey"})
      if (len(scrapedData['productName']) > 0):
          scrapedData['productName'] = str(scrapedData['productName'][0].contents[0])
      scrapedData['productImageURL'] = "https://a.fsimg.co.nz/product/retail/fan/image/master/" + productId.replace("_ea_000", "") + ".png"
      scrapedData['productDescription'] = soup.find_all('div', {'class': "fs-product-detail__description"})
      if (len(scrapedData['productDescription']) > 0):
          scrapedData['productDescription'] = scrapedData['productDescription'][0].text.strip()
      else:
          scrapedData['productDescription'] = ''
      scrapedData['volumeText'] = soup.find_all('div', {'class': 'fs-accordion__accesible-panel'})
      if (len(scrapedData['volumeText']) > 0):
          scrapedData['volumeText'] = scrapedData['volumeText'][1].find('p').text
          scrapedData['volumeData'] = list(re.findall(config['regex']['volumeData'], scrapedData['volumeText'])[0])
      else:
          scrapedData['volumeData'] = ['', '']
      scrapedData['ppl'] = soup.find_all('div', {'class': 'fs-product-card__price-by-weight'})
      scrapedData['pplValid'] = False
      if (len(scrapedData['ppl']) > 0):
          scrapedData['ppl'] = str(scrapedData['ppl'][0].contents[0]).replace('$', '')
          scrapedData['pplValid'] = True
          if (scrapedData['ppl'].endswith(' per 100ml')):
            scrapedData['ppl'] = scrapedData['ppl'].replace(' per 100ml', '')
            scrapedData['ppl'] = float(scrapedData['ppl'])*10
          elif (scrapedData['ppl'].endswith(' per 1l')):
            scrapedData['ppl'] = scrapedData['ppl'].replace(' per 1l', '')
            scrapedData['ppl'] = float(scrapedData['ppl'])
      else:
          scrapedData['ppl'] = 0
          scrapedData['pplValid'] = False
      centsprice =re.findall(config['regex']['cents'], scrapedData['cents'])
      dollarsprice = re.findall(config['regex']['dollars'], scrapedData['dollars'])
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
        
      price = {'productData': {'name': scrapedData['productName'], 'productId': productId, 'productShopPage': config['siteMeta']['mainURL']+'/shop/product/'+productId+config['siteMeta']['productPrefix'],'productImageURL': scrapedData['productImageURL'], 'productDescription': scrapedData['productDescription'], 'volume': scrapedData['volumeData'][1], 'multipack': {'quantity': scrapedData['volumeData'][0]}}, 'bestPrice': salePrice ,'price': salePrice}
      if (scrapedData['ppl'] > 0):
          price['pricePerLitre'] = scrapedData['ppl']
          price['bestPricePerLitre'] = scrapedData['ppl']
      if (scrapedData['pplValid'] == False):
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
                scrapedData['pplValid'] = True
      if (('pricePerLitre' in price) and ('multipack' in price['productData'])):
          if (price['pricePerLitre'] > 16 and price['productData']['multipack']['quantity'] != ''):
              # assume that foodstuffs messed up with their provided unit pricing, fix it ourselves
              price['pricePerLitre'] = price['pricePerLitre']/int(price['productData']['multipack']['quantity'])
              price['bestPricePerLitre'] = price['bestPricePerLitre']/int(price['productData']['multipack']['quantity'])
    try:
        mbR = s.get(config['siteMeta']['mainURL']+"/CommonApi/PromoGroup/GetPromoGroup?productId="+productId)
        try:
            mbData = json.loads(mbR.content)
            if (mbData['success'] == True):
                multibuyQuantity = mbData['promoGroup']['multiBuyQuantity']
                multibuyPrice = mbData['promoGroup']['multiBuyPrice']
                if (multibuyQuantity > 1):
                    price['multiBuy'] = {'quantity': multibuyQuantity, 'value': multibuyPrice, 'perUnit': multibuyPrice/multibuyQuantity}
                    price['bestPrice'] = multibuyPrice/multibuyQuantity
                    if (scrapedData['pplValid'] == True):
                        price['bestPrice'] = float(price['bestPrice'])
                        price['price'] = float(price['price'])
                        price['pricePerLitre'] = float(price['pricePerLitre'])
                        price['bestPricePerLitre'] = price['bestPrice'] / (price['price'] / price['pricePerLitre'])
        except json.decoder.JSONDecodeError:
            print("welp, error decoding json oof")
    except ConnectionError:
        print("shit")
    if (price['bestPricePerLitre'] > 30):
      # assume that their data is messed up (most likely they are 10x more than actual)
      price['bestPricePerLitre'] = price['bestPricePerLitre']/10
      price['pricePerLitre'] = price['pricePerLitre']/10
    return price