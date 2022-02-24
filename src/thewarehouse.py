import requests
from bs4 import BeautifulSoup as bs
import re
import asyncio

config = {'siteMeta': {'name': 'The Warehouse', 'mainURL': 'www.thewarehouse.co.nz', 'productPrefix': ''},
          'regex': {'dollars': '>([0-9][0-9]?)', 'cents': '>([0-9][0-9])'}, 'endpoints': {}}


async def getProductPrice(productId):
    baseurl = f"https://{config['siteMeta']['mainURL']}/p/product/{productId}.html"
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    with requests.session() as s:
        r = s.get(baseurl)
        soup = bs(r.content, 'html.parser')

        scrapedData = {}

        scrapedData['cents'] = str(soup.find_all(
            'span', {'class': "now-price-fraction"}))
        dollars = str(soup.find_all('span', {'class': "now-price-integer"}))
        productName = soup.find_all('h1', {'class': "h4 product-name"})
        productName = str(productName[0].contents[0]) if len(
            productName) > 0 else ''
        productDescription = soup.find_all(
            'div', {'class': "long-description"})
        productDescription = str(productDescription[0].contents[0]) if len(
            productDescription) > 0 else ''
        productImageURL = soup.find_all(
            'img', {'class': 'product-slider-image embed-responsive-item img-fluid'})
        productImageURL = str(productImageURL[0]['src']) if len(
            productImageURL) > 0 else ''
        centsprice = re.findall(config['regex']['cents'], scrapedData['cents'])
        dollarsprice = re.findall(config['regex']['dollars'], dollars)
        multipack_detect = re.match(
            "(.{1,})(\d{3,}ml).(\d{1,}) Pack", productName)
        volume_detect = re.match("(.{1,})(\d{3,}ml)", productName)
        volume_litre_detect = re.match("(.{1,})(\d{1,}\s{0,}[L-l])", productName)
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

        price = {'productData': {'name': productName, 'productId': productId, 'productShopPage': baseurl,
                                 'productDescription': productDescription.strip(), 'productImageURL': productImageURL}, 'bestPrice': salePrice, 'price': salePrice}
        if (multipack_detect):
            price['productData']['multipack'] = {
                'quantity': multipack_detect.groups()[2]}
            price['productData']['volume'] = multipack_detect.groups()[1]
        elif (volume_detect):
            price['productData']['volume'] = volume_detect.groups()[1]
            mutatedVolume = float(
                price['productData']['volume'].replace('ml', ''))
            actualVolume = float(mutatedVolume)
            price['productData']['volume'] = actualVolume
        elif (volume_litre_detect):
            mutatedVolume = volume_litre_detect.groups()[1]
            mutatedVolume = mutatedVolume.replace('L', '')
            mutatedVolume = mutatedVolume.replace('l', '')
            actualVolume = float(mutatedVolume)*1000
            price['productData']['volume'] = actualVolume
        if ('volume' in price['productData']):
            if ('multipack' in price['productData']):
                actualVolume = mutatedVolume * \
                    int(price['productData']['multipack']['quantity'])
            calculatedPricePerLitre = float(price['price'])*(1000/actualVolume)
            calculatedBestPricePerLitre = float(
                price['bestPrice'])*(1000/actualVolume)
            price['pricePerLitre'] = calculatedPricePerLitre
            price['bestPricePerLitre'] = calculatedBestPricePerLitre
        return price
