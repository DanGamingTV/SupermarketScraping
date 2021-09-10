import requests
from bs4 import BeautifulSoup as bs
import re

config = {'siteMeta': {'name': 'The Warehouse', 'mainURL': 'www.thewarehouse.co.nz', 'productPrefix': ''}, 'regex': {'dollars': '>([0-9][0-9]?)', 'cents': '>([0-9][0-9])'}, 'endpoints': {}}

def getProductPrice(productId):

    baseurl=f"https://{config['siteMeta']['mainURL']}/p/product/{productId}.html"
    header = {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest"
    }

    with requests.session() as s:
      r = s.get(baseurl)
      soup = bs(r.content,'html.parser')

      scrapedData = {}

      scrapedData['cents'] =  str(soup.find_all('span', {'class': "now-price-fraction"}))
      dollars =  str(soup.find_all('span', {'class': "now-price-integer"}))
      productName = soup.find_all('h1', {'class': "h4 product-name"})
      productName = str(productName[0].contents[0]) if len(productName) > 0 else ''
      productDescription = soup.find_all('div', {'class': "long-description"})
      productDescription = str(productDescription[0].contents[0]) if len(productDescription) > 0 else ''
      productImageURL = soup.find_all('img', {'class': 'product-slider-image embed-responsive-item img-fluid'})
      productImageURL = str(productImageURL[0]['src']) if len(productImageURL) > 0 else ''
      centsprice =re.findall(config['regex']['cents'], scrapedData['cents'])
      dollarsprice = re.findall(config['regex']['dollars'], dollars)
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
        
      price = {'productData': {'name': productName, 'productId': productId, 'productShopPage': baseurl, 'productDescription': productDescription.strip(), 'productImageURL': productImageURL}, 'bestPrice': salePrice ,'price': salePrice}
      if (multipack_detect):
          price['productData']['multipack'] = {'quantity': multipack_detect.groups()[2]}
          price['productData']['volume'] = multipack_detect.groups()[1]
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
      

""" # print(getProductPrice("5011153_ea_000pns?name=energy-drink-can", "3bb30799-82ce-4648-8c02-5113228963ed"))
productsToCheck = ["R671608", "R671606", "R1907052", "R2613851", "R2628987", "R501186", "R2628988", "R2378859", "R2613850", "R2717468", "R2457276", "R2457274", "R1559892", "R2755897", "R1907053", "R501187", "R1559891", "R2720433", "R2720434", "R2494486", "R2381465", "R2137497", "R2607463", "R2494487", "R2538645", "R2381615", "R2229714", "R1648759", "R2607462", "R2391372", "R2426919", "R2481578", "R2456984", "R2456983", "R2560028", "R1573117", "R1539597", "R2739987", "R1573116", "R151415", "R500135", "R2226500", "R671491", "R2657178", "R1445715", "R671492", "R1233239", "R2739986", "R2657177", "R2391373", "R2457274", "R2197289", "R2457276"]
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
        json.dump(dataList, f, ensure_ascii=False, indent=4) """