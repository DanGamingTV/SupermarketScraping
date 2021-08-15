import requests
from bs4 import BeautifulSoup as bs
import re

config = {'siteMeta': {'name': 'Mighty Ape', 'mainURL': 'www.mightyape.co.nz', 'productPrefix': ''}, 'regex': {'dollars': '(\d{1,})', 'cents': '(\d{2,})', 'multipackDetect': '(\d{1,}ml).{0,}\((\d{1,}).{0,}p.{0,}k\)'}, 'endpoints': {}}

def getProductPrice(productId):

    baseurl=f"https://{config['siteMeta']['mainURL']}/product/name/{productId}"
    header = {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest"
    }

    with requests.session() as s:
      r = s.get(baseurl)
      soup = bs(r.content,'html.parser')

      scrapedData = {}

      scrapedData['cents'] =  str(soup.find_all('span', {'class': "cents"}))
      dollars =  str(soup.find_all('span', {'class': "dollars"}))
      productName = soup.find_all('h1')
      productName = str(productName[0].contents[0]) if len(productName) > 0 else ''
      productDescription = soup.find_all('div', {'class': "product-description"})
      productDescription = str(productDescription[0].contents[0]) if len(productDescription) > 0 else ''
      productImageURL = soup.find_all('div', {'class': 'image-wrapper'})
      productImageURL = str(productImageURL[0].find('img')['src']) if len(productImageURL) > 0 else ''
      productFormat = soup.find_all('div', {'class': 'static'})
      productFormat = productFormat[0] if len(productFormat) > 0 else ''
      productFormat = productFormat.find('span').text.strip() if len(productFormat.find_all('span')) > 0 else ''
      productFormatMultipackDetect = re.findall("Pack of (\d{1,})", productFormat)
      centsprice =re.findall(config['regex']['cents'], scrapedData['cents'])
      dollarsprice = re.findall(config['regex']['dollars'], dollars)
      multipack_detect = re.findall(config['regex']['multipackDetect'], productName.lower())
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
        
      price = {'productData': {'name': productName, 'productId': productId, 'productShopPage': baseurl, 'productDescription': productDescription.strip(), 'productImageURL': productImageURL}, 'bestPrice': salePrice ,'price': salePrice}
      if (productFormatMultipackDetect):
          price['productData']['multipack'] = {'quantity': productFormatMultipackDetect[0]}
      if (multipack_detect):
          if ('multipack' not in price['productData']):
              price['productData']['multipack'] = {'quantity': list(multipack_detect[0])[1]}
          price['productData']['volume'] = list(multipack_detect[0])[0]
      elif (volume_detect):
          price['productData']['volume'] = volume_detect.groups()[1]
      if ('volume' in price['productData']):
          mutatedVolume = float(price['productData']['volume'].replace('ml', ''))
          actualVolume = float(mutatedVolume)
          if ('multipack' in price['productData']):
              actualVolume = mutatedVolume*int(price['productData']['multipack']['quantity'])
          calculatedPricePerLitre = float(price['price'])*(1000/actualVolume)
          calculatedBestPricePerLitre = float(price['bestPrice'])*(1000/actualVolume)
          price['pricePerLitre'] = calculatedPricePerLitre
          price['bestPricePerLitre'] = calculatedBestPricePerLitre
      return price